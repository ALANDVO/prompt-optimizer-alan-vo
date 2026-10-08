from datetime import datetime
from typing import Any, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int = 1
    page_size: int = 20


# Authentication schemas
class DemoLoginRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=64)
    role: str = Field(default="operator", pattern="^(viewer|operator|admin)$")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 43200
    user_id: str
    username: str
    roles: list[str]


class UserProfileResponse(BaseModel):
    user_id: str
    username: str
    email: str
    roles: list[str]
    is_demo: bool


class OIDCConfigResponse(BaseModel):
    issuer_url: str
    client_id: str
    audience: str
    demo_mode: bool
    environment: str


# Evaluation schemas
class EvaluationRequest(BaseModel):
    prompt: str = Field(..., min_length=3, max_length=20000)
    domain: str = Field(default="general", max_length=64)


class DimensionScore(BaseModel):
    dimension: str
    score: float
    rating: str
    notes: str


class EvaluationResponse(BaseModel):
    id: int | None = None
    prompt: str
    overall_score: float
    grade: str
    clarity_score: float
    specificity_score: float
    structure_score: float
    constraints_score: float
    output_spec_score: float
    role_score: float
    examples_score: float
    safety_score: float
    dimensions: list[DimensionScore]
    weak_areas: list[str]
    recommendations: list[str]
    created_at: datetime


# Optimization schemas
class OptimizationRequest(BaseModel):
    prompt: str = Field(..., min_length=3, max_length=20000)
    target_domain: str = Field(default="general", max_length=64)
    strategy: str = Field(default="structured", max_length=64)
    use_advisory_llm: bool = False


class OptimizationResponse(BaseModel):
    id: int | None = None
    original_prompt: str
    optimized_prompt: str
    strategy: str
    target_domain: str
    score_before: float
    score_after: float
    improvement_delta: float
    diff_summary: str
    advisory_notes: str
    llm_used: bool
    created_at: datetime


# A/B Testing schemas
class TestCaseSchema(BaseModel):
    __test__ = False
    input: str
    expected: str = ""
    assertion_type: str = Field(default="contains", pattern="^(exact|contains|regex|json_validity|min_length)$")


class ABTestRequest(BaseModel):
    prompt_a: str = Field(..., min_length=3)
    prompt_b: str = Field(..., min_length=3)
    cases: list[TestCaseSchema] = Field(..., min_length=1, max_length=100)


class ABCaseResult(BaseModel):
    case_index: int
    input_preview: str
    winner: str
    reason: str
    prompt_a_passed: bool
    prompt_b_passed: bool


class ABTestResponse(BaseModel):
    id: int | None = None
    prompt_a: str
    prompt_b: str
    cases_count: int
    wins_a: int
    wins_b: int
    ties: int
    winner: str
    confidence: float
    details: list[ABCaseResult]
    created_at: datetime


# Benchmark schemas
class BenchmarkRequest(BaseModel):
    prompt: str = Field(..., min_length=3)
    models: list[str] = Field(default=["gpt-4o-mini", "claude-3-5-sonnet", "gemini-1.5-pro", "ollama-llama3"])


class BenchmarkModelResult(BaseModel):
    model: str
    latency_seconds: float
    estimated_tokens: int
    clarity_index: float
    compliance_score: float
    overall_quality: float
    status: str


class BenchmarkResponse(BaseModel):
    id: int | None = None
    prompt: str
    results: list[BenchmarkModelResult]
    best_model: str
    benchmarked_at: datetime


# Prompt Library schemas
class PromptCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=128)
    prompt: str = Field(..., min_length=3)
    domain: str = Field(default="general", max_length=64)
    tags: str = Field(default="", max_length=256)


class PromptUpdateRequest(BaseModel):
    prompt: str | None = None
    domain: str | None = None
    tags: str | None = None


class PromptResponse(BaseModel):
    id: int
    name: str
    prompt: str
    domain: str
    tags: str
    version: int
    created_at: datetime
    updated_at: datetime


# Audit log schemas
class AuditLogResponse(BaseModel):
    id: int
    user_id: str
    username: str
    action: str
    resource: str
    resource_id: str
    details: str
    created_at: datetime
