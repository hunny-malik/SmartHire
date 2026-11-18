import React, { useState, useEffect, useRef } from 'react';
import { resumeApi } from '../api';
import { CandidateProfile } from '../types';
import {
  UploadCloud,
  FileText,
  CheckCircle2,
  AlertCircle,
  Download,
  Briefcase,
  GraduationCap,
  FolderGit2,
  Award,
  Sparkles,
  RefreshCw,
  Plus
} from 'lucide-react';

export const ResumeUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [profile, setProfile] = useState<CandidateProfile | null>(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const res = await resumeApi.getProfile();
      setProfile(res.data);
    } catch (err) {
      console.info('No candidate profile uploaded yet.');
    }
  };

  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (f: File) => {
    setError('');
    const ext = f.name.split('.').pop()?.toLowerCase();
    if (!['pdf', 'docx'].includes(ext || '')) {
      setError('Please upload a valid PDF or DOCX file.');
      return;
    }
    if (f.size > 10 * 1024 * 1024) {
      setError('File size exceeds the 10MB limit.');
      return;
    }
    setFile(f);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError('');
    setSuccess('');
    setProgress(20);

    const formData = new FormData();
    formData.append('file', file);

    try {
      setProgress(50);
      const res = await resumeApi.uploadResume(formData);
      setProgress(100);
      setProfile(res.data);
      setSuccess('Resume successfully uploaded and structured profile generated!');
      setFile(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Resume parsing failed. Please verify file integrity.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-8 pb-12">
      <div>
        <h1 className="text-2xl font-black text-white tracking-tight">AI Resume Parser & Profile Extractor</h1>
        <p className="text-xs text-slate-400 mt-1">
          Upload your resume in PDF or DOCX. SmartHire extracts your tech skills, projects, and career milestones using NLP.
        </p>
      </div>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-xs text-red-400 flex items-start space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-xs text-emerald-400 flex items-start space-x-2">
          <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{success}</span>
        </div>
      )}

      {/* Upload Drag & Drop Zone */}
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleFileDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-2xl p-8 md:p-12 text-center cursor-pointer transition-all ${
          file
            ? 'border-indigo-500 bg-indigo-950/20'
            : 'border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-900'
        }`}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileSelect}
          accept=".pdf,.docx"
          className="hidden"
        />

        <div className="flex flex-col items-center justify-center space-y-3">
          <div className="w-14 h-14 rounded-2xl bg-indigo-600/20 text-indigo-400 flex items-center justify-center border border-indigo-500/30">
            <UploadCloud className="w-7 h-7" />
          </div>

          <div>
            <h3 className="text-sm font-bold text-white">
              {file ? file.name : 'Click to upload or drag & drop your resume'}
            </h3>
            <p className="text-xs text-slate-500 mt-1">Supported formats: PDF, DOCX (Max 10MB)</p>
          </div>

          {file && (
            <div className="pt-2">
              <span className="text-xs font-semibold px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                {(file.size / 1024 / 1024).toFixed(2)} MB &bull; Ready for AI extraction
              </span>
            </div>
          )}
        </div>
      </div>

      {file && (
        <div className="flex justify-end space-x-3">
          <button
            onClick={() => setFile(null)}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl"
          >
            Cancel
          </button>
          <button
            onClick={handleUpload}
            disabled={uploading}
            className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl flex items-center space-x-2 shadow-lg shadow-indigo-600/20"
          >
            {uploading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Parsing Resume NLP Pipeline... ({progress}%)</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Extract Candidate Profile</span>
              </>
            )}
          </button>
        </div>
      )}

      {/* Extracted Profile View */}
      {profile && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 md:p-8 space-y-8">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-slate-800 gap-4">
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-xl font-bold text-white">{profile.full_name}</h2>
                <span className="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded font-semibold">
                  Verified Extraction
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                {profile.email} &bull; {profile.phone || 'Phone not specified'}
              </p>
            </div>

            {profile.resume_id && (
              <a
                href={`http://localhost:8000/api/resume/download/${profile.resume_id}`}
                target="_blank"
                rel="noreferrer"
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl flex items-center space-x-1.5 self-start"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Download Original Document</span>
              </a>
            )}
          </div>

          {/* Extracted Skills Section */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center">
              <Sparkles className="w-4 h-4 mr-1.5 text-indigo-400" />
              Extracted Technical Skills ({profile.skills?.length || 0})
            </h3>
            <div className="flex flex-wrap gap-2">
              {profile.skills?.map((skill) => (
                <span
                  key={skill}
                  className="px-3 py-1 bg-slate-800/80 border border-slate-700/80 text-slate-200 rounded-lg text-xs font-medium"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>

          {/* Experience Section */}
          <div className="space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center">
              <Briefcase className="w-4 h-4 mr-1.5 text-indigo-400" />
              Work Experience
            </h3>
            <div className="space-y-3">
              {profile.experience?.map((exp, idx) => (
                <div key={idx} className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl space-y-1">
                  <div className="flex justify-between items-start">
                    <h4 className="font-semibold text-sm text-slate-200">{exp.title}</h4>
                    <span className="text-xs text-slate-500">{exp.duration}</span>
                  </div>
                  <p className="text-xs text-indigo-400">{exp.company}</p>
                  <p className="text-xs text-slate-400 pt-1 leading-relaxed">{exp.responsibilities}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Projects Section */}
          <div className="space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center">
              <FolderGit2 className="w-4 h-4 mr-1.5 text-indigo-400" />
              Key Technical Projects
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {profile.projects?.map((proj, idx) => (
                <div key={idx} className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl space-y-2">
                  <h4 className="font-semibold text-sm text-slate-200">{proj.title}</h4>
                  <p className="text-xs text-slate-400 leading-relaxed">{proj.description}</p>
                  {proj.technologies && (
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {proj.technologies.map((t) => (
                        <span key={t} className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded">
                          {t}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Education & Certifications */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center">
                <GraduationCap className="w-4 h-4 mr-1.5 text-indigo-400" />
                Education
              </h3>
              {profile.education?.map((edu, idx) => (
                <div key={idx} className="p-3.5 bg-slate-950/60 border border-slate-800 rounded-xl space-y-0.5">
                  <p className="font-semibold text-xs text-slate-200">{edu.degree}</p>
                  <p className="text-xs text-slate-400">{edu.institution} ({edu.year})</p>
                </div>
              ))}
            </div>

            <div className="space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center">
                <Award className="w-4 h-4 mr-1.5 text-indigo-400" />
                Certifications
              </h3>
              {profile.certifications?.length > 0 ? (
                profile.certifications.map((cert, idx) => (
                  <div key={idx} className="p-3.5 bg-slate-950/60 border border-slate-800 rounded-xl">
                    <p className="font-semibold text-xs text-slate-200">{cert.title}</p>
                    <p className="text-xs text-slate-500">{cert.issuer} &bull; {cert.year}</p>
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-500 italic">No formal certifications detected in document.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
