import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { skillsApi } from '../api';
import { RoadmapItem } from '../types';
import {
  CalendarCheck,
  CheckCircle2,
  Clock,
  BookOpen,
  ExternalLink,
  ChevronRight,
  Sparkles,
  AlertCircle,
  PlayCircle
} from 'lucide-react';

export const LearningRoadmap: React.FC = () => {
  const location = useLocation();
  const roleId = location.state?.roleId;

  const [roadmap, setRoadmap] = useState<RoadmapItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchRoadmap();
  }, [roleId]);

  const fetchRoadmap = async () => {
    try {
      setLoading(true);
      setError('');
      const res = await skillsApi.getRoadmap(roleId);
      setRoadmap(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load roadmap.');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (itemId: string, newStatus: 'not_started' | 'in_progress' | 'completed') => {
    try {
      setUpdatingId(itemId);
      const res = await skillsApi.updateRoadmapItem(itemId, newStatus);
      setRoadmap((prev) =>
        prev.map((item) => (item.id === itemId ? res.data : item))
      );
    } catch (err) {
      console.error('Failed to update roadmap item status', err);
    } finally {
      setUpdatingId(null);
    }
  };

  const completedCount = roadmap.filter((r) => r.status === 'completed').length;
  const progressPercent = roadmap.length > 0 ? Math.round((completedCount / roadmap.length) * 100) : 0;

  return (
    <div className="space-y-8 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight">Personalized Learning Roadmap</h1>
          <p className="text-xs text-slate-400 mt-1">
            Topologically sequenced curriculum closing your career skill gaps with curated resources and verified milestone tracking.
          </p>
        </div>

        {/* Progress Bar Badge */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 min-w-[220px]">
          <div className="flex justify-between items-center text-xs mb-1.5">
            <span className="font-semibold text-slate-400">Curriculum Progress</span>
            <span className="font-extrabold text-indigo-400">{progressPercent}%</span>
          </div>
          <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
            <div
              className="bg-indigo-500 h-full rounded-full transition-all duration-500"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
          <p className="text-[10px] text-slate-500 mt-1.5 text-right">
            {completedCount} of {roadmap.length} weeks finished
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
        <div className="space-y-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 h-40 animate-pulse"></div>
          ))}
        </div>
      ) : roadmap.length === 0 ? (
        <div className="p-12 text-center text-slate-500 border border-dashed border-slate-800 rounded-2xl bg-slate-900/40">
          <CalendarCheck className="w-12 h-12 mx-auto text-slate-600 mb-3" />
          <p className="text-sm font-semibold text-slate-300">No active learning roadmap found.</p>
          <p className="text-xs text-slate-500 mt-1">
            Run a Skill Gap Analysis to generate your customized step-by-step roadmap.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {roadmap.map((item) => {
            const isCompleted = item.status === 'completed';
            const isInProgress = item.status === 'in_progress';

            return (
              <div
                key={item.id}
                className={`border rounded-2xl p-6 transition-all ${
                  isCompleted
                    ? 'bg-slate-900/40 border-emerald-500/30'
                    : isInProgress
                    ? 'bg-slate-900 border-indigo-500/40 shadow-lg shadow-indigo-600/5'
                    : 'bg-slate-900 border-slate-800'
                }`}
              >
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-bold px-2.5 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                        WEEK {item.week_number}
                      </span>
                      <h3 className="font-bold text-base text-white">{item.phase_title}</h3>
                    </div>

                    <p className="text-xs text-slate-300 font-medium flex items-center">
                      <span className="text-slate-500 mr-2">Target Skill:</span>
                      <span className="px-2.5 py-0.5 rounded-md bg-slate-800 text-indigo-300 text-xs font-semibold">
                        {item.skill_name}
                      </span>
                      <span className="ml-4 text-slate-500 flex items-center text-xs">
                        <Clock className="w-3.5 h-3.5 mr-1" />
                        Est. {item.estimated_hours} Hours
                      </span>
                    </p>
                  </div>

                  {/* Status Action Buttons */}
                  <div className="flex items-center space-x-1.5 self-start md:self-auto bg-slate-950 p-1.5 rounded-xl border border-slate-800 shrink-0">
                    <button
                      onClick={() => handleStatusChange(item.id, 'not_started')}
                      disabled={updatingId === item.id}
                      className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                        item.status === 'not_started'
                          ? 'bg-slate-800 text-slate-200'
                          : 'text-slate-500 hover:text-slate-300'
                      }`}
                    >
                      Not Started
                    </button>
                    <button
                      onClick={() => handleStatusChange(item.id, 'in_progress')}
                      disabled={updatingId === item.id}
                      className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                        item.status === 'in_progress'
                          ? 'bg-indigo-600 text-white shadow-sm'
                          : 'text-slate-500 hover:text-slate-300'
                      }`}
                    >
                      In Progress
                    </button>
                    <button
                      onClick={() => handleStatusChange(item.id, 'completed')}
                      disabled={updatingId === item.id}
                      className={`px-3 py-1 rounded-lg text-xs font-medium transition-all flex items-center space-x-1 ${
                        isCompleted
                          ? 'bg-emerald-600 text-white shadow-sm'
                          : 'text-slate-500 hover:text-slate-300'
                      }`}
                    >
                      <CheckCircle2 className="w-3 h-3" />
                      <span>Completed</span>
                    </button>
                  </div>
                </div>

                {/* Curated Resources */}
                {item.learning_resources?.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-800/80 space-y-2">
                    <span className="text-[11px] font-semibold text-slate-400 flex items-center">
                      <BookOpen className="w-3 h-3 mr-1.5 text-indigo-400" />
                      Curated Study Materials & Hands-on Labs:
                    </span>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {item.learning_resources.map((res, idx) => (
                        <a
                          key={idx}
                          href={res.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center justify-between p-2.5 bg-slate-950/60 rounded-xl border border-slate-800/80 hover:border-indigo-500/30 text-xs text-slate-200 hover:text-indigo-300 transition-colors group"
                        >
                          <span className="truncate pr-2 font-medium">{res.title}</span>
                          <span className="text-[10px] text-slate-500 group-hover:text-indigo-400 shrink-0 flex items-center">
                            {res.type}
                            <ExternalLink className="w-3 h-3 ml-1" />
                          </span>
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
