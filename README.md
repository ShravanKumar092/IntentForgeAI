# IntentForge AI

> From Raw Idea to Verified Project.

IntentForge AI is an evidence-governed project intelligence and engineering platform.

The repository currently contains a verified Day 1 backend foundation and a verified PostgreSQL persistence foundation:

- modular monorepo structure;
- FastAPI API under `apps/api`;
- typed runtime configuration;
- runtime identity and correlation handling;
- structured request logging;
- health and readiness endpoints;
- PostgreSQL persistence scaffolding and regression tests.

## Current State

Phase 1 is active.

Day 1 is complete for the verified backend foundation and runtime observability baseline.
M3 is complete for the PostgreSQL persistence foundation.

## Runtime Contract

The official backend runtime is:

- Python 3.12;
- FastAPI;
- PostgreSQL;
- Redis;
- Docker and Docker Compose.

The broader project stack also targets:

- Node.js 22;
- Java 17;
- React;
- TypeScript;
- Vite.

## Backend Setup

From `apps/api`:

1. Create or activate the official virtual environment at `apps/api/.venv`.
2. Install dependencies with `.\.venv\Scripts\python.exe -m pip install -e .[dev]`.
3. Run linting with `.\.venv\Scripts\python.exe -m ruff check .`.
4. Run tests with `.\.venv\Scripts\python.exe -m pytest tests -v`.
5. Start PostgreSQL locally with `docker compose -f ..\..\compose.yml up -d postgres` when validating M3.

## Local Run

Start the API from `apps/api` with:

```powershell
.\.venv\Scripts\python.exe -m uvicorn intentforge_api.main:app --host 127.0.0.1 --port 8010 --reload
```

## Verification

- Health endpoint: `GET /api/v1/health`
- Readiness endpoint: `GET /api/v1/readiness`
- OpenAPI docs: `http://127.0.0.1:8010/docs`
- ReDoc: `http://127.0.0.1:8010/redoc`

## Project Structure

- `apps/api` - verified FastAPI backend.
- `docs/adr` - architecture decisions.
- `docs/traceability` - milestone and closure records.
- `research/experiments/evidence` - evidence records.
- `research/traceability` - registry data.

## Development Notes

Use the official Python executable at `apps/api/.venv/Scripts/python.exe` for all backend work.

The shell default `python` command may point to a different installation and should not be used for verification.
