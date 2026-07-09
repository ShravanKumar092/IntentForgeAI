# IF-P1-E008 — Source and Evidence Provenance Foundation

This evidence record demonstrates the addition of project-owned provenance support for sources, evidence, and evidence-to-requirement relationships.

- Added `sources`, `evidence`, and `evidence_requirement_links` database tables.
- Added SQLAlchemy models and repository methods for sources, evidence, and evidence requirement links.
- Added service-level authorization to keep provenance records scoped by project ownership.
- Added API routes for creating, listing, and linking provenance data.
- Added automated tests for provenance persistence, service behavior, and API route contracts.

The implementation preserves the existing project ownership and authentication model while enabling traceable source and evidence provenance for requirements.
