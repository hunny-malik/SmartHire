export interface User {
  id: string;
  email: string;
  full_name: string;
  target_role?: string;
  language_preference: string;
  created_at: string;
}

export interface CandidateProfile {
  id: string;
  user_id: string;
  resume_id?: string;
  full_name?: string;
  email?: string;
  phone?: string;
  education: Array<{ degree: string; institution: string; year: string }>;
  skills: string[];
  experience: Array<{ title: string; company: string; duration: string; responsibilities: string }>;
  projects: Array<{ title: string; description: string; technologies: string[] }>;
  certifications: Array<{ title: string; issuer: string; year: string }>;
  job_titles: string[];
  updated_at: string;
}

export interface RoleRecommendation {
  role_id: string;
  role_title: string;
  category: string;
  match_percentage: number;
  matching_skills: string[];
  missing_skills: string[];
  reason: string;
}

export interface RoleOut {
  id: string;
  title: string;
  description: string;
  category: string;
  min_experience_months: number;
  required_skills: Array<{
    skill_name: string;
    category: string;
    importance_weight: number;
    required_level: string;
  }>;
}

export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  job_type: string;
  salary_range?: string;
  experience_level: string;
  required_skills: string[];
  description: string;
  apply_url: string;
  source: string;
  posted_date: string;
}

export interface JobMatch {
  job: Job;
  bm25_score: number;
  cosine_score: number;
  final_score: number;
  matched_skills: string[];
  is_live_external: boolean;
}

export interface SkillGapItem {
  name: string;
  current_level: string;
  required_level: string;
  gap_score: number;
  importance: number;
  priority: 'critical' | 'high' | 'medium' | 'low';
  prerequisites: string[];
  recommended_resources: Array<{ title: string; url: string; type: string; est_hours: number }>;
  estimated_learning_hours: number;
}

export interface SkillGapAnalysis {
  role_id: string;
  role_title: string;
  match_percentage: number;
  gap_percentage: number;
  matching_skills: Array<{ name: string; level: string; importance: number; category: string }>;
  missing_skills: SkillGapItem[];
  prerequisite_dag: {
    nodes: Array<{ id: string; label: string; priority: string; importance: number }>;
    edges: Array<{ from: string; to: string }>;
  };
  career_transition_path: string[];
}

export interface RoadmapItem {
  id: string;
  week_number: number;
  phase_title: string;
  skill_name: string;
  status: 'not_started' | 'in_progress' | 'completed';
  learning_resources: Array<{ title: string; url: string; type: string; est_hours: number }>;
  estimated_hours: number;
}

export interface Question {
  id: string;
  sequence_order: number;
  category: string;
  difficulty: string;
  skill?: string;
  question_text: string;
  expected_concepts: string[];
  audio_base64?: string;
}

export interface AnswerEvaluation {
  technical_accuracy: number;
  communication_score: number;
  confidence_score: number;
  problem_solving_score: number;
  completeness_score: number;
  feedback: string;
  strengths: string[];
  weaknesses: string[];
  is_follow_up: boolean;
  next_question?: Question;
}

export interface InterviewSession {
  id: string;
  role_id?: string;
  role_title?: string;
  interview_type: string;
  language: string;
  status: string;
  overall_score?: number;
  started_at: string;
  questions_count: number;
}

export interface InterviewReport {
  id: string;
  interview_id: string;
  candidate_name: string;
  target_role: string;
  interview_date: string;
  overall_score: number;
  technical_score: number;
  communication_score: number;
  problem_solving_score: number;
  confidence_score: number;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  improvement_suggestions: string[];
  revision_topics: string[];
  qa_records: Array<{
    sequence_order: number;
    category: string;
    skill?: string;
    question_text: string;
    candidate_answer: string;
    technical_accuracy: number;
    communication_score: number;
    problem_solving_score: number;
    confidence_score: number;
    feedback: string;
    strengths: string[];
    weaknesses: string[];
  }>;
  pdf_download_url?: string;
}

export interface MLBenchmark {
  metric: string;
  target: string;
  actual: string;
  gap: string;
  status: 'PASS' | 'NEEDS_IMPROVEMENT';
  explanation: string;
}
