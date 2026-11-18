import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { interviewApi } from '../api';
import { InterviewSession } from '../types';
import { Award, Calendar, ChevronRight, Mic, Sparkles, AlertCircle } from 'lucide-react';

export const InterviewHistory: React.FC = () => {
  const [interviews, setInterviews] = useState<InterviewSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const res = await interviewApi.getHistory();
      setInterviews(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load interview history.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 pb-12">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight">Interview History & Performance Reports</h1>
          <p className="text-xs text-slate-400 mt-1">
            Review past mock interview sessions, historical score trends, and access downloadable PDF evaluation reports.
          </p>
        </div>
        <Link
          to="/interview"
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold flex items-center space-x-2 shadow-md shadow-indigo-600/20"
        >
          <Mic className="w-3.5 h-3.5" />
          <span>New Interview</span>
        </Link>
      </div>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-xs text-red-400 flex items-start space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-24 bg-slate-900 border border-slate-800 rounded-2xl animate-pulse"></div>
          ))}
        </div>
      ) : interviews.length === 0 ? (
        <div className="p-12 text-center text-slate-500 border border-dashed border-slate-800 rounded-2xl bg-slate-900/40">
          <Award className="w-12 h-12 mx-auto text-slate-600 mb-3" />
          <p className="text-sm font-semibold text-slate-300">No mock interviews completed yet.</p>
          <p className="text-xs text-slate-500 mt-1">Start your first live mock interview to receive detailed feedback.</p>
          <Link
            to="/interview"
            className="mt-4 inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-xl text-xs font-semibold"
          >
            Launch Mock Interview
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {interviews.map((inv) => (
            <div
              key={inv.id}
              className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:border-slate-700 transition-all"
            >
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <h3 className="font-bold text-sm text-white">{inv.role_title || 'Software Engineer'}</h3>
                  <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-medium border border-slate-700/60">
                    {inv.language}
                  </span>
                  <span className="text-[10px] bg-indigo-500/10 text-indigo-400 px-2 py-0.5 rounded border border-indigo-500/20 font-medium">
                    {inv.interview_type}
                  </span>
                </div>
                <div className="flex items-center space-x-3 text-xs text-slate-500">
                  <span className="flex items-center">
                    <Calendar className="w-3.5 h-3.5 mr-1" />
                    {new Date(inv.started_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                  </span>
                  <span>&bull;</span>
                  <span>{inv.questions_count} Questions Answered</span>
                </div>
              </div>

              <div className="flex items-center space-x-4 self-end sm:self-center">
                <div className="text-right">
                  <span className="text-[10px] text-slate-500 uppercase font-semibold">Overall Score</span>
                  <p className="text-lg font-black text-emerald-400">
                    {inv.overall_score ? `${inv.overall_score}%` : 'In Progress'}
                  </p>
                </div>

                <Link
                  to={`/interview/${inv.id}/report`}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition-colors"
                >
                  <span>View Report</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
