"""Evidence and source provenance foundation.

Revision ID: m8_project_001
Revises: m7_project_001
Create Date: 2026-07-09
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "m8_project_001"
down_revision: Union[str, Sequence[str], None] = "m7_project_001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sources",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("project_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("locator", sa.String(length=1024), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_sources_project_id_projects"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sources")),
        sa.UniqueConstraint("project_id", "locator", name=op.f("uq_sources_project_locator")),
    )
    op.create_index(op.f("ix_sources_project_id"), "sources", ["project_id"], unique=False)

    op.create_table(
        "evidence",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("project_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("source_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("claim", sa.Text(), nullable=False),
        sa.Column("excerpt", sa.Text(), nullable=True),
        sa.Column("source_location", sa.String(length=1024), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_evidence_project_id_projects"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["sources.id"],
            name=op.f("fk_evidence_source_id_sources"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_evidence")),
    )
    op.create_index(op.f("ix_evidence_project_id"), "evidence", ["project_id"], unique=False)
    op.create_index(op.f("ix_evidence_source_id"), "evidence", ["source_id"], unique=False)

    op.create_table(
        "evidence_requirement_links",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("project_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("evidence_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("requirement_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("relationship_type", sa.String(length=16), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_evidence_requirement_links_project_id_projects"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["evidence_id"],
            ["evidence.id"],
            name=op.f("fk_evidence_requirement_links_evidence_id_evidence"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["requirement_id"],
            ["requirements.id"],
            name=op.f("fk_evidence_requirement_links_requirement_id_requirements"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_evidence_requirement_links")),
        sa.UniqueConstraint(
            "project_id",
            "evidence_id",
            "requirement_id",
            "relationship_type",
            name=op.f("uq_evidence_requirement_links_project_evidence_requirement_relationship"),
        ),
        sa.CheckConstraint(
            "relationship_type IN ('supports', 'contradicts', 'relevant')",
            name=op.f("ck_evidence_requirement_links_relationship_type"),
        ),
    )
    op.create_index(
        op.f("ix_evidence_requirement_links_project_id"),
        "evidence_requirement_links",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_evidence_requirement_links_evidence_id"),
        "evidence_requirement_links",
        ["evidence_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_evidence_requirement_links_requirement_id"),
        "evidence_requirement_links",
        ["requirement_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_evidence_requirement_links_requirement_id"),
        table_name="evidence_requirement_links",
    )
    op.drop_index(
        op.f("ix_evidence_requirement_links_evidence_id"),
        table_name="evidence_requirement_links",
    )
    op.drop_index(
        op.f("ix_evidence_requirement_links_project_id"),
        table_name="evidence_requirement_links",
    )
    op.drop_table("evidence_requirement_links")
    op.drop_index(op.f("ix_evidence_source_id"), table_name="evidence")
    op.drop_index(op.f("ix_evidence_project_id"), table_name="evidence")
    op.drop_table("evidence")
    op.drop_index(op.f("ix_sources_project_id"), table_name="sources")
    op.drop_table("sources")
