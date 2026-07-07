# Changelog

All significant changes to IntentForge AI are documented in this file.

## [Unreleased]

### Added

- Day 1 closure document `docs/traceability/closures/IF-D1-day-1-closure.md`.
- Day 1 closure evidence record `IF-P1-E003`.
- Day 1 closure registry entry in `research/traceability/registry.json`.
- Repository documentation aligned with the verified backend state.
- Explicit line-ending policy through `.gitattributes`.
- Apache 2.0 licensing for the repository.

### Verification

- Confirmed the official Python 3.12.10 virtual environment.
- Confirmed package import and application import.
- Verified Ruff static analysis passes.
- Verified the 16-test backend regression suite passes.
- Verified the remote repository is synchronized with local `main`.

## [0.1.0] — 2026-07-07

### Added

- IntentForge AI repository initialized.
- Official remote repository connected.
- Phase 1 backend foundation established and verified.

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

- Accepted ADR-001: Modular Monorepo Architecture.
- Accepted ADR-002: Runtime and Technology Stack.
- Accepted ADR-003: Configuration, Runtime Identity, and Observability Foundation.
