import {
  User,
  TokenResponse,
  Job,
  JobScore,
  JobSource,
  JobFetchResponse,
  ManualJobCreate,
  Application,
  ApplicationDetail,
  ApplicationListResponse,
  ApplicationQuestion,
  CandidateProfile,
  DashboardSummary,
  SetupStatus,
  ResumeVariant,
  ResumeVersion,
  CandidateFact,
  SkillCategory,
  ClaimValidationResponse,
  ResumeValidationResponse,
  CoverLetterResponse,
  FollowupListResponse,
  FollowupDraftRequest,
  FollowupDraftResponse,
  EmailParseRequest,
  EmailParseResponse,
  EmailApplyMatchRequest,
  ApplicationStatusUpdateRequest,
  NotificationListResponse,
  InAppNotification,
  FunnelResponse,
  BreakdownsResponse,
  TimelineResponse,
  LLMUsageResponse,
  LearningLoopResponse,
} from '@/types';

const API_BASE = '/api';

class ApiClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
    if (token) localStorage.setItem('token', token);
    else localStorage.removeItem('token');
  }

  getToken(): string | null {
    if (this.token) return this.token;
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('token');
    }
    return this.token;
  }

  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...((options.headers as Record<string, string>) || {}),
    };
    const token = this.getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
    
    const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
    if (res.status === 401) {
      this.setToken(null);
      if (typeof window !== 'undefined') window.location.href = '/login';
      throw new Error('Unauthorized');
    }
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || error.message || 'Request failed');
    }
    return res.json();
  }

  // Auth
  setupStatus() { return this.request<SetupStatus>('/auth/setup/status'); }
  setup(data: { email: string; password: string; full_name: string }) { return this.request<TokenResponse>('/auth/setup', { method: 'POST', body: JSON.stringify(data) }); }
  login(email: string, password: string) { return this.request<TokenResponse>('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }); }
  me() { return this.request<User>('/auth/me'); }

  // Dashboard
  dashboardSummary() { return this.request<DashboardSummary>('/analytics/summary'); }

  // Jobs
  getJobs(params?: Record<string, string>) {
    const qs = params ? '?' + new URLSearchParams(params).toString() : '';
    return this.request<{ items: Job[]; total: number }>(`/jobs${qs}`);
  }
  getJob(id: number) { return this.request<Job>(`/jobs/${id}`); }
  getJobScore(id: number) { return this.request<JobScore | null>(`/jobs/${id}/score`); }
  createManualJob(data: ManualJobCreate) {
    return this.request<{ job: Job; is_new: boolean; message: string }>('/jobs/manual', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
  fetchJobs(data?: { keyword?: string; location?: string; remote?: boolean; limit?: number; sources?: string[] }) {
    return this.request<JobFetchResponse>('/jobs/fetch', {
      method: 'POST',
      body: JSON.stringify(data || {}),
    });
  }
  getJobSources() {
    return this.request<JobSource[]>('/jobs/sources');
  }
  classifyJob(id: number) {
    return this.request<{ job: Job; score: JobScore; processing_summary: Record<string, unknown> }>(`/jobs/${id}/classify`, {
      method: 'POST',
    });
  }
  processPendingJobs(limit: number = 50) {
    return this.request<{ total_processed: number; passed: number; rejected: number; job_ids: number[] }>(`/jobs/process-pending?limit=${limit}`, {
      method: 'POST',
    });
  }
  analyzeJob(id: number) {
    return this.request<JobScore>(`/jobs/${id}/analyze`, {
      method: 'POST',
    });
  }

  // Applications  
  getApplications(params?: Record<string, string>) {
    const qs = params ? '?' + new URLSearchParams(params).toString() : '';
    return this.request<ApplicationListResponse>(`/applications${qs}`);
  }
  getApplication(id: number) {
    return this.request<ApplicationDetail>(`/applications/${id}`);
  }
  prepareApplication(jobId: number, variantId?: string, tone: string = 'technical') {
    return this.request<ApplicationDetail>(`/applications/prepare/${jobId}`, {
      method: 'POST',
      body: JSON.stringify({ variant_id: variantId, tone }),
    });
  }
  approveApplication(id: number, options: { user_approved?: boolean; dry_run?: boolean; notes?: string } = {}) {
    return this.request<{ message: string; status: string; evidence: Record<string, any> }>(`/applications/${id}/approve`, {
      method: 'POST',
      body: JSON.stringify({
        user_approved: options.user_approved ?? true,
        dry_run: options.dry_run,
        notes: options.notes,
      }),
    });
  }
  rejectApplication(id: number, reason?: string) {
    return this.request<{ message: string }>(`/applications/${id}/reject`, {
      method: 'POST',
      body: JSON.stringify({ reason }),
    });
  }
  updateQuestion(appId: number, questionId: number, finalAnswer: string, approved: boolean = true) {
    return this.request<ApplicationQuestion>(`/applications/${appId}/questions/${questionId}`, {
      method: 'POST',
      body: JSON.stringify({ final_answer: finalAnswer, approved }),
    });
  }

  // Candidate
  getCandidate() { return this.request<CandidateProfile>('/candidate/'); }
  updateCandidate(data: Partial<CandidateProfile>) { return this.request<CandidateProfile>('/candidate/', { method: 'PUT', body: JSON.stringify(data) }); }
  getCandidateFacts(category?: string) {
    const qs = category ? `?category=${encodeURIComponent(category)}` : '';
    return this.request<CandidateFact[]>(`/candidate/facts${qs}`);
  }
  getCandidateSkills() {
    return this.request<{ categories: SkillCategory[]; total_skills: number }>('/candidate/skills');
  }
  syncCandidateKB() {
    return this.request<{ status: string; message: string; facts_count: number; candidate_name: string }>('/candidate/sync', { method: 'POST' });
  }
  validateClaim(claim: string) {
    return this.request<ClaimValidationResponse>('/candidate/validate-claim', { method: 'POST', body: JSON.stringify({ claim }) });
  }
  validateResumeText(content: string) {
    return this.request<ResumeValidationResponse>('/candidate/validate-resume', { method: 'POST', body: JSON.stringify({ content }) });
  }

  // Resumes
  getResumeVariants() { return this.request<ResumeVariant[]>('/resumes/variants'); }
  getResumeVersions(params?: Record<string, string>) {
    const qs = params ? '?' + new URLSearchParams(params).toString() : '';
    return this.request<{ items: ResumeVersion[]; total: number; page: number; per_page: number }>(`/resumes/versions${qs}`);
  }
  getResumeVersion(id: number) { return this.request<ResumeVersion>(`/resumes/versions/${id}`); }
  tailorResume(jobId: number, variantId?: string) {
    const qs = variantId ? `?variant_id=${encodeURIComponent(variantId)}` : '';
    return this.request<ResumeVersion>(`/jobs/${jobId}/tailor-resume${qs}`, { method: 'POST' });
  }

  // Cover Letter
  getCoverLetter(jobId: number) {
    return this.request<CoverLetterResponse>(`/jobs/${jobId}/cover-letter`);
  }
  generateCoverLetter(jobId: number, tone: string = 'technical', customInstructions?: string) {
    return this.request<CoverLetterResponse>(`/jobs/${jobId}/cover-letter`, {
      method: 'POST',
      body: JSON.stringify({ tone, custom_instructions: customInstructions }),
    });
  }
  updateCoverLetter(jobId: number, contentMarkdown: string) {
    return this.request<CoverLetterResponse>(`/jobs/${jobId}/cover-letter`, {
      method: 'PUT',
      body: JSON.stringify({ content_markdown: contentMarkdown }),
    });
  }

  // Monitoring & Follow-ups
  getFollowups() {
    return this.request<FollowupListResponse>('/monitoring/followups');
  }
  draftFollowup(applicationId: number, data: FollowupDraftRequest) {
    return this.request<FollowupDraftResponse>(`/monitoring/followups/${applicationId}/draft`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
  parseEmail(data: EmailParseRequest) {
    return this.request<EmailParseResponse>('/monitoring/email/parse', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
  applyEmailMatch(data: EmailApplyMatchRequest) {
    return this.request<{ success: boolean; application_id: number; status: string; message: string }>('/monitoring/email/apply', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
  getNotifications(unreadOnly: boolean = false) {
    const qs = unreadOnly ? '?unread_only=true' : '';
    return this.request<NotificationListResponse>(`/monitoring/notifications${qs}`);
  }
  markNotificationRead(id: number) {
    return this.request<{ success: boolean }>(`/monitoring/notifications/${id}/read`, { method: 'POST' });
  }
  markAllNotificationsRead() {
    return this.request<{ updated_count: number }>('/monitoring/notifications/read-all', { method: 'POST' });
  }
  updateApplicationStatus(applicationId: number, data: ApplicationStatusUpdateRequest) {
    return this.request<{ message: string }>(`/applications/${applicationId}/status`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Analytics
  getAnalyticsFunnel() {
    return this.request<FunnelResponse>('/analytics/funnel');
  }
  getAnalyticsBreakdowns() {
    return this.request<BreakdownsResponse>('/analytics/breakdowns');
  }
  getAnalyticsTimeline(days: number = 30) {
    return this.request<TimelineResponse>(`/analytics/timeline?days=${days}`);
  }
  getAnalyticsLLMUsage() {
    return this.request<LLMUsageResponse>('/analytics/llm-usage');
  }
  getAnalyticsInsights() {
    return this.request<LearningLoopResponse>('/analytics/insights');
  }

  // Settings
  getSettings() { return this.request<Record<string, unknown>>('/settings'); }
  updateSettings(data: Record<string, unknown>) { return this.request<Record<string, unknown>>('/settings', { method: 'PUT', body: JSON.stringify(data) }); }

  // Health
  health() { return this.request<Record<string, unknown>>('/health'); }
}

export const api = new ApiClient();
