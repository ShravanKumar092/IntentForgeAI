# ADR-008: Source and Evidence Provenance Foundation

## Status

Proposed

## Context

IntentForge AI needs to capture not only project intent and requirements, but also the source and evidence that validate requirement claims. This provenance data must remain owned by a project and be traceable through relationships between sources, evidence items, and requirements.

## Decision

We will introduce a provenance foundation with three new domain concepts:

- `Source`: an original artifact or source of truth, such as a document, conversation, benchmark, or external reference.
- `Evidence`: an instance of a claim, observation, or excerpt derived from a source.
- `EvidenceRequirementLink`: a typed relationship linking evidence to a requirement, representing how the evidence supports, contradicts, or contextualizes the requirement.

The design uses a project-owned boundary for all provenance entities. Each provenance record must be associated with the owning project and enforced through service authorization.

## Consequences

- The API surface expands with project-scoped provenance endpoints.
- Provenance entities are persisted in PostgreSQL with explicit project ownership.
- Evidence links to existing requirements are modeled as first-class relationship records.
- This foundation enables future workflows for auditability, traceability, and trace-based validation of requirements.
- Ownership enforcement reduces risk of cross-project data leakage.

## Related

- ADR-001 — Modular Monorepo Architecture
- ADR-002 — Runtime and Technology Stack
- ADR-003 — Configuration, Runtime Identity, and Observability Foundation
- ADR-004 — PostgreSQL Persistence and Migration Foundation
- ADR-005 — Redis Ephemeral State and Coordination Foundation
- ADR-006 — Security, Identity, and Authentication Foundation
- ADR-007 — Core Project Domain and Ownership Foundation
