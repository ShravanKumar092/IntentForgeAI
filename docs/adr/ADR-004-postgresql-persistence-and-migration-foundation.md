# ADR-004: PostgreSQL Persistence and Migration Foundation

## Status

Accepted

## Date

2026-07-08

## Context

IntentForge AI now requires a deterministic persistence boundary for future domain records, experiments, evidence, and stateful workflow data.

The persistence layer must support:

- asynchronous API access;
- explicit session ownership;
- controlled transaction boundaries;
- migration-based schema evolution;
- repository-level reproducibility;
- future domain-model expansion without structural rewrites.

The database foundation must not weaken the verified backend and observability baseline established in M1 and M2.

## Decision

IntentForge AI will use PostgreSQL as the authoritative relational persistence engine for the API boundary.

The persistence stack will use:

- SQLAlchemy 2.x for the ORM and database abstraction;
- asyncpg as the PostgreSQL async driver;
- Alembic as the schema migration authority;
- async SQLAlchemy engine and session primitives;
- explicit application-owned connection lifecycle management.

### Configuration Ownership

PostgreSQL configuration will remain centralized in the typed application settings model.

The API will consume:

- PostgreSQL host;
- PostgreSQL port;
- PostgreSQL database;
- PostgreSQL user;
- PostgreSQL password.

Database URLs will be derived centrally and must not be reconstructed ad hoc across modules.

### Metadata Ownership

Declarative model metadata will live in the database package and be exported as the authoritative Alembic target.

Application code must not create competing metadata registries.

### Session Ownership

The application will create a session factory explicitly from the managed engine.

Request handlers may acquire sessions through a bounded dependency helper.

Global mutable sessions are rejected.

### Migration Governance

Schema changes will be made through Alembic revisions.

The application will not auto-create or mutate tables during startup.

Migration scripts must import the authoritative metadata and settings-driven connection contract.

### Readiness Semantics

Liveness and readiness are distinct.

- `GET /api/v1/health` reports process liveness and runtime identity.
- `GET /api/v1/readiness` reports PostgreSQL availability.

Database failure must not break liveness.

### Test Strategy

The persistence boundary will be verified by:

- settings validation tests;
- engine derivation tests;
- session-factory tests;
- explicit database probe tests;
- readiness success and failure tests;
- health independence tests;
- Alembic environment verification;
- live PostgreSQL verification when infrastructure is available.

### Failure Behavior

If PostgreSQL is unavailable, the API should fail readiness explicitly and safely.

The API must not expose credentials or internal connection details in logs or client responses.

## Rejected Decisions

### Direct `psycopg` Calls in Business Logic

Rejected because database access must remain abstracted and testable.

### Automatic `create_all()` at Startup

Rejected because schema mutation must occur through migrations.

### Schema Mutation Outside Migrations

Rejected because it undermines determinism and traceability.

### Global Mutable Sessions

Rejected because they obscure ownership and lifecycle.

### Hidden Database Connectivity Inside Unrelated Modules

Rejected because readiness and persistence must be explicit.

### SQLite as the Production Persistence Contract

Rejected because the initial persistence boundary is PostgreSQL.

### Premature Repository Abstractions

Rejected because M3 only establishes infrastructure, not domain repositories.

## Consequences

### Positive

- deterministic PostgreSQL boundary;
- explicit session lifecycle;
- migration-controlled schema evolution;
- readiness visibility;
- future domain expansion with a stable base.

### Negative

- more infrastructure code;
- more operational steps during local development;
- migration discipline becomes mandatory.

## Governance Rule

Any major change to the PostgreSQL contract, SQLAlchemy usage, async session ownership, or migration strategy requires a new architecture decision record.
