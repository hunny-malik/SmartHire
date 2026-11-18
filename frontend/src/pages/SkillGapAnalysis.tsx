import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { skillsApi, rolesApi } from '../api';
import { SkillGapAnalysis as SkillGapType, RoleOut } from '../types';
import { RadarChart } from '../components/RadarChart';
import { PrerequisiteGraph } from '../components/PrerequisiteGraph';
import {
  GitMerge,
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  Clock,
  BookOpen,
  ExternalLink,
  Sparkles,
  Layers,
  AlertCircle
} from 'lucide-react';

export const SkillGapAnalysis: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const initialRoleId = location.state?.roleId;

  const [roles, setRoles] = useState<RoleOut[]>([]);
  const [selectedRoleId, setSelectedRoleId] = useState<string>(initialRoleId || '');
  const [gapData, setGapData] = useState<SkillGapType | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadRoles();
  }, []);

  useEffect(() => {
    if (selectedRoleId) {
      analyzeRole(selectedRoleId);
    }
  }, [selectedRoleId]);

  const loadRoles = async () => {
    try {
      const res = await rolesApi.getRoles();
      setRoles(res.data);
      if (!selectedRoleId && res.data.length > 0) {
        setSelectedRoleId(res.data[0].id);
      }
    } catch (err) {
      console.error('Failed to load roles:', err);
    }
  };

  const analyzeRole = async (roleId: string) => {
    try {
      setLoading(true);
      setError('');
      const res = await skillsApi.analyzeGap(roleId);
      setGapData(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to analyze skill gap.');
    } finally {
      setLoading(false);
    }
  };

  // Prepare data points for RadarChart
  const radarData = gapData
    ? [
        { label: 'Match Ratio', value: gapData.match_percentage },
        { label: 'Core Foundations', value: Math.min(100, Math.round(gapData.match_percentage * 1.1)) },
        { label: 'Architecture', value: gapData.gap_percentage < 30 ? 85 : 55 },
        { label: 'Domain Tools', value: Math.min(100, Math.round(gapData.matching_skills.length * 15)) },
        { label: 'Prerequisites', value: Math.max(40, 100 - gapData.missing_skills.length * 10) },
      ]
    : [];

  return (
    <div className="space-y-8 pb-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight">ESCO / O*NET Skill Gap Analysis</h1>
          <p className="text-xs text-slate-400 mt-1">
            Ontology-driven competency mapping identifying missing skills, DAG prerequisites, and topological learning sequence.
          </p>
        </div>

        {/* Role Selector Dropdown */}
        <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 rounded-xl px-3 py-1.5 self-start">
          <span className="text-xs text-slate-400 font-medium">Target Role:</span>
          <select
            value={selectedRoleId}
            onChange={(e) => setSelectedRoleId(e.target.value)}
            className="bg-transparent text-xs font-semibold text-white focus:outline-none cursor-pointer"
          >
            {roles.map((r) => (
              <option key={r.id} value={r.id} className="bg-slate-900 text-white">
                {r.title}
              </option>
            ))}
          </select>
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
            <p className="text-xs text-slate-400 font-medium">Constructing Skill Dependency DAG...</p>
          </div>
        </div>
      ) : gapData ? (
        <div className="space-y-8">
          {/* Top Overview: Match Stats & Radar Visualization */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Match & Gap Percentage Cards */}
            <div className="lg:col-span-1 space-y-4">
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Role Match Score</span>
                  <span className="text-xs font-bold text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
                    {gapData.match_percentage}% Aligned
                  </span>
                </div>
                <div>
                  <div className="flex justify-between text-xs text-slate-300 font-medium mb-1">
                    <span>Acquired Skills</span>
                    <span>{gapData.match_percentage}%</span>
                  </div>
                  <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                    <div className="bg-emerald-500 h-full rounded-full transition-all duration-500" style={{ width: `${gapData.match_percentage}%` }}></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-xs text-slate-300 font-medium mb-1">
                    <span>Skill Gap</span>
                    <span>{gapData.gap_percentage}%</span>
                  </div>
                  <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                    <div className="bg-red-500 h-full rounded-full transition-all duration-500" style={{ width: `${gapData.gap_percentage}%` }}></div>
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-800 text-xs text-slate-400 leading-relaxed">
                  Target: <strong className="text-white">{gapData.role_title}</strong>. Complete the prioritized roadmap below to close technical prerequisites.
                </div>

                <button
                  onClick={() => navigate('/roadmap', { state: { roleId: gapData.role_id } })}
                  className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold flex items-center justify-center space-x-2 shadow-lg shadow-indigo-600/20 transition-all"
                >
                  <span>View Step-by-Step Roadmap</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Acquired Skills Preview */}
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-3">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center">
                  <CheckCircle2 className="w-3.5 h-3.5 mr-1.5 text-emerald-400" />
                  Matching Competencies ({gapData.matching_skills.length})
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {gapData.matching_skills.map((m) => (
                    <span key={m.name} className="px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs font-medium">
                      {m.name}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Radar Chart Visualizer */}
            <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col items-center justify-center">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider self-start mb-2 flex items-center">
                <Sparkles className="w-4 h-4 mr-1.5 text-indigo-400" />
                Multi-Dimensional Competency Radar
              </h3>
              <RadarChart data={radarData} size={300} color="#6366f1" fillColor="rgba(99, 102, 241, 0.25)" />
            </div>
          </div>

          {/* Prerequisite DAG Graph */}
          <div className="space-y-4">
            <h3 className="text-base font-bold text-white tracking-tight flex items-center">
              <GitMerge className="w-5 h-5 mr-2 text-indigo-400" />
              Prerequisite Dependency Ontology
            </h3>
            <PrerequisiteGraph
              dag={gapData.prerequisite_dag}
              transitionPath={gapData.career_transition_path}
            />
          </div>

          {/* Missing Skills Prioritized Cards */}
          <div className="space-y-4">
            <h3 className="text-base font-bold text-white tracking-tight flex items-center">
              <Layers className="w-5 h-5 mr-2 text-red-400" />
              Prioritized Skill Gaps & Recommended Learning Resources
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {gapData.missing_skills.map((item) => {
                const isCritical = item.priority === 'critical';
                return (
                  <div
                    key={item.name}
                    className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-3 hover:border-slate-700 transition-all"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-bold text-sm text-white">{item.name}</h4>
                        <span className="text-[10px] text-slate-500">Required Level: {item.required_level}</span>
                      </div>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${
                          isCritical
                            ? 'bg-red-500/10 text-red-400 border-red-500/30'
                            : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                        }`}
                      >
                        {item.priority} Priority
                      </span>
                    </div>

                    {item.prerequisites.length > 0 && (
                      <div className="text-xs text-slate-400">
                        <span className="text-slate-500">Prerequisites:</span>{' '}
                        <span className="text-indigo-300 font-medium">{item.prerequisites.join(', ')}</span>
                      </div>
                    )}

                    <div className="space-y-1.5 pt-2 border-t border-slate-800/80">
                      <span className="text-[11px] font-semibold text-slate-400 flex items-center">
                        <BookOpen className="w-3 h-3 mr-1 text-indigo-400" /> Curated Learning Resources:
                      </span>
                      {item.recommended_resources.map((res, rIdx) => (
                        <a
                          key={rIdx}
                          href={res.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center justify-between text-xs text-slate-300 hover:text-indigo-400 bg-slate-950/60 p-2 rounded-lg border border-slate-800 hover:border-indigo-500/30 transition-colors"
                        >
                          <span className="truncate pr-2">{res.title}</span>
                          <span className="text-[10px] text-slate-500 shrink-0 flex items-center">
                            {res.type} &bull; {res.est_hours}h
                            <ExternalLink className="w-3 h-3 ml-1" />
                          </span>
                        </a>
                      ))}
                    </div>

                    <div className="text-[11px] text-slate-500 flex items-center justify-end">
                      <Clock className="w-3 h-3 mr-1" />
                      Estimated time: {item.estimated_learning_hours} hours
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
