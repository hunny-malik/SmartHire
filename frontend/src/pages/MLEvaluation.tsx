import React, { useState, useEffect } from 'react';
import { metricsApi } from '../api';
import { MLBenchmark } from '../types';
import {
  BarChart3,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Cpu,
  Zap,
  Target,
  FileText,
  Search,
  Mic,
  GitMerge
} from 'lucide-react';

export const MLEvaluation: React.FC = () => {
  const [benchmarks, setBenchmarks] = useState<MLBenchmark[]>([]);
  const [timestamp, setTimestamp] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBenchmarks();
  }, []);

  const fetchBenchmarks = async () => {
    try {
      setLoading(true);
      const res = await metricsApi.getMlMetrics();
      setBenchmarks(res.data.benchmarks);
      setTimestamp(res.data.timestamp);
    } catch (err) {
      console.error('Failed to load ML metrics', err);
    } finally {
      setLoading(false);
    }
  };

  const getMetricIcon = (name: string) => {
    if (name.includes('Resume')) return <FileText className="w-4 h-4 text-indigo-400" />;
    if (name.includes('Job')) return <Search className="w-4 h-4 text-blue-400" />;
    if (name.includes('Skill')) return <GitMerge className="w-4 h-4 text-purple-400" />;
    return <Mic className="w-4 h-4 text-emerald-400" />;
  };

  return (
    <div className="space-y-8 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight">ML & System Benchmark Dashboard</h1>
          <p className="text-xs text-slate-400 mt-1">
            Empirical evaluation metrics validating NLP extraction, hybrid ranking (NDCG@10), prerequisite recall, and voice latency against strict project targets.
          </p>
        </div>

        <button
          onClick={fetchBenchmarks}
          disabled={loading}
          className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-slate-200 rounded-xl text-xs font-semibold border border-slate-800 flex items-center space-x-2 transition-colors self-start"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Re-run Evaluation</span>
        </button>
      </div>

      {/* Target Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {benchmarks.map((b, idx) => {
          const isPass = b.status === 'PASS';
          return (
            <div
              key={idx}
              className={`bg-slate-900 border rounded-2xl p-6 flex flex-col justify-between space-y-4 transition-all ${
                isPass ? 'border-slate-800' : 'border-amber-500/40 bg-amber-950/10'
              }`}
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-2">
                    {getMetricIcon(b.metric)}
                    <h3 className="font-bold text-sm text-white">{b.metric}</h3>
                  </div>
                  <span
                    className={`text-[10px] font-black px-2 py-0.5 rounded border uppercase ${
                      isPass
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                        : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                    }`}
                  >
                    {isPass ? 'PASS' : 'GAP OBSERVED'}
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-2 bg-slate-950/80 p-3 rounded-xl border border-slate-800 text-center">
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase font-semibold">Target</span>
                    <p className="text-xs font-bold text-slate-300 mt-0.5">{b.target}</p>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase font-semibold">Actual</span>
                    <p className={`text-xs font-extrabold mt-0.5 ${isPass ? 'text-emerald-400' : 'text-amber-400'}`}>
                      {b.actual}
                    </p>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase font-semibold">Gap</span>
                    <p className="text-xs font-semibold text-slate-400 mt-0.5">{b.gap}</p>
                  </div>
                </div>

                <p className="text-xs text-slate-400 leading-relaxed">
                  {b.explanation}
                </p>
              </div>

              <div className="pt-3 border-t border-slate-800/80 text-[10px] text-slate-500 flex items-center justify-between">
                <span>Verified by backend unit evaluation script</span>
                <span className="font-mono">test_eval_ml.py</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Target Metrics Architecture Summary */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 md:p-8 space-y-4">
        <h3 className="font-bold text-base text-white tracking-tight flex items-center">
          <Cpu className="w-5 h-5 mr-2 text-indigo-400" />
          Empirical Validation & Methodology
        </h3>
        <p className="text-xs text-slate-400 leading-relaxed">
          SmartHire enforces strict non-fabrication of ML evaluation metrics. All figures displayed above are computed dynamically by <code>eval_ml.py</code> running automated ground-truth skill extraction tests across 5 verified industry resumes (Junior Python Developer, Senior Full Stack, Data Scientist, DevOps SRE, and React Frontend), NDCG@10 ranking queries against realistic job corpuses, and audio latency telemetry.
        </p>
      </div>
    </div>
  );
};
