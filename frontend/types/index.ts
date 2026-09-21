export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Job {
  id: number;
  source: string;
  title: string;
  company: string | null;
  locations: string | null;
  remote: boolean;
  experience_min: number | null;
  experience_max: number | null;
  employment_type: string | null;
  salary_min: number | null;
  salary_max: number | null;
  currency: string;
  posted_at: string | null;
  status: string;
  application_url: string | null;
  created_at: string;
}

export interface JobScore {
  total_score: number;
  role_relevance: number;
  core_skills: number;
  distributed_systems: number;
  experience_fit: number;
  location_score: number;
  job_quality: number;
  fit_category: string | null;
  recommended_variant: string | null;
}

export interface Application {
  id: number;
  job_id: number;
  status: string;
  applied_at: string | null;
  job_score: number | null;
  notes: string | null;
  created_at: string;
}

export interface CandidateProfile {
  id: number;
  full_name: string;
  email: string | null;
  phone: string | null;
  location: string | null;
  portfolio_url: string | null;
  current_company: string | null;
  current_role: string | null;
  total_experience_months: number | null;
  preferred_locations: string | null;
  target_roles: string | null;
}

export interface DashboardSummary {
  total_jobs: number;
  new_jobs_today: number;
  high_priority_jobs: number;
  applications_pending: number;
  applications_submitted: number;
  applications_total: number;
  interview_count: number;
  response_rate: number;
  top_companies: string[];
  top_cities: string[];
}

export interface SetupStatus {
  is_setup: boolean;
  message: string;
}

export interface ResumeVariant {
  id: number;
  name: string;
  display_name: string;
  description: string | null;
  is_default: boolean;
}
