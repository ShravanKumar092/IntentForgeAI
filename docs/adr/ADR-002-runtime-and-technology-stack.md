# ADR-002: Runtime and Technology Stack

## Status

Accepted

## Date

2026-07-07

## Context

IntentForge AI requires a technology foundation capable of supporting:

- asynchronous APIs;
- AI and machine learning workflows;
- evidence retrieval;
- graph-based traceability;
- multi-agent orchestration;
- isolated code execution;
- real-time development interfaces;
- long-running background jobs;
- reproducible research experiments.

The project must remain suitable for both academic research and production-oriented software engineering.

## Decision

IntentForge AI will use the following initial runtime architecture.

### Backend Runtime

Python 3.12

Primary responsibilities:

- API services;
- AI workflows;
- research intelligence;
- evidence processing;
- agent orchestration;
- evaluation;
- experimentation.

Python 3.13 installed on the development machine will remain available but will not be the official project runtime.

### Backend Framework

FastAPI

Primary responsibilities:

- REST APIs;
- asynchronous endpoints;
- lifecycle services;
- project management APIs;
- AI execution APIs;
- streaming interfaces where required.

### Frontend Runtime

Node.js 22 LTS

### Frontend Stack

React  
TypeScript  
Vite

Primary responsibilities:

- project workspace;
- idea intelligence interface;
- research views;
- graph exploration;
- development studio;
- evidence inspection;
- autonomous execution monitoring.

### Primary Relational Database

PostgreSQL

Primary responsibilities:

- users;
- projects;
- lifecycle state;
- project constitutions;
- tasks;
- agent runs;
- approvals;
- structured metadata.

### Background and Runtime State

Redis

Primary responsibilities:

- background job coordination;
- caching;
- temporary runtime state;
- event distribution where required.

Redis is not the permanent source of truth.

### Traceability Storage

The Intent-to-Evidence Graph will initially be implemented behind a storage abstraction.

The first implementation may use PostgreSQL-backed graph relationships.

A dedicated graph database may be introduced only if experiments or query complexity justify it.

### Containerization

Docker and Docker Compose

Primary responsibilities:

- local infrastructure;
- reproducible services;
- isolated dependencies;
- controlled execution environments;
- research reproducibility.

### Java Runtime

OpenJDK 17 LTS will remain available for future tools that require a JVM.

Java is not part of the initial application runtime.

## Version Policy

The project will distinguish between:

1. development machine versions;
2. officially supported project runtime versions;
3. container-pinned service versions.

Exact dependency versions will be locked in dependency manifests and updated deliberately.

## Architectural Principle

A technology must not be added because it is popular.

Every major technology must justify at least one of:

- a system requirement;
- a research requirement;
- an evaluation requirement;
- a reproducibility requirement.

## Consequences

### Positive

- stable AI and Python ecosystem compatibility;
- modern frontend development;
- clear storage responsibilities;
- reproducible infrastructure;
- controlled future evolution.

### Negative

- multiple runtime technologies increase operational complexity;
- Docker will become necessary for full local development;
- service boundaries must be carefully controlled.

## Rejected Decisions

### Python 3.13 as the official initial runtime

Rejected for the initial project runtime because the project will depend on a broad AI, research, evaluation, and systems ecosystem. Python 3.12 provides a more conservative compatibility target.

### Dedicated Graph Database from Day 1

Rejected because the graph model should first prove its research and query requirements before introducing another infrastructure dependency.

### Microservices from Day 1

Rejected because premature service separation would increase operational complexity before module boundaries are validated.

The initial backend will use a modular architecture with explicit boundaries and may extract services later when justified.

## Governance Rule

Any change to a primary runtime, database, framework, or infrastructure component requires a new Architecture Decision Record.
