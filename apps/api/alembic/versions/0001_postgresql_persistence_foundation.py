"""PostgreSQL persistence foundation baseline.

Revision ID: m3_postgres_001
Revises:
Create Date: 2026-07-08

This revision intentionally introduces no tables.
The milestone establishes the migration boundary and revision control
without inventing domain schema before a domain requirement exists.
"""

from typing import Sequence, Union


revision: str = "m3_postgres_001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
