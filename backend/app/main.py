from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.models.db_models import PromptTemplate
from app.api.auth import router as auth_router
from app.api.evaluate import router as eval_router
from app.api.optimize import router as opt_router
from app.api.ab_test import router as ab_router
from app.api.benchmark import router as bm_router
from app.api.library import router as lib_router
from app.api.audit import router as audit_router


def seed_initial_templates() -> None:
    db = SessionLocal()
    try:
        count = db.query(PromptTemplate).count()
        if count == 0:
            samples = [
                PromptTemplate(
                    name="Security Threat Modeler",
                    prompt="Analyze the following system architecture and generate STRIDE threat models with concrete mitigation steps.",
                    domain="cybersecurity",
                    tags="security,stride,architecture",
                    version=1,
                ),
                PromptTemplate(
                    name="API Specification Generator",
                    prompt="Generate an OpenAPI 3.1 specification for a user authentication and RBAC microservice including error schemas.",
                    domain="software_engineering",
                    tags="api,openapi,specs",
                    version=1,
                ),
                PromptTemplate(
                    name="Prompt Evaluation Rubric",
                    prompt="Evaluate the given AI agent prompt against criteria for ambiguity, hallucination guardrails, and role definition.",
                    domain="ml_engineering",
                    tags="evals,prompts,benchmarks",
                    version=1,
                ),
            ]
            db.add_all(samples)
            db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings.validate_environment()
    Base.metadata.create_all(bind=engine)
    seed_initial_templates()
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title="Prompt Optimizer API",
        description="Deterministic and LLM-assisted prompt engineering, evaluation, and benchmarking engine.",
        version=settings.app_version,
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.get("/api/health")
    def health_check() -> dict[str, str]:
        return {
            "status": "ok",
            "app": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
        }

    @application.get("/api/version")
    def get_version() -> dict[str, str]:
        return {"version": settings.app_version}

    application.include_router(auth_router, prefix="/api")
    application.include_router(eval_router, prefix="/api")
    application.include_router(opt_router, prefix="/api")
    application.include_router(ab_router, prefix="/api")
    application.include_router(bm_router, prefix="/api")
    application.include_router(lib_router, prefix="/api")
    application.include_router(audit_router, prefix="/api")

    return application


app = create_app()
