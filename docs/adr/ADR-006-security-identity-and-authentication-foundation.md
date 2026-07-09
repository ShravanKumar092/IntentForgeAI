# ADR-006: Security, Identity, and Authentication Foundation

## Status

Accepted

## Context

IntentForge AI needs a first production-grade trust boundary for durable user identity, secure credential handling, authenticated request context, and protected API routes. M5 must avoid speculative permissions, enterprise SSO, and incomplete refresh-token machinery.

## Decision

### Identity Authority

PostgreSQL is the authoritative durable store for user identity and credential metadata.

Redis is not used as the primary identity store.

### Password Security

User passwords are hashed with `pbkdf2_hmac("sha256", ...)` using a random per-password salt and a high iteration count.

This decision uses the Python 3.12 standard library to keep the milestone self-contained and reproducible without introducing additional password-hashing dependencies during M5.

Plaintext passwords are never persisted or logged.

### Authentication Strategy

M5 uses short-lived signed access tokens carried in the `Authorization: Bearer` header.

Validated identity becomes available to protected routes only after server-side token validation and identity lookup.

### Token Governance

Access tokens include:

- `sub` for the durable user identifier;
- `iat` for issued-at time;
- `exp` for expiration time;
- `iss` for issuer;
- `aud` for audience;
- `token_type` to distinguish access tokens.

Tokens are signed with a centralized secret and a configurable signing algorithm.

Access tokens and refresh tokens are not interchangeable.

### Refresh Token Strategy

Refresh tokens are deferred for M5.

IntentForge AI does not introduce incomplete refresh-token storage, rotation, or revocation infrastructure in this milestone.

### Authentication Context

Protected routes resolve the authenticated principal through validated server-side token processing and a durable PostgreSQL identity lookup.

Caller-controlled identity headers are rejected.

### Authorization Foundation

M5 establishes authenticated versus unauthenticated boundaries and active versus inactive identity checks.

No project, organization, team, or RBAC permission model is introduced.

### Error Semantics

The API returns controlled public responses for:

- missing credentials;
- malformed tokens;
- invalid signatures;
- expired tokens;
- wrong token type;
- unknown identities;
- inactive identities;
- duplicate identities.

Sensitive internal details are not exposed.

### Security Logging

Security events are logged in structured form with correlation IDs and safe identity identifiers after validation.

Passwords, password hashes, raw tokens, and signing secrets are never logged.

### Rejected Alternatives

Rejected for M5:

- plaintext password storage;
- reversible password encryption;
- custom cryptography;
- identity supplied through caller headers;
- permanent access tokens;
- shared semantics between access and refresh tokens;
- raw refresh-token storage;
- duplicated authentication logic in route handlers;
- Redis as the authoritative identity store;
- premature enterprise SSO;
- premature RBAC or permission modeling.

## Consequences

- The API can register identities, authenticate credentials, and protect routes with validated bearer tokens.
- Refresh tokens remain a later milestone concern.
- The implementation stays deterministic, testable, and aligned with the existing modular-monorepo architecture.
