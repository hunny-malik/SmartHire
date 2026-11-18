import React, { useState, useRef, useEffect } from 'react';
import { Mic, Square, Play, Volume2, AlertCircle, RefreshCw } from 'lucide-react';

interface AudioRecorderProps {
  onAudioCaptured: (audioBlob: Blob, liveTranscript?: string) => void;
  isProcessing?: boolean;
  language?: string; // English, Hindi, Hinglish
}

export const AudioRecorder: React.FC<AudioRecorderProps> = ({
  onAudioCaptured,
  isProcessing = false,
  language = 'English',
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const [liveTranscript, setLiveTranscript] = useState('');
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [capturedBlob, setCapturedBlob] = useState<Blob | null>(null);
  const [micError, setMicError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const timerRef = useRef<any>(null);
  const recognitionRef = useRef<any>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {}
      }
    };
  }, []);

  const startRecording = async () => {
    setMicError(null);
    setAudioUrl(null);
    setCapturedBlob(null);
    setLiveTranscript('');
    audioChunksRef.current = [];

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
        setCapturedBlob(audioBlob);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingSeconds(0);

      timerRef.current = setInterval(() => {
        setRecordingSeconds((prev) => prev + 1);
      }, 1000);

      // Initialize Web Speech Recognition for live speech transcription feedback
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognitionRef.current = recognition;
        recognition.continuous = true;
        recognition.interimResults = true;
        
        // Language locale for Hindi / Hinglish vs English
        if (language.toLowerCase() === 'hindi') {
          recognition.lang = 'hi-IN';
        } else {
          recognition.lang = 'en-US';
        }

        recognition.onresult = (event: any) => {
          let fullTranscript = '';
          for (let i = 0; i < event.results.length; ++i) {
            fullTranscript += event.results[i][0].transcript + ' ';
          }
          setLiveTranscript(fullTranscript.trim());
        };

        recognition.onerror = (e: any) => {
          console.warn('Speech recognition notice:', e.error);
        };

        try {
          recognition.start();
        } catch (e) {}
      }
    } catch (err: any) {
      console.error('Error accessing microphone:', err);
      setMicError('Microphone permission denied or device not found. You can still type your answers using text input.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerRef.current) clearInterval(timerRef.current);
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {}
      }
    }
  };

  const handleSubmitRecordedAudio = () => {
    if (capturedBlob) {
      onAudioCaptured(capturedBlob, liveTranscript);
    }
  };

  const formatTime = (secs: number) => {
    const mins = Math.floor(secs / 60);
    const remaining = secs % 60;
    return `${mins}:${remaining < 10 ? '0' : ''}${remaining}`;
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Volume2 className="w-4 h-4 text-indigo-400" />
          <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
            Bilingual Voice Engine ({language})
          </span>
        </div>
        {isRecording && (
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-ping"></span>
            <span className="text-xs font-bold text-red-400">REC {formatTime(recordingSeconds)}</span>
          </div>
        )}
      </div>

      {micError ? (
        <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl text-xs text-amber-300 flex items-start space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{micError}</span>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-4 space-y-4">
          {/* Waveform indicator */}
          <div className="h-10 flex items-center justify-center space-x-1 w-full max-w-xs">
            {Array.from({ length: 24 }).map((_, i) => (
              <div
                key={i}
                className={`w-1 rounded-full transition-all duration-150 ${
                  isRecording
                    ? 'bg-indigo-500 animate-pulse'
                    : 'bg-slate-800 h-2'
                }`}
                style={{
                  height: isRecording ? `${Math.max(10, Math.sin((i + recordingSeconds * 5) * 0.5) * 36 + 10)}px` : '6px',
                }}
              />
            ))}
          </div>

          {/* Controls */}
          <div className="flex items-center space-x-4">
            {!isRecording ? (
              <button
                type="button"
                onClick={startRecording}
                disabled={isProcessing}
                className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl font-medium text-xs flex items-center space-x-2 shadow-lg shadow-indigo-600/20 transition-all"
              >
                <Mic className="w-4 h-4" />
                <span>Start Speaking</span>
              </button>
            ) : (
              <button
                type="button"
                onClick={stopRecording}
                className="px-5 py-2.5 bg-red-600 hover:bg-red-500 text-white rounded-xl font-medium text-xs flex items-center space-x-2 shadow-lg shadow-red-600/20 animate-pulse transition-all"
              >
                <Square className="w-4 h-4" />
                <span>Stop Recording</span>
              </button>
            )}

            {capturedBlob && !isRecording && (
              <button
                type="button"
                onClick={handleSubmitRecordedAudio}
                disabled={isProcessing}
                className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded-xl font-medium text-xs flex items-center space-x-2 shadow-lg shadow-emerald-600/20 transition-all"
              >
                {isProcessing ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Evaluating...</span>
                  </>
                ) : (
                  <>
                    <span>Submit Voice Answer</span>
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      )}

      {/* Live transcript or recorded audio playback */}
      {(liveTranscript || audioUrl) && (
        <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-xl space-y-2">
          {audioUrl && (
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <span className="text-[11px] font-semibold text-slate-400">Audio Preview:</span>
              <audio controls src={audioUrl} className="h-7 w-56 max-w-full" />
            </div>
          )}
          {liveTranscript && (
            <div>
              <span className="text-[11px] font-semibold text-slate-400">Live Transcript:</span>
              <p className="text-xs text-slate-200 mt-1 italic">"{liveTranscript}"</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
