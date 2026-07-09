from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from intentforge_api.projects.models import (
    EvidenceRelationshipType,
    ProjectLifecycleStatus,
    RequirementClassification,
    RequirementPriority,
    RequirementLifecycleStatus,
    SourceType,
)


class ProjectCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=120)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("project name must not be empty")
        return normalized


class ProjectUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=120)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()
        if not normalized:
            raise ValueError("project name must not be empty")
        return normalized

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "ProjectUpdateRequest":
        if self.name is None:
            raise ValueError("at least one project field must be provided")

        return self


class ProjectPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    lifecycle_status: ProjectLifecycleStatus
    created_at: datetime
    updated_at: datetime


class ProjectIntentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    problem_statement: str | None = Field(default=None, min_length=1)
    desired_outcome: str | None = Field(default=None, min_length=1)
    goals: str | None = Field(default=None, min_length=1)
    non_goals: str | None = Field(default=None, min_length=1)
    constraints: str | None = Field(default=None, min_length=1)
    success_criteria: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def require_any_field(self) -> "ProjectIntentRequest":
        if (
            self.problem_statement is None
            and self.desired_outcome is None
            and self.goals is None
            and self.non_goals is None
            and self.constraints is None
            and self.success_criteria is None
        ):
            raise ValueError("at least one intent field must be provided")
        return self


class ProjectIntentPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    problem_statement: str | None
    desired_outcome: str | None
    goals: str | None
    non_goals: str | None
    constraints: str | None
    success_criteria: str | None
    created_at: datetime
    updated_at: datetime


class RequirementCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    classification: RequirementClassification = Field(default=RequirementClassification.FUNCTIONAL)
    priority: RequirementPriority = Field(default=RequirementPriority.MEDIUM)


class RequirementUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1, max_length=2000)
    classification: RequirementClassification | None = None
    priority: RequirementPriority | None = None
    lifecycle_status: RequirementLifecycleStatus | None = None

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "RequirementUpdateRequest":
        if (
            self.title is None
            and self.description is None
            and self.classification is None
            and self.priority is None
            and self.lifecycle_status is None
        ):
            raise ValueError("at least one requirement field must be provided")
        return self


class RequirementPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    title: str
    description: str
    classification: RequirementClassification
    priority: RequirementPriority
    lifecycle_status: RequirementLifecycleStatus
    created_at: datetime
    updated_at: datetime


class SourceCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_type: SourceType
    title: str = Field(min_length=1, max_length=200)
    locator: str = Field(min_length=1, max_length=1024)
    observed_at: datetime | None = None

    @field_validator("locator")
    @classmethod
    def normalize_locator(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("source locator must not be empty")
        return normalized


class SourceUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    locator: str | None = Field(default=None, min_length=1, max_length=1024)
    observed_at: datetime | None = None

    @field_validator("locator")
    @classmethod
    def normalize_locator(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("source locator must not be empty")
        return normalized

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "SourceUpdateRequest":
        if self.title is None and self.locator is None and self.observed_at is None:
            raise ValueError("at least one source field must be provided")
        return self


class SourcePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    source_type: SourceType
    title: str
    locator: str
    observed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class EvidenceCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: UUID
    claim: str = Field(min_length=1, max_length=2000)
    excerpt: str | None = Field(default=None, min_length=1, max_length=2000)
    source_location: str | None = Field(default=None, min_length=1, max_length=1024)
    observed_at: datetime | None = None


class EvidenceUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim: str | None = Field(default=None, min_length=1, max_length=2000)
    excerpt: str | None = Field(default=None, min_length=1, max_length=2000)
    source_location: str | None = Field(default=None, min_length=1, max_length=1024)
    observed_at: datetime | None = None

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "EvidenceUpdateRequest":
        if (
            self.claim is None
            and self.excerpt is None
            and self.source_location is None
            and self.observed_at is None
        ):
            raise ValueError("at least one evidence field must be provided")
        return self


class EvidencePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    source_id: UUID
    claim: str
    excerpt: str | None
    source_location: str | None
    observed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class EvidenceRequirementLinkRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requirement_id: UUID
    relationship_type: EvidenceRelationshipType


class EvidenceRequirementLinkPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    evidence_id: UUID
    requirement_id: UUID
    relationship_type: EvidenceRelationshipType
    created_at: datetime
