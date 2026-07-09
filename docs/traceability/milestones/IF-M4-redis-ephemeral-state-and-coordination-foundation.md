# IF-M4 — Redis Ephemeral State and Coordination Foundation

## Status

VERIFIED

## Purpose

Establish a minimal, production-grade Redis boundary for ephemeral state and coordination while keeping PostgreSQL as the durable system of record.

## Governing ADRs

- ADR-001 — Modular Monorepo Architecture
- ADR-002 — Runtime and Technology Stack
- ADR-003 — Configuration, Runtime Identity, and Observability Foundation
- ADR-004 — PostgreSQL Persistence and Migration Foundation
- ADR-005 — Redis Ephemeral State and Coordination Foundation

## Implemented Capabilities

- Centralized typed Redis settings in the API configuration model.
- Async Redis client construction from centralized settings.
- Redis client lifecycle ownership through the FastAPI lifespan.
- Explicit Redis connectivity probing via `PING`.
- Readiness aggregation across PostgreSQL and Redis.
- Deterministic Redis key namespace helper.
- Docker Compose Redis service for local verification.

## Redis Role

Redis is approved for ephemeral and operational state only:

- short-lived caches;
- idempotency records;
- temporary execution state;
- distributed coordination;
- rate-limit counters when explicitly required;
- future queue or worker coordination where separately approved.

Redis is not the authoritative durable store.

## PostgreSQL / Redis Boundary

- PostgreSQL remains the durable system of record.
- Redis is reconstructable, time-bound, and coordination-oriented.
- Redis must not replace PostgreSQL for core records or evidence.

## Configuration Contract

The API consumes:

- Redis host
- Redis port
- Redis database index
- Redis connection timeout

Redis settings are owned centrally and are not reconstructed in routes or probes.

## Client Lifecycle

- Client construction is centralized.
- Connection pooling is managed by the Redis client.
- The application owns client shutdown.
- Routes and probes consume the managed client through application state.

## Readiness Architecture

- `GET /api/v1/health` remains a liveness endpoint.
- `GET /api/v1/readiness` aggregates PostgreSQL and Redis availability.
- Readiness returns `200` only when both dependencies are available.
- Readiness returns a controlled `503` when either dependency is unavailable.

## Key Namespace Contract

Redis keys use a deterministic application-owned prefix:

`intentforge:<environment>:<capability>:<identifier>`

No domain keys are introduced by this milestone.

## Tests

- Redis settings validation tests.
- Redis client construction tests.
- Redis key namespace tests.
- Redis PING probe tests.
- Readiness success and failure tests.
- Health independence regression tests.
- PostgreSQL regression tests.

## Real Integration Verification

- PostgreSQL and Redis started successfully through Docker Compose.
- Redis healthcheck passed.
- PostgreSQL healthcheck passed.
- The API started successfully against both services.
- `GET /api/v1/health` returned `200`.
- `GET /api/v1/readiness` returned `200` when both services were healthy.
- Caller correlation IDs were preserved in responses.
- Structured request-start and request-completion logs carried the same correlation ID.

## Failure Verification

- Redis was stopped while PostgreSQL and the API remained controlled.
- `GET /api/v1/health` remained `200`.
- `GET /api/v1/readiness` returned `503`.
- The controlled failure payload was:

  `{"status":"unavailable","database":"available","redis":"unavailable","timestamp":"2026-07-09T08:38:33.133848+00:00"}`

- Redis was restarted and readiness recovered to `200`.

## Evidence Mapping

- `IF-P1-E004`

## Non-Goals

- Authentication
- JWT storage
- Domain caching
- Background workers
- Job queues
- Agents
- AI providers
- Embeddings
- Vector databases
- Frontend integration

## Known Limitations

- The current Redis namespace helper establishes the key contract only; no real business keys are introduced.
- Local verification uses temporary Docker Compose services on ports `55433` and `56379`.

## Deferred Warning

- The Starlette/TestClient `httpx2` deprecation warning remains external to M4.

## Closure Criteria

This milestone is marked `VERIFIED` because:

- Python 3.12 was verified;
- Redis ADR-005 was accepted;
- typed Redis configuration was implemented;
- `.env.example` was synchronized;
- async Redis client ownership was implemented;
- application lifespan manages Redis shutdown;
- Redis connectivity probing is implemented;
- readiness aggregates PostgreSQL and Redis;
- liveness remains independent;
- deterministic unit tests pass;
- M1–M3 regressions pass;
- Ruff passes;
- real Redis PING succeeded;
- real PostgreSQL readiness succeeded;
- aggregate readiness succeeded;
- Redis failure was controlled;
- evidence `IF-P1-E004` exists;
- this milestone closure document exists;
- changelog and traceability registry were updated;
- implementation and traceability commits were pushed.
