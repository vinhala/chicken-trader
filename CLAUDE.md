# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered daily investment opportunity platform. News articles are ingested, clustered into events, and OpenAI generates investment reports with ticker suggestions. Users follow "theses" which get lifecycle states (Active → Hold → Warning → Sell). "Sell" is terminal — it stops re-evaluation. Further details are explainged in the SPEC.md file.

## Architecture

**Full-stack monorepo:**
- `backend/` — Python FastAPI + SQLAlchemy + Celery + PostgreSQL + Redis
- `frontend/` — Vue 3 + TypeScript + Vite + Pinia + Tailwind CSS
- `infrastructure/` — Docker Compose files for Docker Swarm deployment
- `ops/` — Deployment runbooks

**Backend structure:**
- `backend/app/main.py` — FastAPI app entry point; registers all routers, runs startup tasks
- `backend/app/core/config.py` — Pydantic settings singleton; reads from `.env`
- `backend/app/models/entities.py` — All SQLAlchemy ORM models
- `backend/app/api/` — API route handlers (auth, opportunities, theses, notifications)
- `backend/app/services/` — Business logic (report generation, thesis evaluation, news ingestion, notifications)
- `backend/app/workers/` — Celery tasks and beat schedule (news every 6h, thesis re-eval daily)
- `backend/alembic/` — Database migrations

**Frontend structure:**
- `frontend/src/main.ts` — App bootstrap (Vue + Pinia + Router)
- `frontend/src/router/index.ts` — Routes with auth guard
- `frontend/src/stores/` — Pinia stores
- `frontend/src/views/` — Page components
- `frontend/src/components/` — Shared components

**Key data flow:** NewsAPI → article ingestion → event clustering → OpenAI report generation → `ReportAsset` rows (tickers) → user follows thesis → daily Celery re-evaluation → `ThesisEvaluation` state changes → notifications

## Development Commands

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload      # Dev server on :8000
pytest                              # All tests
pytest tests/test_auth_consent.py  # Single test file
alembic upgrade head               # Apply migrations
alembic revision --autogenerate -m "description"  # New migration
```

### Frontend
```bash
cd frontend
npm install
npm run dev      # Dev server on :5173
npm run build    # Production build
npm run preview  # Preview production build
```

### Docker / Full Stack
```bash
make build-local    # Build Docker images
make deploy-local   # Deploy to Docker Swarm (app.localhost, api.localhost)
make deploy-prod    # Deploy to production (set APP_HOST, API_HOST env vars)
make down           # Stop all services
```

## Environment Setup

Copy `.env.example` to `.env` in the project root. Required keys:
- `SECRET_KEY` — JWT signing secret
- `NEWS_API_KEY` — NewsAPI.org key
- `OPENAI_API_KEY` — OpenAI API key
- `MARKET_API_KEY` — Finnhub key
- Postgres and Redis connection details

## Testing

Tests use pytest with an in-memory SQLite database (configured in `backend/tests/conftest.py`). The `db_session` fixture auto-creates all tables. No frontend tests currently exist.

## Key Conventions

- Thesis `Sell` state is **terminal**: once set, re-evaluation stops permanently
- All users must accept a disclaimer (`DisclaimerConsent`) before accessing the app
- Articles are deduplicated via `dedup_hash` on ingest
- `VITE_API_BASE_URL` defaults to `/api`; the Caddy reverse proxy routes `/api` to the FastAPI backend
