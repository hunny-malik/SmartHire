import React from 'react';
import { useAuth } from '../auth/AuthContext';
import { authApi } from '../api';
import { Sparkles, Globe, LogOut, User as UserIcon } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout, updateUser } = useAuth();

  const handleLanguageChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newLang = e.target.value;
    try {
      await authApi.updateProfile({ language_preference: newLang });
      updateUser({ language_preference: newLang });
    } catch (err) {
      console.error('Failed to update language preference', err);
    }
  };

  return (
    <header className="h-16 bg-slate-900/80 backdrop-blur border-b border-slate-800 px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center space-x-3">
        <div className="bg-indigo-600/20 text-indigo-400 p-2 rounded-lg border border-indigo-500/30 flex items-center justify-center">
          <Sparkles className="w-5 h-5 text-indigo-400" />
        </div>
        <div>
          <span className="font-bold text-lg text-white tracking-tight">Smart<span className="text-indigo-400">Hire</span></span>
          <span className="ml-2 text-xs uppercase px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-semibold tracking-wider">AI Copilot</span>
        </div>
      </div>

      <div className="flex items-center space-x-5">
        {user?.target_role && (
          <div className="hidden md:flex items-center text-xs text-slate-400 bg-slate-800/80 px-3 py-1.5 rounded-full border border-slate-700/60">
            <span className="w-2 h-2 rounded-full bg-emerald-500 mr-2 animate-pulse"></span>
            Target: <strong className="text-slate-200 ml-1">{user.target_role}</strong>
          </div>
        )}

        {/* Language Switcher */}
        <div className="flex items-center space-x-1.5 bg-slate-800/80 border border-slate-700/60 rounded-lg px-2.5 py-1 text-xs">
          <Globe className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={user?.language_preference || 'English'}
            onChange={handleLanguageChange}
            className="bg-transparent text-slate-200 font-medium focus:outline-none cursor-pointer"
          >
            <option value="English" className="bg-slate-900 text-white">English</option>
            <option value="Hindi" className="bg-slate-900 text-white">Hindi (हिंदी)</option>
            <option value="Hinglish" className="bg-slate-900 text-white">Hinglish</option>
          </select>
        </div>

        {/* User profile dropdown & logout */}
        <div className="flex items-center space-x-3 border-l border-slate-800 pl-4">
          <div className="flex items-center space-x-2 text-sm text-slate-300">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center font-bold text-white shadow-sm">
              {user?.full_name ? user.full_name[0].toUpperCase() : <UserIcon className="w-4 h-4" />}
            </div>
            <span className="hidden sm:inline font-medium text-slate-200">{user?.full_name}</span>
          </div>

          <button
            onClick={logout}
            title="Log Out"
            className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
};
