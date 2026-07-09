# IF-M7 — Project Intent and Requirement Foundation

## Status

VERIFIED

## Purpose

Extend the owned Project aggregate to capture project intent and durable requirements records within the existing project boundary.

## Governing ADRs

- ADR-001 — Modular Monorepo Architecture
- ADR-002 — Runtime and Technology Stack
- ADR-003 — Configuration, Runtime Identity, and Observability Foundation
- ADR-004 — PostgreSQL Persistence and Migration Foundation
- ADR-005 — Redis Ephemeral State and Coordination Foundation
- ADR-006 — Security, Identity, and Authentication Foundation
- ADR-007 — Core Project Domain and Ownership Foundation

## Domain Model

- `ProjectIntent` captures the problem statement, desired outcome, goals, non-goals, constraints, and success criteria for a project.
- `Requirement` captures project-scoped requirement details with classification, priority, and lifecycle status.
- Intents and requirements are persisted in PostgreSQL and owned by the same authenticated project owner.

## Authorization Model

- All intent and requirement operations require authentication.
- Project ownership is verified before reading or mutating project intent and requirements.
- Missing or unauthorized access is returned as `404 Not Found` to avoid leaking ownership boundaries.

## Persistence

- Project intents are stored in `project_intents` with a unique `project_id` constraint.
- Requirements are stored in `requirements` and indexed by `project_id`.
- Lifecycle defaults are enforced at the database and application layer.

## API Surface

- `GET /api/v1/projects/{project_id}/intent`
- `POST /api/v1/projects/{project_id}/intent`
- `GET /api/v1/projects/{project_id}/requirements`
- `POST /api/v1/projects/{project_id}/requirements`
- `GET /api/v1/projects/{project_id}/requirements/{requirement_id}`
- `PATCH /api/v1/projects/{project_id}/requirements/{requirement_id}`

## Tests

- Project intent and requirement domain models.
- Project repository persistence and query behavior for intents and requirements.
- Project service authorization and stateful upsert/update semantics.
- Project API route contracts for intent and requirement management.

## Live Verification

- The API exposes project-scoped intent and requirement endpoints.
- Requests are authorized through project ownership.
- Project intent and requirements use durable SQL persistence.

## Evidence Mapping

- IF-P1-E007

## Non-Goals

- Full requirement workflow orchestration.
- Team/organization membership or cross-project collaboration.
- AI-driven requirement generation.
- Advanced requirement dependency modeling.

## Closure Criteria

This milestone is marked VERIFIED because:

- project intent persistence is implemented;
- project requirement persistence is implemented;
- project ownership is enforced for intent and requirement routes;
- intent and requirement routes exist and return validated API contracts;
- repository and service methods are implemented and tested;
- new evidence IF-P1-E007 exists.
