# IF-M2: Runtime Identity and Observability Foundation

## Milestone Identity

- Milestone ID: IF-M2
- Project: IntentForge AI
- Phase: Phase 1
- Status: VERIFIED
- Closure Date: 2026-07-07

## Purpose

Establish the deterministic configuration, runtime identity, request correlation, and structured observability foundation required before introducing databases, authentication, external AI providers, background workers, or autonomous agents.

## Architecture Decision

This milestone implements:

- ADR-003: Configuration, Runtime Identity, and Observability Foundation

The milestone remains governed by the earlier project architecture decisions:

- ADR-001: Modular Monorepo
- ADR-002: Runtime and Technology Stack

## Implemented Capabilities

### Typed Configuration

IntentForge AI now provides:

- centralized typed settings;
- environment-aware configuration;
- validated API port boundaries;
- typed runtime environments;
- `.env` loading support;
- cached settings access;
- production-environment detection.

### Environment Contract

The active `.env.example` configuration is synchronized with the implemented Settings model.

Active runtime variables:

- `APP_NAME`
- `APP_VERSION`
- `APP_ENVIRONMENT`
- `APP_DEBUG`
- `API_HOST`
- `API_PORT`
- `LOG_LEVEL`

Future configuration remains explicitly separated as reserved and is not represented as currently implemented runtime behavior.

### Runtime Identity

The application exposes deterministic runtime metadata containing:

- application name;
- application version;
- environment;
- debug state.

The same settings source drives application metadata and health-response runtime identity.

### Request Correlation

Every request receives a correlation identifier.

The runtime:

- preserves valid caller-provided UUID correlation identifiers;
- replaces invalid identifiers;
- generates identifiers when none are supplied;
- stores the identifier in request state;
- exposes the identifier through request-scoped context;
- returns the identifier in the response header.

### Structured Logging

IntentForge AI emits structured JSON application logs containing:

- timestamp;
- severity;
- logger;
- message;
- correlation identifier;
- event metadata.

HTTP request lifecycle logging includes:

- `http_request_started`
- `http_request_completed`

Completion events also include:

- HTTP status code;
- request duration.

### Logging Ownership

The logging configuration preserves externally owned handlers.

IntentForge AI removes only previously installed IntentForge AI handlers before installing its marked JSON handler.

This behavior supports:

- test capture;
- host-process compatibility;
- repeatable logging configuration.

## Verification Summary

### Static Analysis

Result:

`All checks passed!`

### Automated Regression Suite

Result:

- 16 tests passed;
- 0 tests failed;
- 1 known dependency deprecation warning.

### Live Runtime Proof

A real Uvicorn ASGI server successfully handled:

`GET /api/v1/health`

Verified response:

- Status: 200
- Service: IntentForge AI
- Version: 0.1.0
- Environment: development
- Debug: true

### End-to-End Correlation Proof

Verified correlation identifier:

`ff367d02-4c49-4640-b89e-86dddb695904`

The same identifier was preserved across:

1. caller request header;
2. middleware validation;
3. request-scoped context;
4. structured request-start log;
5. structured request-completion log;
6. response header;
7. client-side equality verification.

Result:

`Correlation Match: True`

## Implementation Files

- `.env.example`
- `apps/api/pyproject.toml`
- `apps/api/requirements.lock`
- `apps/api/src/intentforge_api/core/config.py`
- `apps/api/src/intentforge_api/core/runtime.py`
- `apps/api/src/intentforge_api/core/correlation.py`
- `apps/api/src/intentforge_api/core/logging.py`
- `apps/api/src/intentforge_api/middleware/request_logging.py`
- `apps/api/src/intentforge_api/main.py`
- `apps/api/src/intentforge_api/api/routes/health.py`

## Test Files

- `apps/api/tests/test_config.py`
- `apps/api/tests/test_runtime.py`
- `apps/api/tests/test_correlation.py`
- `apps/api/tests/test_logging.py`
- `apps/api/tests/test_health.py`

## Evidence

- IF-P1-E002: Runtime Identity, Correlation, and Observability Verification

Evidence path:

`research/experiments/evidence/phase-1/IF-P1-E002-runtime-identity-correlation-observability.md`

## Known Non-Blocking Concern

The current test stack emits one Starlette deprecation warning related to the TestClient HTTPX compatibility path.

The warning does not affect runtime correctness or test success and is not an M2 closure blocker.

## Explicit Non-Goals

M2 does not introduce:

- PostgreSQL connectivity;
- Redis connectivity;
- authentication;
- authorization;
- distributed tracing;
- OpenTelemetry;
- external AI-provider integration;
- background workers;
- autonomous agents;
- sandbox execution.

These capabilities require separate milestone boundaries.

## Closure Decision

IF-M2 is VERIFIED.

The milestone has demonstrated:

- implementation completeness;
- static-analysis success;
- automated regression success;
- live ASGI execution;
- end-to-end request correlation;
- machine-readable structured logging;
- reproducible evidence.

IntentForge AI is now ready to proceed beyond the runtime-foundation milestone.
