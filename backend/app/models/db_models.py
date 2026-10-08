from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime
from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(128), unique=True, index=True, nullable=False)
    prompt = Column(Text, nullable=False)
    domain = Column(String(64), default="general", nullable=False)
    tags = Column(String(256), default="", nullable=False)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class EvaluationRecord(Base):
    __tablename__ = "evaluation_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    prompt = Column(Text, nullable=False)
    overall_score = Column(Float, nullable=False)
    grade = Column(String(4), nullable=False)
    clarity_score = Column(Float, nullable=False)
    specificity_score = Column(Float, nullable=False)
    structure_score = Column(Float, nullable=False)
    constraints_score = Column(Float, nullable=False)
    output_spec_score = Column(Float, nullable=False)
    role_score = Column(Float, nullable=False)
    examples_score = Column(Float, nullable=False)
    safety_score = Column(Float, nullable=False)
    weak_areas = Column(Text, default="[]", nullable=False)
    recommendations = Column(Text, default="[]", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class OptimizationRecord(Base):
    __tablename__ = "optimization_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    original_prompt = Column(Text, nullable=False)
    optimized_prompt = Column(Text, nullable=False)
    strategy = Column(String(64), nullable=False)
    target_domain = Column(String(64), default="general", nullable=False)
    score_before = Column(Float, nullable=False)
    score_after = Column(Float, nullable=False)
    improvement_delta = Column(Float, nullable=False)
    diff_summary = Column(Text, default="", nullable=False)
    advisory_notes = Column(Text, default="", nullable=False)
    llm_used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class ABTestRecord(Base):
    __tablename__ = "ab_test_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    prompt_a = Column(Text, nullable=False)
    prompt_b = Column(Text, nullable=False)
    cases_count = Column(Integer, nullable=False)
    wins_a = Column(Integer, default=0, nullable=False)
    wins_b = Column(Integer, default=0, nullable=False)
    ties = Column(Integer, default=0, nullable=False)
    winner = Column(String(16), nullable=False)
    details = Column(Text, default="[]", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class BenchmarkRecord(Base):
    __tablename__ = "benchmark_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    prompt = Column(Text, nullable=False)
    models = Column(Text, nullable=False)
    results = Column(Text, nullable=False)
    best_model = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(128), nullable=False)
    username = Column(String(128), nullable=False)
    action = Column(String(64), nullable=False)
    resource = Column(String(64), nullable=False)
    resource_id = Column(String(64), default="", nullable=False)
    details = Column(Text, default="", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
