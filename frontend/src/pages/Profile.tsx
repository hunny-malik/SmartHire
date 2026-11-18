import React, { useState } from 'react';
import { useAuth } from '../auth/AuthContext';
import { authApi } from '../api';
import { User, Mail, Briefcase, Globe, CheckCircle2, AlertCircle, Save } from 'lucide-react';

export const Profile: React.FC = () => {
  const { user, updateUser } = useAuth();

  const [fullName, setFullName] = useState(user?.full_name || '');
  const [targetRole, setTargetRole] = useState(user?.target_role || 'Software Engineer');
  const [language, setLanguage] = useState(user?.language_preference || 'English');
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSuccess('');
    setError('');

    try {
      const res = await authApi.updateProfile({
        full_name: fullName,
        target_role: targetRole,
        language_preference: language,
      });
      updateUser(res.data);
      setSuccess('Profile preferences updated successfully.');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update profile.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-8 pb-12 max-w-2xl">
      <div>
        <h1 className="text-2xl font-black text-white tracking-tight">Candidate Profile & Preferences</h1>
        <p className="text-xs text-slate-400 mt-1">
          Manage your personal information, career target role, and preferred interview dialect.
        </p>
      </div>

      {success && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-xs text-emerald-400 flex items-start space-x-2">
          <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{success}</span>
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-xs text-red-400 flex items-start space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSave} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 md:p-8 space-y-5">
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">Full Name</label>
          <div className="relative">
            <User className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">Email Address (Read-only)</label>
          <div className="relative">
            <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="email"
              disabled
              value={user?.email || ''}
              className="w-full bg-slate-950 border border-slate-800/60 rounded-xl pl-10 pr-4 py-2.5 text-xs text-slate-500 cursor-not-allowed"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">Target Career Role</label>
          <div className="relative">
            <Briefcase className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <select
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 cursor-pointer"
            >
              <option value="Software Engineer">Software Engineer</option>
              <option value="Backend Developer">Backend Developer</option>
              <option value="Frontend Developer">Frontend Developer</option>
              <option value="Full Stack Developer">Full Stack Developer</option>
              <option value="Data Scientist">Data Scientist</option>
              <option value="Machine Learning Engineer">ML Engineer</option>
              <option value="AI Engineer">AI Engineer</option>
              <option value="DevOps Engineer">DevOps Engineer</option>
              <option value="Cloud Architect">Cloud Architect</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">Interview Language Dialect</label>
          <div className="relative">
            <Globe className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 cursor-pointer"
            >
              <option value="English">English</option>
              <option value="Hindi">Hindi (हिंदी)</option>
              <option value="Hinglish">Hinglish (Natural Code-Switching)</option>
            </select>
          </div>
        </div>

        <div className="pt-3 border-t border-slate-800 flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl text-xs font-semibold flex items-center space-x-2 shadow-lg shadow-indigo-600/20 transition-all"
          >
            {saving ? (
              <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            ) : (
              <>
                <Save className="w-4 h-4" />
                <span>Save Changes</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
