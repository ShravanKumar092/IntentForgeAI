from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, UniqueConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from intentforge_api.auth.models import User
from intentforge_api.db.base import Base


class ProjectLifecycleStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class RequirementClassification(StrEnum):
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non-functional"


class RequirementPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RequirementLifecycleStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    SATISFIED = "satisfied"
    REJECTED = "rejected"


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (
        CheckConstraint(
            "lifecycle_status IN ('active', 'archived')",
            name="ck_projects_lifecycle_status",
        ),
        Index("ix_projects_owner_id", "owner_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    lifecycle_status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=ProjectLifecycleStatus.ACTIVE.value,
        server_default=text("'active'"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    owner: Mapped[User] = relationship("User")


class ProjectIntent(Base):
    __tablename__ = "project_intents"
    __table_args__ = (
        UniqueConstraint("project_id", name="uq_project_intents_project_id"),
        Index("ix_project_intents_project_id", "project_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    problem_statement: Mapped[str | None] = mapped_column(Text, nullable=True)
    desired_outcome: Mapped[str | None] = mapped_column(Text, nullable=True)
    goals: Mapped[str | None] = mapped_column(Text, nullable=True)
    non_goals: Mapped[str | None] = mapped_column(Text, nullable=True)
    constraints: Mapped[str | None] = mapped_column(Text, nullable=True)
    success_criteria: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    project: Mapped[Project] = relationship("Project")


class Requirement(Base):
    __tablename__ = "requirements"
    __table_args__ = (
        Index("ix_requirements_project_id", "project_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    classification: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=RequirementClassification.FUNCTIONAL.value,
        server_default=text("'functional'"),
    )
    priority: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=RequirementPriority.MEDIUM.value,
        server_default=text("'medium'"),
    )
    lifecycle_status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=RequirementLifecycleStatus.ACTIVE.value,
        server_default=text("'active'"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    project: Mapped[Project] = relationship("Project")
