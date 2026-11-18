import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { rolesApi } from '../api';
import { RoleRecommendation } from '../types';
import { Briefcase, ArrowRight, CheckCircle2, XCircle, Sparkles, AlertCircle } from 'lucide-react';

export const RoleRecommendations: React.FC = () => {
  const [roles, setRoles] = useState<RoleRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      const res = await rolesApi.getRecommendations();
      setRoles(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load role recommendations. Ensure resume is uploaded.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectRole = (roleId: string) => {
    navigate('/skills', { state: { roleId } });
  };

  return (
    <div className="space-y-8 pb-12">
      <div>
        <h1 className="text-2xl font-black text-white tracking-tight">AI Role Recommendations</h1>
        <p className="text-xs text-slate-400 mt-1">
          Semantic matching between your extracted candidate profile embedding and standardized career competency profiles.
        </p>
      </div>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-xs text-red-400 flex items-start space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 h-56 animate-pulse"></div>
          ))}
        </div>
      ) : roles.length === 0 ? (
        <div className="p-12 text-center text-slate-500 border border-dashed border-slate-800 rounded-2xl bg-slate-900/40">
          <Briefcase className="w-12 h-12 mx-auto text-slate-600 mb-3" />
          <p className="text-sm font-semibold text-slate-300">No profile recommendations available.</p>
          <p className="text-xs text-slate-500 mt-1">Please upload your resume to generate customized role matches.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {roles.map((role) => (
            <div
              key={role.role_id}
              className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between space-y-4 hover:border-slate-700 transition-all shadow-sm"
            >
              <div>
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-bold text-lg text-white">{role.role_title}</h3>
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-indigo-400">
                      {role.category}
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-black px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                      {role.match_percentage}% Fit
                    </span>
                  </div>
                </div>

                <p className="text-xs text-slate-300 mt-3 leading-relaxed bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
                  <span className="font-semibold text-indigo-400">Match Rationale:</span> {role.reason}
                </p>

                {/* Matching Skills */}
                <div className="mt-4 space-y-2">
                  <div className="flex items-center text-xs font-semibold text-emerald-400 space-x-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Matching Skills ({role.matching_skills.length})</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {role.matching_skills.slice(0, 6).map((skill) => (
                      <span key={skill} className="text-[11px] bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 px-2.5 py-0.5 rounded-md font-medium">
                        {skill}
                      </span>
                    ))}
                    {role.matching_skills.length > 6 && (
                      <span className="text-[10px] text-slate-500 self-center">
                        +{role.matching_skills.length - 6} more
                      </span>
                    )}
                  </div>
                </div>

                {/* Missing Skills Gap */}
                {role.missing_skills.length > 0 && (
                  <div className="mt-3 space-y-2">
                    <div className="flex items-center text-xs font-semibold text-red-400 space-x-1.5">
                      <XCircle className="w-3.5 h-3.5" />
                      <span>Skill Gaps Identified ({role.missing_skills.length})</span>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {role.missing_skills.slice(0, 5).map((skill) => (
                        <span key={skill} className="text-[11px] bg-red-500/10 text-red-400 border border-red-500/20 px-2.5 py-0.5 rounded-md font-medium">
                          {skill}
                        </span>
                      ))}
                      {role.missing_skills.length > 5 && (
                        <span className="text-[10px] text-slate-500 self-center">
                          +{role.missing_skills.length - 5} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>

              <div className="pt-2 border-t border-slate-800 flex justify-end">
                <button
                  onClick={() => handleSelectRole(role.role_id)}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold flex items-center space-x-2 shadow-md shadow-indigo-600/20 transition-all"
                >
                  <span>Analyze Skill Gap & Roadmap</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
