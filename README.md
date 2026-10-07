# prompt-optimizer-alan-vo

> AI-powered prompt engineering tool that evaluates raw prompts, rewrites them for clarity and specificity, benchmarks across models, and generates A/B test harnesses for systematic prompt improvement.

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-React-3178C6)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)
![SSO](https://img.shields.io/badge/SSO-SAML%20%2F%20OAuth2-8A2BE2)
![License](https://img.shields.io/badge/License-MIT-green)
![AI](https://img.shields.io/badge/AI-Powered-purple)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

</div>

## Why prompt-optimizer-alan-vo?

AI-powered prompt engineering tool that evaluates raw prompts, rewrites them for clarity and specificity, benchmarks across models, and generates A/B test harnesses for systematic prompt improvement.

Built by [Alan Vo](https://github.com/ALANDVO) — AI/ML & cybersecurity engineer.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     prompt-optimizer-alan-vo                                    │
├─────────────┬─────────────┬─────────────┬───────────────────┤
│  Frontend   │   API Layer │  Services   │   LLM Engine      │
│  React/TS   │  FastAPI    │  Domain     │  Multi-provider   │
│  Dashboard  │  SSO/SAML   │  Logic      │  OpenAI/Claude/   │
│  Real-time  │  JWT Auth   │  Processing │  Gemini/Ollama    │
└─────────────┴─────────────┴─────────────┴───────────────────┘
         │              │              │               │
         ▼              ▼              ▼               ▼
    ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────────┐
    │ Browser │   │  REST   │   │  Domain │   │  LLM API    │
    │  SPA    │   │  API    │   │  Logic  │   │  (any)      │
    └─────────┘   └─────────┘   └─────────┘   └─────────────┘
```

## Features

- **Prompt quality scoring across 8 dimensions (clarity, specificity, structure, etc.)**
- **LLM-driven prompt rewriting with side-by-side before/after comparison**
- **Multi-model benchmarking with token cost and latency tracking**
- **A/B test harness generation for systematic prompt evaluation**
- **Prompt template library with versioning and rollback**
- **Batch evaluation across test case suites with pass/fail reporting**
- **Export to JSON, Markdown, or YAML for CI/CD integration**

## Quick Start

### Docker (Recommended)

```bash
git clone https://github.com/ALANDVO/prompt-optimizer-alan-vo.git
cd prompt-optimizer-alan-vo
cp .env.example .env
docker compose up -d
# Open http://localhost:3000
```

### Local Development

```bash
git clone https://github.com/ALANDVO/prompt-optimizer-alan-vo.git
cd prompt-optimizer-alan-vo
pip install -r requirements.txt
```

## Usage

```
python main.py evaluate "Summarize this email" --score
python main.py optimize "Write code for a REST API" --target python
python main.py benchmark --prompt-file prompt.txt --models gpt-4o,claude-3-opus
python main.py ab-test --cases tests.json --prompt-a v1.txt --prompt-b v2.txt
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_API_KEY` | LLM API key (OpenAI, Anthropic, Gemini) | Required |
| `LLM_BASE_URL` | Custom LLM endpoint (Ollama, vLLM) | `https://api.openai.com/v1` |
| `LLM_MODEL` | Model name | `gpt-4o` |
| `SAML_IDP_ENTITY` | SAML Identity Provider URL | — |
| `JWT_SECRET` | JWT signing secret | Generate one |

## Tech Stack

`Python` `OpenAI/Anthropic/Gemini` `Prompt Engineering` `A/B Testing` `LLM Benchmarking`

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/login` | Login (SSO or email) |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/stats` | Statistics & metrics |
| `POST` | `/api/process` | Main processing endpoint |
| `GET` | `/api/results` | Query results |

## SSO Setup

### SAML
1. Set `SAML_IDP_ENTITY` to your IdP URL
2. Set `SAML_IDP_CERT` to your IdP certificate
3. Set `SAML_ACS_URL` to `https://yourdomain.com/saml/acs`

### OAuth2
1. Register your app with the OAuth provider
2. Set `OAUTH_CLIENT_ID` and `OAUTH_CLIENT_SECRET`
3. Set `OAUTH_REDIRECT_URI`

## License

MIT — see [LICENSE](LICENSE)

---

**Built by [Alan Vo](https://github.com/ALANDVO)** | alanvo@gmail.com | AI, ML & Cybersecurity

[GitHub](https://github.com/ALANDVO/prompt-optimizer-alan-vo)
