# IF-M6 — Core Project Domain and Ownership Foundation

## Status

VERIFIED

## Purpose

Establish the first durable project aggregate for IntentForge AI, including owner-scoped project persistence, project lifecycle metadata, project-scoped authorization, and safe project CRUD boundaries.

## Governing ADRs

- ADR-001 — Modular Monorepo Architecture
- ADR-002 — Runtime and Technology Stack
- ADR-003 — Configuration, Runtime Identity, and Observability Foundation
- ADR-004 — PostgreSQL Persistence and Migration Foundation
- ADR-005 — Redis Ephemeral State and Coordination Foundation
- ADR-006 — Security, Identity, and Authentication Foundation
- ADR-007 — Core Project Domain and Ownership Foundation

## Domain Model

- `Project` is the durable project aggregate.
- Each `Project` belongs to an authenticated `User` owner.
- Projects include a name, lifecycle status, created timestamp, and updated timestamp.
- Project access is strictly owner-scoped.

## Authorization Model

- All project operations require authentication.
- Project authorization is inherited from verified project ownership.
- Unauthorized project access is intentionally disguised as `404 Not Found`.

## Project Lifecycle

- Projects support stable lifecycle status values.
- The initial lifecycle status is `active`.
- Project names are normalized and validated.

## Persistence

- Projects are persisted in PostgreSQL.
- Owner-scoped project queries are indexed by `owner_id`.
- Model constraints enforce lifecycle values and project ownership.

## Tests

- Project model validation and lifecycle defaults.
- Project repository persistence and query behavior.
- Project service ownership and update semantics.
- Project API route contracts for create, read, list, update, and `404` semantics.

## Live Verification

- Project API routes respect authenticated project ownership.
- Project persistence is implemented through SQLAlchemy and Alembic.
- Project lifecycle metadata is durable and queryable.

## Evidence Mapping

- IF-P1-E006

## Non-Goals

- Project collaboration, memberships, or shared workspaces.
- Project requirements or intent management.
- Project roles, teams, organizations, or RBAC.
- Status transitions beyond the initial `active` lifecycle support.
- AI-generated project content.

## Known Limitations

- Project lifecycle semantics are limited to `active` by default.
- Project authorization is owner-only.

## Closure Criteria

This milestone is marked `VERIFIED` because:

- `ADR-007` is accepted;
- project persistence is implemented;
- owner-scoped project authorization is implemented;
- project lifecycle metadata is persisted;
- project CRUD routes are implemented;
- project ownership is enforced through service-level authorization;
- unauthorized access returns `404` semantics;
- new project tests are present;
- evidence IF-P1-E006 exists.
