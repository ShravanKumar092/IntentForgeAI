# Changelog

All significant changes to IntentForge AI will be documented in this file.

## [Unreleased]

### Added

- Initial repository foundation.
- Project governance structure.
- Initial Project Constitution.
- Environment contract.
- Repository ignore rules.
- Research and engineering directory structure.

### Runtime Foundation

- Added centralized typed configuration using Pydantic Settings.
- Added validated runtime environments and API port boundaries.
- Synchronized the active `.env.example` contract with implemented runtime settings.
- Added deterministic runtime identity for application name, version, environment, and debug state.
- Added request correlation with UUID validation, generation, request context, and response propagation.
- Added structured JSON application logging.
- Added HTTP request-start and request-completion lifecycle events.
- Added correlation-aware request logging with status code and duration metadata.
- Preserved externally owned logging handlers while managing IntentForge AI handlers safely.
- Extended the health endpoint with runtime identity metadata.

### Verification

- Added configuration, runtime, correlation, logging, and health regression tests.
- Verified all 16 automated tests pass.
- Verified Ruff static analysis passes.
- Verified the active environment contract against the typed Settings model.
- Verified the API through a live Uvicorn ASGI runtime.
- Verified end-to-end correlation identity across request header, request context, structured logs, response header, and client comparison.
- Added evidence record `IF-P1-E002`.
- Closed milestone `IF-M2` as `VERIFIED`.

### Architecture

- Accepted ADR-003: Configuration, Runtime Identity, and Observability Foundation.

## [0.0.1] — 2026-07-07

### Added

- IntentForge AI repository initialized.
- Official remote repository connected.
- Phase 0 execution started.

### Architecture

- Accepted ADR-002: Runtime and Technology Stack.
- Locked Python 3.12 as the official backend runtime.
- Locked Node.js 22 LTS as the frontend runtime family.
- Selected FastAPI, React, TypeScript, PostgreSQL, Redis, and Docker.
- Rejected premature microservices and a dedicated graph database for the initial implementation.
- Added the machine-readable runtime contract.
