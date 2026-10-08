# Changelog

All notable changes to Prompt Optimizer are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-08

### Added
- **Domain Evaluation Engine**: Multi-dimensional scoring across 8 core heuristic dimensions (clarity, specificity, structure, constraints, output specification, role definition, examples, safety) with actionable weakness diagnosis.
- **Domain Alignment Analysis**: Contextual keyword matching and domain alignment diagnostics across cybersecurity, machine learning engineering, software engineering, and data analysis domains.
- **Optimization & Mutation Engine**: Deterministic prompt optimization pipeline with rule-based structural enhancement and optional grounded LLM advisory synthesis.
- **A/B Testing & Benchmarking Suite**: Comparative evaluation harness executing test cases with deterministic assertion matching and multi-model performance profiling (latency, tokens, compliance).
- **Prompt Template Library**: Full persistent CRUD with SQLite, tag indexing, domain filtering, version tracking, and bulk JSON import/export workflows.
- **Enterprise Authentication & RBAC**: Dual-mode auth with Keycloak OIDC Authorization Code Flow + PKCE for production, and zero-credential localhost demo mode with role hierarchy (`viewer`, `operator`, `admin`).
- **Audit Logging**: Tamper-evident operational audit trail recording user mutations, prompt updates, and security events with automatic credential redaction.
- **React + TypeScript Dashboard**: Responsive single-page application featuring distinct workflows for evaluation, optimization with diff inspection, A/B benchmarking, prompt management, and admin audit inspection.
- **Containerization & CI**: Multi-stage non-root Dockerfiles, `compose.yaml` with Keycloak 24 and persistent volume orchestration, and GitHub Actions CI workflow covering pytest, typecheck, Vitest, and container builds.

### Fixed
- **Frontend Test Alignments**: Resolved placeholder and modal title text discrepancies in `EvaluateView` and `LibraryView` components.
- **API Response Duplication**: Refactored evaluation API response serialization helper to streamline endpoint responses.
