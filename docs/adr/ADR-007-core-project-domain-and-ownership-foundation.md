# ADR-007: Core Project Domain and Ownership Foundation

## Status

Proposed

## Context

IntentForge AI now has verified infrastructure for runtime identity, PostgreSQL persistence, Redis coordination, and authenticated user identity. The first product-domain boundary must establish a durable Project aggregate owned by an authenticated identity without introducing speculative collaboration or generic CRUD abstractions.

## Decision

### Project as the Primary Domain Boundary

Project is the first durable product-domain aggregate in IntentForge AI.

Future project-scoped capabilities must attach to a verified Project boundary rather than creating disconnected global resources.

### Aggregate Ownership

- The authenticated creator becomes the project owner.
- Ownership is assigned server-side.
- Callers cannot submit arbitrary `owner_id` values.
- Ownership transfer is deferred until a later milestone proves a real need.

### Identifier Strategy

Project uses the repository's established UUID strategy.

- Identifiers are immutable.
- Identifiers are stable.
- Identifiers are safe for API routing.

### Project Lifecycle

M6 establishes a minimal lifecycle contract with an active project state.

Archive behavior is deferred until a later milestone.

### Authorization Model

Project authorization is resource-based.

The server verifies:

`authenticated principal -> requested project -> ownership permission`

To avoid resource enumeration, unauthorized access to another user's project returns `404 Not Found` rather than `403 Forbidden`.

### Data Access Boundary

The Project repository is responsible for:

- create;
- find owned by ID;
- list owned projects;
- persist controlled updates.

### Service Boundary

The Project service is responsible for:

- server-side ownership assignment;
- owned project creation;
- owned project lookup;
- owner-scoped listing;
- controlled update;
- explicit transaction ownership;
- safe domain logging.

### Domain Logging

Project events may log:

- project ID;
- authenticated internal user ID;
- event;
- outcome;
- correlation ID.

Sensitive project content must not be logged.

### Rejected Alternatives

- caller-supplied ownership;
- global unauthenticated projects;
- route handlers directly implementing persistence logic;
- authorization checks duplicated across endpoints;
- generic CRUD abstractions;
- speculative organization or team architecture;
- hard deletion without explicit lifecycle governance;
- exposing all projects globally;
- relying only on opaque identifiers as authorization.

## Consequences

- The application gains a clean first product-domain boundary.
- Future project-scoped capabilities can reuse a consistent ownership and authorization model.
- Archive and richer lifecycle management remain available for later work without being rushed into M6.
