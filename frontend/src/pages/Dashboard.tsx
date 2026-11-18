import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import {
  resumeApi,
  rolesApi,
  jobsApi,
  skillsApi,
  interviewApi
} from '../api';
import { CandidateProfile, RoleRecommendation, JobMatch, RoadmapItem, InterviewSession } from '../types';
import {
  FileText,
  Briefcase,
  Search,
  GitMerge,
  CalendarCheck,
  Mic,
  ArrowRight,
  TrendingUp,
  CheckCircle2,
  Clock,
  Sparkles,
  ExternalLink,
  ChevronRight
} from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [profile, setProfile] = useState<CandidateProfile | null>(null);
  const [roles, setRoles] = useState<RoleRecommendation[]>([]);
  const [jobs, setJobs] = useState<JobMatch[]>([]);
  const [roadmap, setRoadmap] = useState<RoadmapItem[]>([]);
  const [interviews, setInterviews] = useState<InterviewSession[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        // Profile
        try {
          const profRes = await resumeApi.getProfile();
          setProfile(profRes.data);
          
          // If profile exists, load recommendations
          const [rolesRes, jobsRes, roadmapRes, interviewRes] = await Promise.all([
            rolesApi.getRecommendations().catch(() => ({ data: [] })),
            jobsApi.getRecommendations({ limit: 4 }).catch(() => ({ data: [] })),
            skillsApi.getRoadmap().catch(() => ({ data: [] })),
            interviewApi.getHistory().catch(() => ({ data: [] })),
          ]);

          setRoles(rolesRes.data);
          setJobs(jobsRes.data);
          setRoadmap(roadmapRes.data);
          setInterviews(interviewRes.data);
        } catch (e) {
          // No profile uploaded yet
          console.info('No candidate profile found yet.');
        }
      } catch (err) {
        console.error('Error loading dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Compute profile completeness
  const completeness = profile
    ? Math.min(100, [
        Boolean(profile.full_name),
        Boolean(profile.email),
        Boolean(profile.skills?.length > 0),
        Boolean(profile.experience?.length > 0),
        Boolean(profile.education?.length > 0),
        Boolean(profile.projects?.length > 0)
      ].filter(Boolean).length * 16.7)
    : 0;

  // Roadmap progress
  const completedWeeks = roadmap.filter((r) => r.status === 'completed').length;
  const roadmapProgress = roadmap.length > 0 ? Math.round((completedWeeks / roadmap.length) * 100) : 0;

  // Latest interview
  const latestInterview = interviews[0];

  return (
    <div className="space-y-8 pb-12">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-indigo-950 via-slate-900 to-slate-900 border border-indigo-900/40 p-6 md:p-8">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-semibold mb-3">
              <Sparkles className="w-3.5 h-3.5" />
              <span>AI Career Copilot Active</span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              Welcome back, {user?.full_name?.split(' ')[0] || 'Candidate'}!
            </h1>
            <p className="text-slate-400 text-sm mt-1 max-w-xl">
              Target Role: <strong className="text-slate-200">{user?.target_role || 'Software Engineer'}</strong>. Track your resume score, match rankings, and practice bilingual mock interviews.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Link
              to="/interview"
              className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-semibold text-xs flex items-center space-x-2 shadow-lg shadow-indigo-600/30 transition-all"
            >
              <Mic className="w-4 h-4" />
              <span>Start Mock Interview</span>
            </Link>
            <Link
              to="/resume"
              className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl font-semibold text-xs border border-slate-700 transition-all flex items-center space-x-2"
            >
              <FileText className="w-4 h-4" />
              <span>Upload Resume</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Profile Completeness Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Profile Completeness</span>
            <FileText className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="my-3">
            <span className="text-3xl font-black text-white">{Math.round(completeness)}%</span>
            <div className="w-full bg-slate-800 h-2 rounded-full mt-2 overflow-hidden">
              <div
                className="bg-indigo-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${completeness}%` }}
              />
            </div>
          </div>
          <p className="text-xs text-slate-500">
            {profile ? `${profile.skills?.length || 0} skills indexed` : 'Upload resume to extract skills'}
          </p>
        </div>

        {/* Top Role Match Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Top Role Match</span>
            <Briefcase className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="my-3">
            <span className="text-3xl font-black text-white">
              {roles[0] ? `${roles[0].match_percentage}%` : 'N/A'}
            </span>
            <p className="text-xs font-medium text-emerald-400 mt-1 truncate">
              {roles[0] ? roles[0].role_title : 'Pending resume upload'}
            </p>
          </div>
          <Link to="/roles" className="text-xs text-indigo-400 hover:underline flex items-center">
            View all role matches <ChevronRight className="w-3.5 h-3.5 ml-0.5" />
          </Link>
        </div>

        {/* Roadmap Progress Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Roadmap Progress</span>
            <CalendarCheck className="w-4 h-4 text-purple-400" />
          </div>
          <div className="my-3">
            <span className="text-3xl font-black text-white">{roadmapProgress}%</span>
            <div className="w-full bg-slate-800 h-2 rounded-full mt-2 overflow-hidden">
              <div
                className="bg-purple-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${roadmapProgress}%` }}
              />
            </div>
          </div>
          <p className="text-xs text-slate-500">
            {completedWeeks} of {roadmap.length || 6} milestones completed
          </p>
        </div>

        {/* Latest Interview Score Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Interview Performance</span>
            <TrendingUp className="w-4 h-4 text-amber-400" />
          </div>
          <div className="my-3">
            <span className="text-3xl font-black text-white">
              {latestInterview?.overall_score ? `${latestInterview.overall_score}%` : 'Not Taken'}
            </span>
            <p className="text-xs text-slate-400 mt-1">
              {latestInterview ? `${latestInterview.language} Interview` : 'Start your first simulation'}
            </p>
          </div>
          <Link to="/reports" className="text-xs text-indigo-400 hover:underline flex items-center">
            View reports & review <ChevronRight className="w-3.5 h-3.5 ml-0.5" />
          </Link>
        </div>
      </div>

      {/* Main Grid: Recommended Roles & Live Jobs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recommended Roles */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Briefcase className="w-5 h-5 text-indigo-400" />
              <h2 className="font-bold text-base text-white">Career Role Recommendations</h2>
            </div>
            <Link to="/roles" className="text-xs text-indigo-400 hover:underline flex items-center">
              Explore All <ChevronRight className="w-3.5 h-3.5 ml-0.5" />
            </Link>
          </div>

          {roles.length === 0 ? (
            <div className="py-10 text-center text-slate-500 border border-dashed border-slate-800 rounded-xl">
              <p className="text-xs">Upload your resume to receive semantic role fit calculations.</p>
              <Link to="/resume" className="mt-3 inline-block text-xs font-semibold text-indigo-400 hover:underline">
                Upload Resume &rarr;
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {roles.slice(0, 3).map((r) => (
                <div key={r.role_id} className="p-4 bg-slate-950/60 border border-slate-800/80 rounded-xl space-y-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-semibold text-sm text-slate-200">{r.role_title}</h4>
                      <span className="text-[10px] text-slate-500 uppercase tracking-wider">{r.category}</span>
                    </div>
                    <span className="text-xs font-extrabold px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                      {r.match_percentage}% Match
                    </span>
                  </div>

                  <p className="text-xs text-slate-400 line-clamp-2">{r.reason}</p>

                  <div className="flex items-center justify-between pt-1">
                    <div className="flex flex-wrap gap-1 max-w-[70%]">
                      {r.matching_skills.slice(0, 3).map((s) => (
                        <span key={s} className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded">
                          {s}
                        </span>
                      ))}
                      {r.missing_skills.length > 0 && (
                        <span className="text-[10px] bg-red-900/20 text-red-400 border border-red-800/30 px-2 py-0.5 rounded">
                          +{r.missing_skills.length} gaps
                        </span>
                      )}
                    </div>
                    <button
                      onClick={() => navigate('/skills', { state: { roleId: r.role_id } })}
                      className="text-xs font-semibold text-indigo-400 hover:underline flex items-center"
                    >
                      Skill Gap &rarr;
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Live Job Recommendations */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Search className="w-5 h-5 text-indigo-400" />
              <h2 className="font-bold text-base text-white">Top Live Job Matches</h2>
            </div>
            <Link to="/jobs" className="text-xs text-indigo-400 hover:underline flex items-center">
              View All Jobs <ChevronRight className="w-3.5 h-3.5 ml-0.5" />
            </Link>
          </div>

          {jobs.length === 0 ? (
            <div className="py-10 text-center text-slate-500 border border-dashed border-slate-800 rounded-xl">
              <p className="text-xs">No jobs aggregated yet. Upload a resume to trigger hybrid BM25 + Vector ranking.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {jobs.slice(0, 3).map((m, idx) => (
                <div key={idx} className="p-4 bg-slate-950/60 border border-slate-800/80 rounded-xl space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h4 className="font-semibold text-sm text-slate-200">{m.job.title}</h4>
                      <p className="text-xs text-indigo-400">{m.job.company} &bull; <span className="text-slate-400">{m.job.location}</span></p>
                    </div>
                    <div className="text-right shrink-0">
                      <span className="text-xs font-extrabold px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                        {m.final_score}% Match
                      </span>
                    </div>
                  </div>

                  {m.job.salary_range && (
                    <p className="text-xs font-medium text-emerald-400">{m.job.salary_range}</p>
                  )}

                  <div className="flex items-center justify-between pt-1">
                    <span className="text-[10px] text-slate-500">Source: {m.job.source}</span>
                    <a
                      href={m.job.apply_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs font-semibold text-slate-300 hover:text-white flex items-center bg-slate-800 hover:bg-slate-700 px-3 py-1 rounded-lg transition-colors"
                    >
                      Apply Now <ExternalLink className="w-3 h-3 ml-1" />
                    </a>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
