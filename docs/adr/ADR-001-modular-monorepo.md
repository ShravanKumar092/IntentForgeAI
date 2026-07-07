# ADR-001: Use a Modular Monorepo Architecture

## Status

Accepted

## Date

2026-07-07

## Context

IntentForge AI combines project intelligence, research intelligence, graph-based traceability, autonomous engineering, multi-agent coordination, testing, debugging, repair, drift detection, and reproducibility.

These capabilities require clear module boundaries while preserving a shared lifecycle and common evidence model.

## Decision

IntentForge AI will use a modular monorepo.

The repository will contain:

- applications;
- independent intelligence services;
- shared packages;
- infrastructure;
- research artifacts;
- tests;
- architecture documentation.

The initial repository structure will separate:

- user-facing applications;
- backend APIs;
- intelligence services;
- shared models;
- graph infrastructure;
- agent protocols;
- evaluation systems;
- research artifacts.

## Consequences

### Positive

- one source of truth;
- easier cross-module traceability;
- shared contracts;
- simpler research experimentation;
- easier end-to-end testing;
- coordinated versioning.

### Negative

- repository complexity will increase;
- module boundaries must be actively enforced;
- careless dependencies could create tight coupling.

## Governance Rule

A new top-level module must have a clear lifecycle responsibility and must not be added merely to organize files.

Every major module must be able to answer:

1. What project problem does this module solve?
2. Which phase introduced it?
3. Which requirement or research question justifies it?
4. What evidence proves that it works?
