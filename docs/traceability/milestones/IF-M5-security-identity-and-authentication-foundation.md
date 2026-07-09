# IF-M5 — Security, Identity, and Authentication Foundation

## Status

VERIFIED

## Purpose

Establish the first production-grade trust boundary for IntentForge AI with durable user identity, secure password handling, signed access tokens, protected routes, and correlation-aware security logging.

## Governing ADRs

- ADR-001 — Modular Monorepo Architecture
- ADR-002 — Runtime and Technology Stack
- ADR-003 — Configuration, Runtime Identity, and Observability Foundation
- ADR-004 — PostgreSQL Persistence and Migration Foundation
- ADR-005 — Redis Ephemeral State and Coordination Foundation
- ADR-006 — Security, Identity, and Authentication Foundation

## Security Model

- PostgreSQL is the authoritative durable store for identity metadata.
- Authentication uses signed bearer access tokens.
- Authorization is limited to authenticated versus unauthenticated boundaries and active versus inactive identities.
- Caller-controlled identity headers are rejected.

## Identity Model

- The durable `users` table stores normalized email, password hash, active status, and timestamps.
- Plaintext passwords are never stored.
- No speculative profile or permission fields were introduced.

## Password Security

- Passwords are hashed with PBKDF2-HMAC-SHA256 and a random salt.
- Hash verification is centralized.
- Rehash detection is available.
- Production secrets are validated through the centralized settings model.

## Token Architecture

- Access tokens are signed centrally.
- Claims include subject, issued-at, expiration, issuer, audience, and token type.
- Bearer token validation is centralized and reusable.

## Refresh Strategy

- Refresh tokens are deferred for M5.
- No incomplete refresh-token persistence or rotation mechanism was introduced.

## Authenticated Principal

- Validated requests resolve an authenticated principal only after token verification and PostgreSQL identity lookup.
- Inactive identities are rejected.

## Protected-Route Boundary

- `POST /api/v1/auth/register` registers a new identity.
- `POST /api/v1/auth/login` authenticates credentials and issues a bearer access token.
- `GET /api/v1/auth/me` returns a safe public identity representation.

## Authorization Foundation

- M5 establishes authenticated and unauthenticated boundaries.
- No project, workspace, organization, or RBAC model was introduced.

## Security Logging

- Registration, login, authentication success, and authentication failure are logged in structured form.
- Correlation IDs are preserved.
- Sensitive material is never logged.

## Migration

- Alembic now tracks the identity schema with a real upgrade.
- The migration head is `m5_auth_001`.
- Revision identifiers were shortened to fit Alembic’s default version table length.

## Tests

- Security configuration tests.
- Password hashing tests.
- Token validation tests.
- Identity model and repository tests.
- Registration, login, and authenticated-principal tests.
- Regression coverage for M1–M4 contracts.

## Live Verification

- PostgreSQL and Redis containers were started successfully.
- Alembic upgraded the live database successfully.
- The live API returned healthy liveness and readiness responses.
- Registration, login, and `auth/me` succeeded live.

## Controlled Failure Verification

- Duplicate registration returned `409 Conflict`.
- Missing bearer credentials returned `401 Unauthorized`.
- Malformed bearer credentials returned `401 Unauthorized`.
- Invalid login credentials returned `401 Unauthorized`.
- Inactive identities are rejected.

## Evidence Mapping

- IF-P1-E005

## Non-Goals

- Projects
- Workspaces
- Organizations
- Teams
- Membership
- Roles
- MFA
- Password reset email delivery
- Email verification delivery
- API keys
- Service accounts
- Social login
- SAML
- Enterprise SSO
- Frontend login screens
- Billing
- Speculative RBAC

## Known Limitations

- Refresh-token lifecycle is deferred.
- Password hashing uses the standard-library PBKDF2 path instead of Argon2id.

## Deferred External Warning

- The Starlette/TestClient `httpx2` warning remains external to M5.
- The pytest cache-path warning is environment-specific.

## Closure Criteria

This milestone is marked `VERIFIED` because:

- M4 is formally closed;
- Python 3.12 was verified;
- ADR-006 was accepted;
- security configuration was centralized;
- production secrets are validated;
- durable identity is implemented;
- a real Alembic migration was applied;
- plaintext passwords are never persisted;
- password hashing and verification are implemented;
- the identity repository boundary is implemented;
- login and registration were verified;
- access-token creation and validation were verified;
- refresh is explicitly deferred;
- authenticated principal resolution was verified;
- protected identity access was verified;
- controlled failure semantics were verified;
- security logs are correlation-aware and secret-safe;
- health remains authentication-independent;
- readiness remains correct;
- all automated tests pass;
- Ruff passes;
- live PostgreSQL verification succeeded;
- Redis regression remained healthy;
- live authentication flow succeeded;
- evidence IF-P1-E005 exists.
