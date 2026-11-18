import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { reportsApi } from '../api';
import { InterviewReport } from '../types';
import { RadarChart } from '../components/RadarChart';
import {
  Award,
  Download,
  CheckCircle2,
  AlertTriangle,
  BookOpen,
  Calendar,
  Sparkles,
  ArrowLeft,
  FileCheck,
  AlertCircle
} from 'lucide-react';

export const InterviewReportView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [report, setReport] = useState<InterviewReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (id) {
      fetchReport(id);
    }
  }, [id]);

  const fetchReport = async (interviewId: string) => {
    try {
      setLoading(true);
      setError('');
      const res = await reportsApi.getReport(interviewId);
      setReport(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Report could not be retrieved. Ensure interview was completed.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!id) return;
    try {
      const res = await reportsApi.downloadPdf(id);
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `SmartHire_Report_${report?.candidate_name || 'Interview'}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Failed to download PDF report', err);
    }
  };

  const radarData = report
    ? [
        { label: 'Technical Accuracy', value: report.technical_score },
        { label: 'Communication', value: report.communication_score },
        { label: 'Overall Score', value: report.overall_score },
      ]
    : [];

  return (
    <div className="space-y-8 pb-12">
      <div className="flex items-center space-x-3">
        <Link
          to="/reports"
          className="p-2 bg-slate-900 border border-slate-800 rounded-xl text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
        </Link>
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight">Interview Evaluation Report</h1>
          <p className="text-xs text-slate-400 mt-1">
            Comprehensive diagnostic feedback, rubric dimension radar, and question transcript analysis.
          </p>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-xs text-red-400 flex items-start space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="h-64 bg-slate-900 border border-slate-800 rounded-2xl flex items-center justify-center">
          <div className="flex flex-col items-center space-y-3">
            <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-xs text-slate-400">Compiling Evaluation Matrix & PDF...</p>
          </div>
        </div>
      ) : report ? (
        <div className="space-y-8">
          {/* Header Action Banner */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider">Candidate:</span>
                <h2 className="text-xl font-bold text-white">{report.candidate_name}</h2>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Target Role: <strong className="text-slate-200">{report.target_role}</strong> &bull; Interview Date: {report.interview_date}
              </p>
            </div>

            <button
              onClick={handleDownloadPdf}
              className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold flex items-center space-x-2 shadow-lg shadow-indigo-600/20 transition-all self-start md:self-auto"
            >
              <Download className="w-4 h-4" />
              <span>Download Official PDF Report</span>
            </button>
          </div>

          {/* Metric Cards & Radar Chart */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Dimensions Grid */}
            <div className="lg:col-span-1 space-y-3">
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 text-center bg-gradient-to-br from-indigo-950/40 to-slate-900">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Composite Overall Score</span>
                <p className="text-4xl font-black text-emerald-400 mt-1">{report.overall_score}%</p>
                <span className="text-[10px] text-slate-500 mt-1 inline-block">Weighted Performance Metric</span>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5">
                  <span className="text-[10px] font-semibold text-slate-500 uppercase">Technical Accuracy</span>
                  <p className="text-xl font-black text-emerald-400 mt-0.5">{report.technical_score}%</p>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5">
                  <span className="text-[10px] font-semibold text-slate-500 uppercase">Communication & Clarity</span>
                  <p className="text-xl font-black text-indigo-400 mt-0.5">{report.communication_score}%</p>
                </div>
              </div>
            </div>

            {/* Radar Chart */}
            <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col items-center justify-center">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider self-start mb-2 flex items-center">
                <Sparkles className="w-4 h-4 mr-1.5 text-indigo-400" />
                Performance Dimension Radar
              </h3>
              <RadarChart data={radarData} size={280} color="#10b981" fillColor="rgba(16, 185, 129, 0.25)" />
            </div>
          </div>

          {/* Executive Summary */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-3">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center">
              <FileCheck className="w-4 h-4 mr-1.5 text-indigo-400" />
              Executive Evaluation Summary
            </h3>
            <p className="text-xs text-slate-200 leading-relaxed bg-slate-950 p-4 rounded-xl border border-slate-800/80">
              {report.summary}
            </p>
          </div>

          {/* Strengths & Growth Areas */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-3">
              <h3 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center">
                <CheckCircle2 className="w-4 h-4 mr-1.5" />
                Key Demonstrated Strengths
              </h3>
              <ul className="space-y-2 text-xs text-slate-300">
                {report.strengths.map((str, idx) => (
                  <li key={idx} className="flex items-start">
                    <span className="text-emerald-400 mr-2 font-bold">&bull;</span>
                    <span>{str}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-3">
              <h3 className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center">
                <AlertTriangle className="w-4 h-4 mr-1.5" />
                Critical Areas for Improvement
              </h3>
              <ul className="space-y-2 text-xs text-slate-300">
                {report.weaknesses.map((w, idx) => (
                  <li key={idx} className="flex items-start">
                    <span className="text-amber-400 mr-2 font-bold">&bull;</span>
                    <span>{w}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Revision Topics */}
          {report.revision_topics?.length > 0 && (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-3">
              <h3 className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center">
                <BookOpen className="w-4 h-4 mr-1.5" />
                Recommended Topics to Revise Before Live Industry Rounds
              </h3>
              <div className="flex flex-wrap gap-2">
                {report.revision_topics.map((t, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-semibold"
                  >
                    {t}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Question by Question Review */}
          <div className="space-y-4">
            <h3 className="text-base font-bold text-white tracking-tight">Question & Answer Detailed Breakdown</h3>
            <div className="space-y-4">
              {report.qa_records?.map((record, idx) => (
                <div key={idx} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                      Question {record.sequence_order} &bull; {record.category}
                    </span>
                    <span className="text-xs font-extrabold text-emerald-400">
                      {record.technical_accuracy}% Technical Score
                    </span>
                  </div>

                  <h4 className="font-semibold text-sm text-white">"{record.question_text}"</h4>

                  <div className="p-3.5 bg-slate-950 rounded-xl border border-slate-800/80 space-y-1">
                    <span className="text-[11px] font-semibold text-slate-400">Candidate Answer:</span>
                    <p className="text-xs text-slate-300 italic leading-relaxed">"{record.candidate_answer}"</p>
                  </div>

                  <p className="text-xs text-emerald-400 bg-emerald-500/5 p-3 rounded-xl border border-emerald-500/20">
                    <strong>AI Feedback:</strong> {record.feedback}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
