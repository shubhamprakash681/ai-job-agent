import {
  User,
  TokenResponse,
  Job,
  JobScore,
  Application,
  CandidateProfile,
  DashboardSummary,
  SetupStatus,
  ResumeVariant
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

  // Applications  
  getApplications(params?: Record<string, string>) {
    const qs = params ? '?' + new URLSearchParams(params).toString() : '';
    return this.request<{ items: Application[]; total: number }>(`/applications${qs}`);
  }

  // Candidate
  getCandidate() { return this.request<CandidateProfile>('/candidate'); }
  updateCandidate(data: Partial<CandidateProfile>) { return this.request<CandidateProfile>('/candidate', { method: 'PUT', body: JSON.stringify(data) }); }

  // Resumes
  getResumeVariants() { return this.request<ResumeVariant[]>('/resumes/variants'); }

  // Settings
  getSettings() { return this.request<Record<string, unknown>>('/settings'); }
  updateSettings(data: Record<string, unknown>) { return this.request<Record<string, unknown>>('/settings', { method: 'PUT', body: JSON.stringify(data) }); }

  // Health
  health() { return this.request<Record<string, unknown>>('/health'); }
}

export const api = new ApiClient();
