# ADR-005: Redis Ephemeral State and Coordination Foundation

## Status

Accepted

## Date

2026-07-09

## Context

IntentForge AI requires a dedicated Redis boundary for ephemeral state and coordination while PostgreSQL remains the authoritative durable relational store.

The repository already established:

- centralized typed configuration;
- application-owned lifecycle management;
- PostgreSQL persistence governance;
- liveness/readiness separation;
- evidence-governed traceability.

Redis must fit inside that architecture without becoming a second source of truth.

## Decision

IntentForge AI will use Redis for ephemeral, reconstructable, time-bound, operational state only.

Approved Redis uses include:

- short-lived caches;
- idempotency records;
- temporary execution state;
- distributed coordination;
- future queue or worker coordination where separately approved;
- rate-limit counters when explicitly required.

Redis is not:

- the durable system of record;
- a replacement for PostgreSQL;
- a permanent audit store;
- a permanent evidence store;
- a hidden business-domain database.

## Client Strategy

The API will use the official asynchronous Redis client from the `redis` package.

Client ownership rules:

- client construction is centralized;
- connection pooling is managed by the client;
- the application owns lifecycle shutdown;
- routes do not construct clients directly;
- connectivity is verified through explicit probing.

## Configuration Ownership

All Redis settings must remain centralized in the typed Settings model.

Redis configuration must not be reconstructed ad hoc in routes, probes, or business modules.

## Failure Semantics

- API liveness must remain independent of Redis.
- Readiness may depend on Redis when Redis is required by the active runtime.
- Redis failures must surface as controlled readiness failures.
- No Redis credentials or internal exception details may leak to API clients.

## Key Governance

Redis keys will use an application-owned namespace with environment isolation.

Preferred form:

`intentforge:<environment>:<capability>:<identifier>`

Only the naming contract is established here.
No domain keys are introduced by this ADR.

## Serialization Governance

Arbitrary Python object serialization is prohibited.

`pickle` is rejected.

Future Redis values must use explicit, safe serialization contracts.

## TTL Governance

Ephemeral records should use explicit expiry when their semantics require it.

Permanent Redis records are not the default.

## Rejected Alternatives

- direct Redis client construction across modules;
- Redis as the primary durable database;
- unbounded cache entries;
- arbitrary `pickle` serialization;
- hard-coded connection strings;
- Redis calls hidden inside unrelated business modules;
- premature worker or queue frameworks;
- fake domain cache implementations solely for verification.

## Consequences

### Positive

- explicit Redis ownership;
- deterministic client lifecycle;
- readiness visibility;
- safe namespace governance;
- future coordination features have a stable boundary.

### Negative

- more infrastructure code;
- more local development setup;
- readiness behavior becomes multi-infrastructure aware.

## Governance Rule

Any major change to Redis role, client strategy, configuration ownership, serialization policy, or readiness semantics requires a new ADR.
