import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sparkles } from 'lucide-react';

export const AuthLayout: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center items-center p-6 relative overflow-hidden">
      {/* Background ambient lighting */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-600/15 rounded-full blur-3xl pointer-events-none"></div>

      <div className="w-full max-w-md relative z-10">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center p-3 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 text-indigo-400 mb-4 shadow-lg shadow-indigo-500/10">
            <Sparkles className="w-8 h-8" />
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Smart<span className="text-indigo-400">Hire</span></h1>
          <p className="text-slate-400 text-sm mt-1.5">AI Career Copilot, Skill Gap Mapper & Bilingual Voice Mock Interview Platform</p>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-7 shadow-2xl backdrop-blur-sm">
          <Outlet />
        </div>

        <div className="mt-6 text-center text-xs text-slate-500">
          SmartHire &copy; 2026 &bull; Production Architecture &bull; Zero-key Dev Ready
        </div>
      </div>
    </div>
  );
};
