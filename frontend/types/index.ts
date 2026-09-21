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
  description?: string | null;
  skills?: string | null;
  required_skills?: string | null;
  preferred_skills?: string | null;
  posted_at: string | null;
  status: string;
  fraud_risk?: string | null;
  application_url: string | null;
  score?: JobScore | null;
  created_at: string;
}

export interface JobSource {
  source: string;
  enabled: boolean;
  requires_auth: boolean;
  description: string;
}

export interface JobFetchResponse {
  status: string;
  total_fetched: number;
  new_jobs_saved: number;
  duplicates_skipped: number;
  errors: string[];
}

export interface ManualJobCreate {
  title: string;
  company?: string;
  description?: string;
  url?: string;
  location?: string;
  salary?: string;
  experience?: string;
  application_url?: string;
}

export interface JobScore {
  id?: number;
  total_score: number;
  role_relevance: number;
  core_skills: number;
  distributed_systems: number;
  experience_fit: number;
  location_score: number;
  job_quality: number;
  llm_score?: number | null;
  fit_category: string | null;
  recommended_variant: string | null;
  strengths?: string | null;
  gaps?: string | null;
  risks?: string | null;
  reasoning?: string | null;
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
  github_url?: string | null;
  linkedin_url?: string | null;
  current_company: string | null;
  current_role: string | null;
  total_experience_months: number | null;
  notice_period_days?: number | null;
  current_ctc?: string | null;
  expected_ctc?: string | null;
  preferred_locations: string | null;
  remote_preference?: string | null;
  target_roles: string | null;
  profile_data?: string | null;
}

export interface CandidateFact {
  id: number;
  fact_id: string;
  claim: string;
  category: string;
  source: string;
  verified: boolean;
  allowed_for_resume: boolean;
  allowed_for_application: boolean;
  metadata_json?: string | null;
}

export interface SkillItem {
  name: string;
  proficiency: string;
  years_experience: number;
  verified: boolean;
  evidence_source: string;
  primary: boolean;
}

export interface SkillCategory {
  id: string;
  name: string;
  skills: SkillItem[];
}

export interface ClaimValidationResponse {
  is_supported: boolean;
  confidence: number;
  claim: string;
  conflicts: string[];
  reasoning: string;
  supporting_evidence: Array<{
    fact_id: string;
    category: string;
    claim: string;
    source_reference: string;
    confidence: number;
  }>;
}

export interface ResumeValidationResponse {
  passed: boolean;
  confidence_score: number;
  supported_claims_count: number;
  unsupported_claims_count: number;
  supported_claims: Array<{
    claim: string;
    confidence: number;
    primary_fact_id?: string;
    source?: string;
  }>;
  unsupported_claims: string[];
  hallucinated_skills: string[];
  verified_skills: string[];
  metric_discrepancies: Array<{
    metric: string;
    claimed_value: number;
    verified_value: number;
    issue: string;
  }>;
  warnings: string[];
  errors: string[];
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
