import { apiClient } from './client';

export const authApi = {
  register: (data: any) => apiClient.post('/auth/register', data),
  login: (data: any) => apiClient.post('/auth/login', data),
  getMe: () => apiClient.get('/auth/me'),
  updateProfile: (data: any) => apiClient.put('/auth/profile', data),
};

export const resumeApi = {
  uploadResume: (formData: FormData) => apiClient.post('/resume/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getProfile: () => apiClient.get('/resume/profile'),
  updateProfile: (data: any) => apiClient.put('/resume/profile', data),
  downloadResume: (id: string) => apiClient.get(`/resume/download/${id}`, { responseType: 'blob' }),
};

export const rolesApi = {
  getRecommendations: () => apiClient.get('/roles/recommendations'),
  getRoles: () => apiClient.get('/roles'),
  getRole: (id: string) => apiClient.get(`/roles/${id}`),
};

export const jobsApi = {
  getRecommendations: (params?: { role?: string; location?: string; limit?: number }) =>
    apiClient.get('/jobs/recommendations', { params }),
  searchJobs: (data: { query?: string; location?: string; min_match_score?: number }) =>
    apiClient.post('/jobs/search', data),
};

export const skillsApi = {
  analyzeGap: (role_id: string) => apiClient.post('/skills/analyze', { role_id }),
  getRoadmap: (role_id?: string) => apiClient.get('/skills/roadmap', { params: { role_id } }),
  updateRoadmapItem: (itemId: string, status: string) =>
    apiClient.patch(`/skills/roadmap/${itemId}`, { status }),
  getAllSkills: () => apiClient.get('/skills/all'),
};

export const interviewApi = {
  startInterview: (data: { role_id?: string; language?: string; interview_type?: string }) =>
    apiClient.post('/interview/start', data),
  submitAnswer: (interviewId: string, data: { candidate_answer: string; latency_seconds?: number }) =>
    apiClient.post(`/interview/${interviewId}/answer`, data),
  submitVoiceAnswer: (interviewId: string, formData: FormData) =>
    apiClient.post(`/interview/${interviewId}/voice`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
  completeInterview: (interviewId: string) => apiClient.post(`/interview/${interviewId}/complete`),
  getHistory: () => apiClient.get('/interview/history'),
};

export const reportsApi = {
  getReport: (interviewId: string) => apiClient.get(`/reports/${interviewId}`),
  downloadPdf: (interviewId: string) =>
    apiClient.get(`/reports/${interviewId}/download`, { responseType: 'blob' }),
};

export const metricsApi = {
  getMlMetrics: () => apiClient.get('/metrics/ml'),
};
