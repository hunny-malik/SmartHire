import React, { useState, useEffect } from 'react';
import { jobsApi } from '../api';
import { JobMatch } from '../types';
import {
  Search,
  MapPin,
  Briefcase,
  DollarSign,
  Calendar,
  ExternalLink,
  SlidersHorizontal,
  CheckCircle2,
  Sparkles,
  AlertCircle
} from 'lucide-react';

export const JobsDirectory: React.FC = () => {
  const [jobs, setJobs] = useState<JobMatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');
  const [location, setLocation] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      setError('');
      const res = await jobsApi.getRecommendations({
        role: query || undefined,
        location: location || undefined,
        limit: 10,
      });
      setJobs(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to aggregate live jobs. Ensure resume is uploaded.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchJobs();
  };

  return (
    <div className="space-y-8 pb-12">
      <div>
        <h1 className="text-2xl font-black text-white tracking-tight">Live Job Search & Hybrid Matcher</h1>
        <p className="text-xs text-slate-400 mt-1">
          Aggregated live job listings ranked via hybrid BM25 Okapi keyword scoring (45%) and dense vector cosine similarity (55%).
        </p>
      </div>

      {/* Filter / Search Bar */}
      <form onSubmit={handleSearch} className="bg-slate-900 border border-slate-800 rounded-2xl p-4 flex flex-col md:flex-row gap-3">
        <div className="flex-1 relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search role, skills, keywords (e.g. Backend Developer, FastAPI)..."
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="w-full md:w-64 relative">
          <MapPin className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="Location (e.g. Remote, San Francisco)..."
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <button
          type="submit"
          className="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold shadow-md shadow-indigo-600/20 transition-all"
        >
          Search Jobs
        </button>
      </form>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-xs text-red-400 flex items-start space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* Jobs Grid */}
      {loading ? (
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 h-48 animate-pulse"></div>
          ))}
        </div>
      ) : jobs.length === 0 ? (
        <div className="p-12 text-center text-slate-500 border border-dashed border-slate-800 rounded-2xl bg-slate-900/40">
          <Briefcase className="w-12 h-12 mx-auto text-slate-600 mb-3" />
          <p className="text-sm font-semibold text-slate-300">No matching jobs found.</p>
          <p className="text-xs text-slate-500 mt-1">Try broadening your search query or location criteria.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {jobs.map((item, idx) => {
            const { job, final_score, bm25_score, cosine_score, matched_skills, is_live_external } = item;
            return (
              <div
                key={job.id || idx}
                className="bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-all space-y-4"
              >
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center space-x-2">
                      <h3 className="font-bold text-base text-white">{job.title}</h3>
                      {is_live_external && (
                        <span className="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded font-bold">
                          LIVE API
                        </span>
                      )}
                    </div>
                    <p className="text-xs font-semibold text-indigo-400 mt-0.5">
                      {job.company} &bull; <span className="text-slate-400 font-normal">{job.location}</span>
                    </p>

                    <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400 mt-2">
                      <span className="flex items-center">
                        <Briefcase className="w-3.5 h-3.5 mr-1 text-slate-500" />
                        {job.job_type}
                      </span>
                      {job.salary_range && (
                        <span className="flex items-center text-emerald-400 font-semibold">
                          <DollarSign className="w-3.5 h-3.5 mr-0.5" />
                          {job.salary_range}
                        </span>
                      )}
                      <span className="flex items-center text-slate-500">
                        <Calendar className="w-3.5 h-3.5 mr-1" />
                        {job.posted_date}
                      </span>
                      <span className="text-[11px] text-slate-500">
                        Via {job.source}
                      </span>
                    </div>
                  </div>

                  {/* Hybrid Rank Score Breakdown Badge */}
                  <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 shrink-0 text-right space-y-1">
                    <div className="text-sm font-extrabold text-white flex items-center justify-end space-x-1">
                      <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                      <span>{final_score}% Match</span>
                    </div>
                    <div className="text-[10px] text-slate-500 font-medium">
                      BM25 (0.45): <span className="text-slate-300">{bm25_score}%</span> &bull; Semantic (0.55): <span className="text-slate-300">{cosine_score}%</span>
                    </div>
                  </div>
                </div>

                <p className="text-xs text-slate-400 leading-relaxed line-clamp-3">
                  {job.description}
                </p>

                {/* Required Skills & Matched Skills */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t border-slate-800/80">
                  <div className="flex flex-wrap items-center gap-1.5 max-w-xl">
                    <span className="text-[11px] font-semibold text-slate-500 mr-1">Skills:</span>
                    {job.required_skills?.map((s) => {
                      const isMatched = matched_skills.includes(s);
                      return (
                        <span
                          key={s}
                          className={`text-[10px] px-2 py-0.5 rounded font-medium ${
                            isMatched
                              ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/30'
                              : 'bg-slate-800 text-slate-400 border border-slate-700/60'
                          }`}
                        >
                          {isMatched && <CheckCircle2 className="w-2.5 h-2.5 inline mr-1 text-emerald-400" />}
                          {s}
                        </span>
                      );
                    })}
                  </div>

                  <a
                    href={job.apply_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold flex items-center space-x-1.5 shadow-md shadow-indigo-600/20 transition-all self-start sm:self-auto shrink-0"
                  >
                    <span>Apply at Source</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
