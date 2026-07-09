# IF-M8 — Source and Evidence Provenance Foundation

## Status

PENDING

## Purpose

Capture durable provenance for project sources and evidence, and connect evidence to requirements through explicit relationship links.

## Governing ADRs

- ADR-001 — Modular Monorepo Architecture
- ADR-002 — Runtime and Technology Stack
- ADR-003 — Configuration, Runtime Identity, and Observability Foundation
- ADR-004 — PostgreSQL Persistence and Migration Foundation
- ADR-005 — Redis Ephemeral State and Coordination Foundation
- ADR-006 — Security, Identity, and Authentication Foundation
- ADR-007 — Core Project Domain and Ownership Foundation
- ADR-008 — Source and Evidence Provenance Foundation

## Domain Model

- `Source` captures project-owned provenance sources such as documents, transcripts, and references.
- `Evidence` captures source-derived claims or observations that support requirement decisions.
- `EvidenceRequirementLink` captures the relationship between evidence and requirements, including types like `supports`, `contradicts`, and `contextualizes`.
- All provenance records are owned by the same project entity and stored in PostgreSQL.

## Authorization Model

- All provenance operations require authentication.
- Project ownership is verified before reading or mutating source, evidence, or evidence link records.
- Unauthorized or missing project access returns `404 Not Found` to avoid leaking cross-project data.

## Persistence

- `sources` stores source metadata and ownership.
- `evidence` stores evidence claims with optional source excerpt and location data.
- `evidence_requirement_links` stores typed relationships between evidence and requirements.

## API Surface

- `GET /api/v1/projects/{project_id}/sources`
- `POST /api/v1/projects/{project_id}/sources`
- `GET /api/v1/projects/{project_id}/evidence`
- `POST /api/v1/projects/{project_id}/evidence`
- `GET /api/v1/projects/{project_id}/evidence/{evidence_id}/requirements`
- `POST /api/v1/projects/{project_id}/evidence/{evidence_id}/requirements`
- `GET /api/v1/projects/{project_id}/requirements/{requirement_id}/evidence`

## Tests

- Provenance repository persistence and project scoping.
- Provenance service authorization, creation, update, and relationship handling.
- Provenance API routes and request/response contract validation.

## Evidence Mapping

- IF-P1-E008

## Closure Criteria

This milestone will be marked VERIFIED when:

- source, evidence, and evidence requirement relationship persistence is implemented;
- project ownership is enforced for all provenance endpoints;
- provenance routes exist and expose validated contracts;
- repository, service, and route behavior are covered by tests.
