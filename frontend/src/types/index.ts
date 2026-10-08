export interface PaginatedResponse<T> { items: T[]; total: number; page: number; page_size: number; }
export type UserRole = 'viewer' | 'operator' | 'admin';

export interface UserProfileResponse { user_id: string; username: string; email: string; roles: string[]; is_demo: boolean; }
export interface TokenResponse { access_token: string; token_type: string; expires_in: number; user_id: string; username: string; roles: string[]; }
export interface OIDCConfigResponse { issuer_url: string; client_id: string; audience: string; demo_mode: boolean; environment: string; }

export interface DimensionScore { dimension: string; score: number; rating: string; notes: string; }
export interface EvaluationRequest { prompt: string; domain?: string; }
export interface EvaluationResponse {
  id?: number; prompt: string; overall_score: number; grade: string;
  clarity_score: number; specificity_score: number; structure_score: number;
  constraints_score: number; output_spec_score: number; role_score: number;
  examples_score: number; safety_score: number; dimensions: DimensionScore[];
  weak_areas: string[]; recommendations: string[]; created_at: string;
}

export interface OptimizationRequest { prompt: string; target_domain?: string; strategy?: string; use_advisory_llm?: boolean; }
export interface OptimizationResponse {
  id?: number; original_prompt: string; optimized_prompt: string; strategy: string;
  target_domain: string; score_before: number; score_after: number;
  improvement_delta: number; diff_summary: string; advisory_notes: string;
  llm_used: boolean; created_at: string;
}

export interface TestCaseSchema { input: string; expected?: string; assertion_type: 'exact' | 'contains' | 'regex' | 'json_validity' | 'min_length'; }
export interface ABTestRequest { prompt_a: string; prompt_b: string; cases: TestCaseSchema[]; }
export interface ABCaseResult { case_index: number; input_preview: string; winner: string; reason: string; prompt_a_passed: boolean; prompt_b_passed: boolean; }
export interface ABTestResponse {
  id?: number; prompt_a: string; prompt_b: string; cases_count: number;
  wins_a: number; wins_b: number; ties: number; winner: string;
  confidence: number; details: ABCaseResult[]; created_at: string;
}

export interface BenchmarkRequest { prompt: string; models?: string[]; }
export interface BenchmarkModelResult { model: string; latency_seconds: number; estimated_tokens: number; clarity_index: number; compliance_score: number; overall_quality: number; status: string; }
export interface BenchmarkResponse { id?: number; prompt: string; results: BenchmarkModelResult[]; best_model: string; benchmarked_at: string; }

export interface PromptCreateRequest { name: string; prompt: string; domain?: string; tags?: string; }
export interface PromptUpdateRequest { prompt?: string; domain?: string; tags?: string; }
export interface PromptResponse { id: number; name: string; prompt: string; domain: string; tags: string; version: number; created_at: string; updated_at: string; }

export interface AuditLogResponse { id: number; user_id: string; username: string; action: string; resource: string; resource_id: string; details: string; created_at: string; }
