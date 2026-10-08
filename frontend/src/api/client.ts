import {
  PaginatedResponse, TokenResponse, UserProfileResponse, OIDCConfigResponse,
  EvaluationRequest, EvaluationResponse, OptimizationRequest, OptimizationResponse,
  ABTestRequest, ABTestResponse, BenchmarkRequest, BenchmarkResponse,
  PromptCreateRequest, PromptUpdateRequest, PromptResponse, AuditLogResponse,
} from '../types';

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = '') {
    this.baseUrl = baseUrl;
  }

  setToken(t: string | null) { this.token = t; }
  getToken(): string | null { return this.token; }

  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      Accept: 'application/json',
      ...((options.headers as Record<string, string>) || {}),
    };
    if (this.token) headers['Authorization'] = `Bearer ${this.token}`;
    if (options.body && typeof options.body === 'string' && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    const res = await fetch(`${this.baseUrl}${path}`, { ...options, headers });
    if (!res.ok) {
      let detail = `Error ${res.status}`;
      try {
        const err = await res.json();
        if (err.detail) detail = typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail);
      } catch {}
      throw new ApiError(res.status, detail);
    }
    return res.json();
  }

  getOIDCConfig() { return this.request<OIDCConfigResponse>('/api/auth/config'); }
  async demoLogin(username: string, role = 'operator') {
    const d = await this.request<TokenResponse>('/api/auth/demo-login', {
      method: 'POST', body: JSON.stringify({ username, role }),
    });
    this.setToken(d.access_token);
    return d;
  }
  getMe() { return this.request<UserProfileResponse>('/api/auth/me'); }
  async logout() {
    try { await this.request<{ status: string }>('/api/auth/logout', { method: 'POST' }); }
    finally { this.setToken(null); }
  }

  getVersion() { return this.request<{ version: string }>('/api/version'); }

  evaluate(req: EvaluationRequest) {
    return this.request<EvaluationResponse>('/api/evaluate', { method: 'POST', body: JSON.stringify(req) });
  }
  getEvaluations(page = 1, pageSize = 20) {
    return this.request<PaginatedResponse<EvaluationResponse>>(`/api/evaluations?page=${page}&page_size=${pageSize}`);
  }
  getEvaluation(id: number) { return this.request<EvaluationResponse>(`/api/evaluations/${id}`); }

  optimize(req: OptimizationRequest) {
    return this.request<OptimizationResponse>('/api/optimize', { method: 'POST', body: JSON.stringify(req) });
  }
  getOptimizations(page = 1, pageSize = 20) {
    return this.request<PaginatedResponse<OptimizationResponse>>(`/api/optimizations?page=${page}&page_size=${pageSize}`);
  }

  runABTest(req: ABTestRequest) {
    return this.request<ABTestResponse>('/api/ab-test', { method: 'POST', body: JSON.stringify(req) });
  }
  getABTests(page = 1, pageSize = 20) {
    return this.request<PaginatedResponse<ABTestResponse>>(`/api/ab-tests?page=${page}&page_size=${pageSize}`);
  }

  runBenchmark(req: BenchmarkRequest) {
    return this.request<BenchmarkResponse>('/api/benchmark', { method: 'POST', body: JSON.stringify(req) });
  }
  getBenchmarks(page = 1, pageSize = 20) {
    return this.request<PaginatedResponse<BenchmarkResponse>>(`/api/benchmarks?page=${page}&page_size=${pageSize}`);
  }

  listPrompts(page = 1, pageSize = 50, domain?: string, search?: string) {
    const p = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (domain) p.set('domain', domain);
    if (search) p.set('search', search);
    return this.request<PaginatedResponse<PromptResponse>>(`/api/prompts?${p.toString()}`);
  }
  getPrompt(id: number) { return this.request<PromptResponse>(`/api/prompts/${id}`); }
  createPrompt(req: PromptCreateRequest) {
    return this.request<PromptResponse>('/api/prompts', { method: 'POST', body: JSON.stringify(req) });
  }
  updatePrompt(id: number, req: PromptUpdateRequest) {
    return this.request<PromptResponse>(`/api/prompts/${id}`, { method: 'PUT', body: JSON.stringify(req) });
  }
  deletePrompt(id: number) {
    return this.request<{ status: string }>(`/api/prompts/${id}`, { method: 'DELETE' });
  }

  getAuditLogs(page = 1, pageSize = 20) {
    return this.request<PaginatedResponse<AuditLogResponse>>(`/api/audit-logs?page=${page}&page_size=${pageSize}`);
  }
}

export async function generatePKCECodes(): Promise<{ verifier: string; challenge: string; state: string }> {
  const rb = new Uint8Array(32);
  crypto.getRandomValues(rb);
  const verifier = Array.from(rb, (b) => b.toString(16).padStart(2, '0')).join('');

  const sb = new Uint8Array(16);
  crypto.getRandomValues(sb);
  const state = Array.from(sb, (b) => b.toString(16).padStart(2, '0')).join('');

  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(verifier));
  const challenge = btoa(String.fromCharCode(...new Uint8Array(digest)))
    .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');

  return { verifier, challenge, state };
}

export function savePKCESession(state: string, verifier: string): void {
  sessionStorage.setItem('oidc_state', state);
  sessionStorage.setItem('oidc_verifier', verifier);
}

export function verifyAndConsumePKCESession(state: string): string | null {
  const savedState = sessionStorage.getItem('oidc_state');
  const savedVerifier = sessionStorage.getItem('oidc_verifier');
  sessionStorage.removeItem('oidc_state');
  sessionStorage.removeItem('oidc_verifier');
  return (!savedState || savedState !== state) ? null : savedVerifier;
}

export const api = new ApiClient();
