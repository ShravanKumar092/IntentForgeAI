"""Project intent and requirement foundation.

Revision ID: m7_project_001
Revises: m6_project_001
Create Date: 2026-07-09
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "m7_project_001"
down_revision: Union[str, Sequence[str], None] = "m6_project_001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "project_intents",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("project_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("problem_statement", sa.Text(), nullable=True),
        sa.Column("desired_outcome", sa.Text(), nullable=True),
        sa.Column("goals", sa.Text(), nullable=True),
        sa.Column("non_goals", sa.Text(), nullable=True),
        sa.Column("constraints", sa.Text(), nullable=True),
        sa.Column("success_criteria", sa.Text(), nullable=True),
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
            name=op.f("fk_project_intents_project_id_projects"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_intents")),
    )
    op.create_index(
        op.f("ix_project_intents_project_id"),
        "project_intents",
        ["project_id"],
        unique=False,
    )

    op.create_table(
        "requirements",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("project_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "classification",
            sa.String(length=16),
            nullable=False,
            server_default=sa.text("'functional'"),
        ),
        sa.Column(
            "priority",
            sa.String(length=16),
            nullable=False,
            server_default=sa.text("'medium'"),
        ),
        sa.Column(
            "lifecycle_status",
            sa.String(length=16),
            nullable=False,
            server_default=sa.text("'active'"),
        ),
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
            name=op.f("fk_requirements_project_id_projects"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_requirements")),
    )
    op.create_index(op.f("ix_requirements_project_id"), "requirements", ["project_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_requirements_project_id"), table_name="requirements")
    op.drop_table("requirements")
    op.drop_index(op.f("ix_project_intents_project_id"), table_name="project_intents")
    op.drop_table("project_intents")
