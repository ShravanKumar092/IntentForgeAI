# IF-M3 — PostgreSQL Persistence Foundation

## Status

VERIFIED

## Purpose

Establish a deterministic, migration-controlled PostgreSQL persistence boundary for IntentForge AI.

## Governing ADRs

- ADR-001 — Modular Monorepo Architecture
- ADR-002 — Runtime and Technology Stack
- ADR-003 — Configuration, Runtime Identity, and Observability Foundation
- ADR-004 — PostgreSQL Persistence and Migration Foundation

## Implemented Capabilities

- Centralized typed PostgreSQL settings in the API configuration model.
- Async SQLAlchemy 2.x engine and session factory ownership in the API boundary.
- Declarative database metadata under the API database package.
- Alembic migration environment bound to the centralized settings and metadata.
- Explicit database connectivity probe for readiness checks.
- `GET /api/v1/readiness` for PostgreSQL availability.
- Docker Compose PostgreSQL service for local verification.

## Configuration Contract

The API consumes:

- PostgreSQL host
- PostgreSQL port
- PostgreSQL database
- PostgreSQL user
- PostgreSQL password

Database URLs are derived centrally from settings and are not rebuilt ad hoc.

## Database Architecture

- PostgreSQL is the authoritative relational persistence engine.
- SQLAlchemy 2.x provides ORM and database abstraction.
- asyncpg provides the PostgreSQL async driver.
- Engine creation is explicit and application-owned.
- Session creation is explicit and request-scoped.
- Global mutable sessions are rejected.

## Migration Architecture

- Alembic is the schema migration authority.
- Migration configuration reads from centralized application settings.
- Migration scripts target the authoritative SQLAlchemy metadata.
- Automatic `create_all()` at startup is rejected.

## Health / Readiness Distinction

- `GET /api/v1/health` remains a liveness endpoint.
- `GET /api/v1/readiness` reports database availability.
- Database unavailability must not break liveness.

## Tests

- Configuration validation tests.
- Database engine and session-factory tests.
- Database probe success and failure tests.
- Readiness success and failure tests.
- Health independence tests.

## Live Verification

- PostgreSQL container verified healthy through Docker Compose.
- `GET /api/v1/health` returned `200` while PostgreSQL was available.
- `GET /api/v1/readiness` returned `200` while PostgreSQL was available.
- `GET /api/v1/readiness` returned `503` while PostgreSQL was stopped.
- Correlation IDs matched on request, response, and structured request logs.

## Evidence Mapping

- `IF-P1-E003`

## Non-Goals

- Authentication
- Users
- Domain repositories
- Agents
- AI provider integration
- Redis
- Frontend work
- Production deployment infrastructure

## Known Limitations

- Local verification uses a temporary Docker Compose PostgreSQL container on port `55432`.
- A separate deployment or orchestration decision may be needed for future environments.

## Closure Criteria

This milestone can be marked `VERIFIED` when:

- unit tests pass;
- Ruff passes;
- Alembic configuration is validated;
- a real PostgreSQL instance is verified;
- readiness succeeds against the running database;
- health remains independent of database availability;
- evidence `IF-P1-E003` is completed;
- traceability registry is updated with the implementation commit.
