import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { interviewApi, rolesApi } from '../api';
import { Question, AnswerEvaluation, RoleOut } from '../types';
import { AudioRecorder } from '../components/AudioRecorder';
import {
  Mic,
  MessageSquare,
  Volume2,
  VolumeX,
  Play,
  CheckCircle2,
  AlertCircle,
  Clock,
  Sparkles,
  ArrowRight,
  TrendingUp,
  FileCheck,
  Languages
} from 'lucide-react';

export const MockInterview: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [roles, setRoles] = useState<RoleOut[]>([]);
  const [selectedRoleId, setSelectedRoleId] = useState<string>('');
  const [language, setLanguage] = useState<string>(user?.language_preference || 'English');
  const [interviewType, setInterviewType] = useState<string>('comprehensive');

  // Active Session State
  const [interviewId, setInterviewId] = useState<string | null>(null);
  const [roleTitle, setRoleTitle] = useState<string>('');
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [latestEvaluation, setLatestEvaluation] = useState<AnswerEvaluation | null>(null);
  
  // Input State
  const [textAnswer, setTextAnswer] = useState('');
  const [inputMode, setInputMode] = useState<'voice' | 'text'>('voice');
  const [loading, setLoading] = useState(false);
  const [evaluating, setEvaluating] = useState(false);
  const [latency, setLatency] = useState<number | null>(null);
  const [error, setError] = useState('');
  const [isCompleted, setIsCompleted] = useState(false);

  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    loadRoles();
  }, []);

  const loadRoles = async () => {
    try {
      const res = await rolesApi.getRoles();
      setRoles(res.data);
      if (res.data.length > 0) {
        setSelectedRoleId(res.data[0].id);
      }
    } catch (e) {
      console.error('Failed to load roles for interview', e);
    }
  };

  const handleStartInterview = async () => {
    try {
      setLoading(true);
      setError('');
      setLatestEvaluation(null);
      setIsCompleted(false);

      const res = await interviewApi.startInterview({
        role_id: selectedRoleId || undefined,
        language: language,
        interview_type: interviewType,
      });

      setInterviewId(res.data.interview_id);
      setRoleTitle(res.data.role_title);
      setCurrentQuestion(res.data.question);

      // Play synthesized audio if present
      if (res.data.question.audio_base64) {
        playBase64Audio(res.data.question.audio_base64);
      } else {
        // Fallback browser speech synthesis
        speakBrowser(res.data.question.question_text, language);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start interview. Ensure resume is uploaded.');
    } finally {
      setLoading(false);
    }
  };

  const playBase64Audio = (b64: string) => {
    try {
      const snd = new Audio(`data:audio/mp3;base64,${b64}`);
      snd.play().catch((e) => console.log('Autoplay policy caught, click to play:', e));
    } catch (e) {
      console.error('Audio playback error', e);
    }
  };

  const speakBrowser = (text: string, lang: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      if (lang.toLowerCase() === 'hindi') {
        utterance.lang = 'hi-IN';
      } else {
        utterance.lang = 'en-US';
      }
      utterance.rate = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  };

  const handleTextSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!textAnswer.trim() || !interviewId) return;

    const startTime = performance.now();
    setEvaluating(true);
    setError('');

    try {
      const res = await interviewApi.submitAnswer(interviewId, {
        candidate_answer: textAnswer,
        latency_seconds: 1.1,
      });

      const elapsedSec = (performance.now() - startTime) / 1000;
      setLatency(parseFloat(elapsedSec.toFixed(2)));
      handleAnswerProcessed(res.data);
      setTextAnswer('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to evaluate answer.');
    } finally {
      setEvaluating(false);
    }
  };

  const handleVoiceCaptured = async (audioBlob: Blob, liveTranscript?: string) => {
    if (!interviewId) return;
    const startTime = performance.now();
    setEvaluating(true);
    setError('');

    const formData = new FormData();
    formData.append('audio', audioBlob, 'candidate_answer.webm');
    if (liveTranscript && liveTranscript.trim()) {
      formData.append('live_transcript', liveTranscript.trim());
    }

    try {
      const res = await interviewApi.submitVoiceAnswer(interviewId, formData);
      const elapsedSec = (performance.now() - startTime) / 1000;
      setLatency(parseFloat(elapsedSec.toFixed(2)));
      handleAnswerProcessed(res.data.evaluation);
    } catch (err: any) {
      const detail = err.response?.data?.detail || '';
      // If no speech was detected, show a clear message — don't silently fallback
      if (err.response?.status === 422 || detail.includes('No speech')) {
        setError(detail || 'No speech detected. Please speak clearly or switch to text input.');
      } else if (liveTranscript) {
        // Fallback: If voice endpoint fails for other reasons, submit live transcript text
        try {
          const fallbackRes = await interviewApi.submitAnswer(interviewId, {
            candidate_answer: liveTranscript,
            latency_seconds: 1.2,
          });
          handleAnswerProcessed(fallbackRes.data);
        } catch (e) {
          setError('Failed to process voice response.');
        }
      } else {
        setError('Voice processing error. Please try typing your response.');
      }
    } finally {
      setEvaluating(false);
    }
  };

  const handleAnswerProcessed = (evaluation: AnswerEvaluation) => {
    setLatestEvaluation(evaluation);

    if (evaluation.next_question) {
      setCurrentQuestion(evaluation.next_question);
      if (evaluation.next_question.audio_base64) {
        playBase64Audio(evaluation.next_question.audio_base64);
      } else {
        speakBrowser(evaluation.next_question.question_text, language);
      }
    } else {
      // All questions completed!
      setIsCompleted(true);
    }
  };

  const handleCompleteInterview = async () => {
    if (!interviewId) return;
    try {
      setLoading(true);
      await interviewApi.completeInterview(interviewId);
      navigate(`/interview/${interviewId}/report`);
    } catch (err) {
      console.error('Error completing interview', err);
      navigate(`/interview/${interviewId}/report`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 pb-12">
      <div>
        <h1 className="text-2xl font-black text-white tracking-tight">AI Mock Interview Room</h1>
        <p className="text-xs text-slate-400 mt-1">
          Dynamic contextual interview questions generated from your resume, skill gaps, and live responses. Supports English, Hindi, and Hinglish.
        </p>
      </div>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-xs text-red-400 flex items-start space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* Setup Step (when no active interview) */}
      {!interviewId ? (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 md:p-8 space-y-6 max-w-2xl mx-auto shadow-xl">
          <div className="flex items-center space-x-3 pb-4 border-b border-slate-800">
            <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <Mic className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Configure Interview Simulation</h2>
              <p className="text-xs text-slate-400">Choose your target position, language dialect, and interview style.</p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Target Career Role</label>
              <select
                value={selectedRoleId}
                onChange={(e) => setSelectedRoleId(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                {roles.map((r) => (
                  <option key={r.id} value={r.id} className="bg-slate-900 text-white">
                    {r.title} ({r.category})
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Interview Language</label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="English">English</option>
                  <option value="Hindi">Hindi (हिंदी)</option>
                  <option value="Hinglish">Hinglish (Code-Switching)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Interview Focus</label>
                <select
                  value={interviewType}
                  onChange={(e) => setInterviewType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="comprehensive">Comprehensive (Technical + Behavioral)</option>
                  <option value="technical">Pure Technical & System Architecture</option>
                  <option value="behavioral">Behavioral & Situational</option>
                </select>
              </div>
            </div>

            <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 text-xs text-slate-400 space-y-1">
              <span className="font-semibold text-slate-200 flex items-center">
                <Sparkles className="w-3.5 h-3.5 mr-1 text-indigo-400" />
                Conversational AI Features:
              </span>
              <p>&bull; Dynamic follow-up questions adapted to answer accuracy.</p>
              <p>&bull; Understands colloquial technical Hinglish effortlessly.</p>
              <p>&bull; Sub-1.8 second turn evaluation latency benchmarking.</p>
            </div>

            <button
              onClick={handleStartInterview}
              disabled={loading}
              className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold shadow-lg shadow-indigo-600/30 flex items-center justify-center space-x-2 transition-all mt-4"
            >
              {loading ? (
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
              ) : (
                <>
                  <Mic className="w-4 h-4" />
                  <span>Enter Interview Room</span>
                </>
              )}
            </button>
          </div>
        </div>
      ) : (
        /* Active Interview Room Interface */
        <div className="space-y-6">
          {/* Header Status Bar */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 rounded-full bg-red-500 animate-ping"></div>
              <div>
                <span className="text-xs font-bold text-white uppercase tracking-wider">
                  Live Mock Interview &bull; {roleTitle}
                </span>
                <span className="ml-2 text-[10px] bg-indigo-500/10 text-indigo-400 px-2 py-0.5 rounded border border-indigo-500/20">
                  {language}
                </span>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              {latency !== null && (
                <div className="text-xs text-slate-400 bg-slate-950 px-3 py-1 rounded-lg border border-slate-800 flex items-center">
                  <Clock className="w-3.5 h-3.5 mr-1 text-emerald-400" />
                  AI Latency: <strong className="text-emerald-400 ml-1">{latency}s</strong> (Target &le; 1.8s)
                </div>
              )}

              <button
                onClick={handleCompleteInterview}
                className="px-4 py-1.5 bg-slate-800 hover:bg-red-500/20 hover:text-red-400 text-slate-300 rounded-xl text-xs font-semibold border border-slate-700 transition-colors"
              >
                End & View Report
              </button>
            </div>
          </div>

          {/* AI Question Prompt Card */}
          {currentQuestion && (
            <div className="bg-gradient-to-br from-indigo-950/40 via-slate-900 to-slate-900 border border-indigo-900/60 rounded-2xl p-6 md:p-8 space-y-4 shadow-xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-extrabold border border-indigo-500/30">
                    Question {currentQuestion.sequence_order} of 4
                  </span>
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    {currentQuestion.category} &bull; {currentQuestion.difficulty}
                  </span>
                </div>

                <button
                  onClick={() => {
                    if (currentQuestion.audio_base64) {
                      playBase64Audio(currentQuestion.audio_base64);
                    } else {
                      speakBrowser(currentQuestion.question_text, language);
                    }
                  }}
                  className="p-2 text-indigo-400 hover:bg-indigo-500/10 rounded-lg transition-colors flex items-center space-x-1 text-xs font-semibold"
                >
                  <Volume2 className="w-4 h-4" />
                  <span>Replay Audio</span>
                </button>
              </div>

              <h2 className="text-lg md:text-xl font-bold text-white leading-relaxed">
                "{currentQuestion.question_text}"
              </h2>

              {currentQuestion.expected_concepts?.length > 0 && (
                <div className="flex flex-wrap items-center gap-1.5 pt-2">
                  <span className="text-[11px] font-semibold text-slate-500 mr-1">Expected Concepts:</span>
                  {currentQuestion.expected_concepts.map((c, idx) => (
                    <span key={idx} className="text-[10px] bg-slate-800/80 text-slate-400 border border-slate-700/60 px-2 py-0.5 rounded">
                      {c}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Candidate Response Input Area */}
          {!isCompleted ? (
            <div className="space-y-4">
              {/* Input Mode Toggle */}
              <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
                <button
                  type="button"
                  onClick={() => setInputMode('voice')}
                  className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center space-x-2 transition-all ${
                    inputMode === 'voice'
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
                      : 'text-slate-400 hover:text-slate-200 bg-slate-900'
                  }`}
                >
                  <Mic className="w-3.5 h-3.5" />
                  <span>Voice Microphone</span>
                </button>
                <button
                  type="button"
                  onClick={() => setInputMode('text')}
                  className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center space-x-2 transition-all ${
                    inputMode === 'text'
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
                      : 'text-slate-400 hover:text-slate-200 bg-slate-900'
                  }`}
                >
                  <MessageSquare className="w-3.5 h-3.5" />
                  <span>Text Fallback</span>
                </button>
              </div>

              {inputMode === 'voice' ? (
                <AudioRecorder
                  onAudioCaptured={handleVoiceCaptured}
                  isProcessing={evaluating}
                  language={language}
                />
              ) : (
                <form onSubmit={handleTextSubmit} className="space-y-3">
                  <textarea
                    rows={4}
                    value={textAnswer}
                    onChange={(e) => setTextAnswer(e.target.value)}
                    placeholder={
                      language.toLowerCase() === 'hinglish'
                        ? 'Aap apna answer Hinglish me type kar sakte hain (e.g. "Main REST APIs use karta hoon...")...'
                        : 'Type your detailed technical explanation here...'
                    }
                    className="w-full bg-slate-900 border border-slate-800 rounded-2xl p-4 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500 transition-colors leading-relaxed"
                  />
                  <div className="flex justify-end">
                    <button
                      type="submit"
                      disabled={evaluating || !textAnswer.trim()}
                      className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl text-xs font-semibold flex items-center space-x-2 shadow-lg shadow-indigo-600/20 transition-all"
                    >
                      {evaluating ? (
                        <>
                          <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                          <span>AI Evaluating...</span>
                        </>
                      ) : (
                        <>
                          <span>Submit Answer</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </>
                      )}
                    </button>
                  </div>
                </form>
              )}
            </div>
          ) : (
            <div className="p-8 bg-emerald-950/20 border border-emerald-500/30 rounded-2xl text-center space-y-4">
              <div className="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-white">Interview Simulation Finished!</h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                Your answers across technical accuracy, problem solving, and articulation have been evaluated into a comprehensive report.
              </p>
              <button
                onClick={handleCompleteInterview}
                className="px-6 py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold shadow-lg shadow-emerald-600/20 transition-all inline-flex items-center space-x-2"
              >
                <span>View Final Evaluation Report</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          )}

          {/* Real-Time Answer Evaluation Feedback Card */}
          {latestEvaluation && (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center">
                  <Sparkles className="w-4 h-4 mr-1.5" />
                  Turn Evaluation & Multi-Dimensional Grading
                </span>
                <span className="text-xs text-slate-500">
                  {latestEvaluation.is_follow_up ? 'Follow-up question queued' : 'Interview complete'}
                </span>
              </div>

              {/* Objective Evaluation Scores */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="bg-slate-950 p-3 rounded-xl border border-slate-800/80">
                  <span className="text-[10px] font-semibold text-slate-500 uppercase">Technical Accuracy</span>
                  <p className="text-lg font-black text-emerald-400 mt-0.5">{latestEvaluation.technical_accuracy}%</p>
                </div>
                <div className="bg-slate-950 p-3 rounded-xl border border-slate-800/80">
                  <span className="text-[10px] font-semibold text-slate-500 uppercase">Communication & Clarity</span>
                  <p className="text-lg font-black text-indigo-400 mt-0.5">{latestEvaluation.communication_score}%</p>
                </div>
                <div className="bg-slate-950 p-3 rounded-xl border border-slate-800/80">
                  <span className="text-[10px] font-semibold text-slate-500 uppercase">Concept Coverage</span>
                  <p className="text-lg font-black text-purple-400 mt-0.5">{latestEvaluation.completeness_score}%</p>
                </div>
              </div>

              {/* Feedback Text */}
              <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
                <strong className="text-indigo-400">Interviewer Assessment:</strong> {latestEvaluation.feedback}
              </p>

              {/* Strengths & Weaknesses */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                {latestEvaluation.strengths?.length > 0 && (
                  <div className="p-3 bg-emerald-500/5 border border-emerald-500/20 rounded-xl space-y-1">
                    <span className="font-semibold text-emerald-400 flex items-center">
                      <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Demonstrated Strengths:
                    </span>
                    <ul className="list-disc list-inside text-slate-300 space-y-0.5">
                      {latestEvaluation.strengths.map((s, i) => (
                        <li key={i}>{s}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {latestEvaluation.weaknesses?.length > 0 && (
                  <div className="p-3 bg-amber-500/5 border border-amber-500/20 rounded-xl space-y-1">
                    <span className="font-semibold text-amber-400 flex items-center">
                      <TrendingUp className="w-3.5 h-3.5 mr-1" /> Suggestions to Polish:
                    </span>
                    <ul className="list-disc list-inside text-slate-300 space-y-0.5">
                      {latestEvaluation.weaknesses.map((w, i) => (
                        <li key={i}>{w}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
