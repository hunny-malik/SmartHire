import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './auth/AuthContext';
import { ProtectedRoute } from './auth/ProtectedRoute';
import { AppLayout } from './layouts/AppLayout';
import { AuthLayout } from './layouts/AuthLayout';

// Pages
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { ResumeUpload } from './pages/ResumeUpload';
import { RoleRecommendations } from './pages/RoleRecommendations';
import { JobsDirectory } from './pages/JobsDirectory';
import { SkillGapAnalysis } from './pages/SkillGapAnalysis';
import { LearningRoadmap } from './pages/LearningRoadmap';
import { MockInterview } from './pages/MockInterview';
import { InterviewHistory } from './pages/InterviewHistory';
import { InterviewReportView } from './pages/InterviewReportView';
import { MLEvaluation } from './pages/MLEvaluation';
import { Profile } from './pages/Profile';

export function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Auth Routes */}
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
          </Route>

          {/* Protected Application Routes */}
          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/resume" element={<ResumeUpload />} />
              <Route path="/roles" element={<RoleRecommendations />} />
              <Route path="/jobs" element={<JobsDirectory />} />
              <Route path="/skills" element={<SkillGapAnalysis />} />
              <Route path="/roadmap" element={<LearningRoadmap />} />
              <Route path="/interview" element={<MockInterview />} />
              <Route path="/reports" element={<InterviewHistory />} />
              <Route path="/interview/:id/report" element={<InterviewReportView />} />
              <Route path="/benchmarks" element={<MLEvaluation />} />
              <Route path="/evaluation" element={<Navigate to="/benchmarks" replace />} />
              <Route path="/profile" element={<Profile />} />
            </Route>
          </Route>

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
