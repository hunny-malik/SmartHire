import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  Briefcase,
  Search,
  GitMerge,
  CalendarCheck,
  Mic,
  Award,
  BarChart3,
  User
} from 'lucide-react';

const NAV_ITEMS = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/resume', label: 'Resume Parser', icon: FileText },
  { path: '/roles', label: 'Role Finder', icon: Briefcase },
  { path: '/jobs', label: 'Live Jobs', icon: Search },
  { path: '/skills', label: 'Skill Gap Graph', icon: GitMerge },
  { path: '/roadmap', label: 'Learning Roadmap', icon: CalendarCheck },
  { path: '/interview', label: 'Mock Interview', icon: Mic, highlight: true },
  { path: '/reports', label: 'Reports & History', icon: Award },
  { path: '/benchmarks', label: 'ML Benchmarks', icon: BarChart3 },
  { path: '/profile', label: 'Profile Settings', icon: User },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between h-[calc(100vh-4rem)] sticky top-16 select-none">
      <div className="py-4 px-3 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-wider text-slate-500">
          Career Copilot Navigation
        </div>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `
                flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition-all group
                ${isActive
                  ? 'bg-indigo-600/15 text-indigo-400 border border-indigo-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }
                ${item.highlight ? 'relative font-semibold' : ''}
              `}
            >
              <Icon className={`w-4 h-4 mr-3 transition-colors ${item.highlight ? 'text-indigo-400' : 'text-slate-400 group-hover:text-slate-200'}`} />
              <span>{item.label}</span>
              {item.highlight && (
                <span className="ml-auto text-[10px] bg-indigo-500/20 text-indigo-300 px-1.5 py-0.5 rounded border border-indigo-500/30 animate-pulse">
                  AI Live
                </span>
              )}
            </NavLink>
          );
        })}
      </div>

      <div className="p-4 border-t border-slate-800 bg-slate-950/40">
        <div className="p-3 bg-gradient-to-br from-indigo-950/60 to-slate-900 rounded-xl border border-indigo-900/40 text-xs">
          <p className="font-semibold text-slate-200">Bilingual Voice Mode</p>
          <p className="text-slate-400 mt-0.5">Supports real-time English, Hindi, and Hinglish mock speech.</p>
        </div>
      </div>
    </aside>
  );
};
