# ADR-003: Configuration, Runtime Identity, and Observability Foundation

## Status

Accepted

## Date

2026-07-07

## Context

IntentForge AI will eventually contain multiple intelligence, engineering, evidence, and execution capabilities.

The system requires a consistent way to:

- load configuration;
- distinguish environments;
- validate required settings;
- expose runtime identity;
- correlate requests;
- generate structured logs;
- diagnose failures;
- preserve operational evidence.

Configuration and observability must be established before databases, authentication, AI providers, background workers, or autonomous agents are introduced.

## Decision

IntentForge AI will establish a centralized runtime foundation.

### Typed Configuration

Application settings will be represented through validated typed models.

Environment variables will remain the external configuration boundary.

The application must not read environment variables directly throughout business logic.

### Environment Loading

Local development may load values from a `.env` file.

Real secrets must never be committed.

`.env.example` remains the documented environment contract.

### Runtime Identity

Every running API instance will expose a runtime identity containing:

- application name;
- application version;
- environment;
- debug state.

Future versions may extend this identity with:

- build commit;
- deployment identifier;
- instance identifier.

### Startup Validation

Invalid configuration must fail early during application startup or settings construction.

The system must prefer explicit startup failure over delayed runtime failure.

### Request Correlation

Every HTTP request will receive a correlation identifier.

If a valid caller-provided correlation identifier exists, the application may preserve it.

Otherwise, the application will generate one.

The identifier will be returned in the response.

### Structured Logging

Application logs will use structured JSON records.

The initial log contract will support:

- timestamp;
- severity;
- logger;
- message;
- correlation identifier;
- event fields.

### Configuration Access

Settings will be created through a centralized cached provider.

Application modules must not independently construct competing configuration objects.

## Initial Implementation Scope

M2 will implement:

- typed settings;
- `.env` loading;
- runtime identity;
- startup validation;
- request correlation middleware;
- structured JSON logging;
- health-response runtime metadata;
- automated tests;
- live verification;
- evidence records.

## Non-Goals

M2 will not implement:

- PostgreSQL connectivity;
- Redis connectivity;
- authentication;
- distributed tracing;
- external log aggregation;
- OpenTelemetry;
- AI-provider configuration;
- secrets-management infrastructure.

These capabilities will be introduced only when their milestone requires them.

## Consequences

### Positive

- deterministic configuration;
- early configuration failure;
- consistent runtime identity;
- request-level traceability;
- machine-readable logs;
- stronger debugging foundations;
- better future evidence collection.

### Negative

- additional middleware and configuration complexity;
- logging contracts must remain stable;
- correlation context must be carefully managed.

## Rejected Decisions

### Direct `os.environ` Access Across Modules

Rejected because configuration access would become fragmented and difficult to validate.

### Plain Text Logging as the Primary Contract

Rejected because future agents, experiments, and operational evidence require machine-readable events.

### Database or Redis Integration in M2

Rejected because runtime identity and configuration must be verified independently before external infrastructure is introduced.

## Governance Rule

Any major change to configuration ownership, runtime identity, request correlation, or logging format requires an Architecture Decision Record.