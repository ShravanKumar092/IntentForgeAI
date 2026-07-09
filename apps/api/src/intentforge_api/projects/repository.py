from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from intentforge_api.projects.models import (
    Evidence,
    EvidenceRequirementLink,
    Project,
    ProjectIntent,
    ProjectLifecycleStatus,
    Requirement,
    Source,
)


class SqlAlchemyProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, *, owner_id: UUID, name: str) -> Project:
        project = Project(
            owner_id=owner_id,
            name=name,
            lifecycle_status=ProjectLifecycleStatus.ACTIVE.value,
        )
        self.session.add(project)

        await self.session.flush()
        await self.session.refresh(project)
        return project

    async def list_owned(self, *, owner_id: UUID) -> list[Project]:
        result = await self.session.execute(
            select(Project)
            .where(Project.owner_id == owner_id)
            .order_by(Project.created_at.asc(), Project.id.asc())
        )
        return list(result.scalars().all())

    async def find_owned_by_id(self, *, owner_id: UUID, project_id: UUID) -> Project | None:
        result = await self.session.execute(
            select(Project).where(
                Project.id == project_id,
                Project.owner_id == owner_id,
            )
        )
        return result.scalar_one_or_none()

    async def save(self, project: Project) -> Project:
        await self.session.flush()
        await self.session.refresh(project)
        return project

    async def get_intent_by_project_id(self, project_id: UUID) -> ProjectIntent | None:
        result = await self.session.execute(
            select(ProjectIntent).where(ProjectIntent.project_id == project_id)
        )
        return result.scalar_one_or_none()

    async def create_intent_for_project(
        self,
        project_id: UUID,
        problem_statement: str | None = None,
        desired_outcome: str | None = None,
        goals: str | None = None,
        non_goals: str | None = None,
        constraints: str | None = None,
        success_criteria: str | None = None,
    ) -> ProjectIntent:
        intent = ProjectIntent(
            project_id=project_id,
            problem_statement=problem_statement,
            desired_outcome=desired_outcome,
            goals=goals,
            non_goals=non_goals,
            constraints=constraints,
            success_criteria=success_criteria,
        )
        self.session.add(intent)

        await self.session.flush()
        await self.session.refresh(intent)
        return intent

    async def save_intent(self, intent: ProjectIntent) -> ProjectIntent:
        await self.session.flush()
        await self.session.refresh(intent)
        return intent

    async def create_requirement(
        self,
        project_id: UUID,
        title: str,
        description: str,
        classification: str,
        priority: str,
        lifecycle_status: str,
    ) -> Requirement:
        requirement = Requirement(
            project_id=project_id,
            title=title,
            description=description,
            classification=classification,
            priority=priority,
            lifecycle_status=lifecycle_status,
        )
        self.session.add(requirement)

        await self.session.flush()
        await self.session.refresh(requirement)
        return requirement

    async def list_requirements(self, *, project_id: UUID) -> list[Requirement]:
        result = await self.session.execute(
            select(Requirement)
            .where(Requirement.project_id == project_id)
            .order_by(Requirement.created_at.asc(), Requirement.id.asc())
        )
        return list(result.scalars().all())

    async def get_requirement_by_id(
        self,
        project_id: UUID,
        requirement_id: UUID,
    ) -> Requirement | None:
        result = await self.session.execute(
            select(Requirement).where(
                Requirement.id == requirement_id,
                Requirement.project_id == project_id,
            )
        )
        return result.scalar_one_or_none()

    async def save_requirement(self, requirement: Requirement) -> Requirement:
        await self.session.flush()
        await self.session.refresh(requirement)
        return requirement


class SqlAlchemySourceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_source(
        self,
        project_id: UUID,
        source_type: str,
        title: str,
        locator: str,
        observed_at: datetime | None = None,
    ) -> "Source":
        from intentforge_api.projects.models import Source

        source = Source(
            project_id=project_id,
            source_type=source_type,
            title=title,
            locator=locator,
            observed_at=observed_at,
        )
        self.session.add(source)

        await self.session.flush()
        await self.session.refresh(source)
        return source

    async def list_sources(self, *, project_id: UUID) -> list["Source"]:
        from intentforge_api.projects.models import Source

        result = await self.session.execute(
            select(Source)
            .where(Source.project_id == project_id)
            .order_by(Source.created_at.asc(), Source.id.asc())
        )
        return list(result.scalars().all())

    async def get_source_by_id(self, project_id: UUID, source_id: UUID) -> "Source" | None:
        from intentforge_api.projects.models import Source

        result = await self.session.execute(
            select(Source).where(
                Source.id == source_id,
                Source.project_id == project_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_source_by_locator(self, project_id: UUID, locator: str) -> "Source" | None:
        from intentforge_api.projects.models import Source

        result = await self.session.execute(
            select(Source).where(
                Source.project_id == project_id,
                Source.locator == locator,
            )
        )
        return result.scalar_one_or_none()

    async def save_source(self, source: "Source") -> "Source":
        await self.session.flush()
        await self.session.refresh(source)
        return source


class SqlAlchemyEvidenceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_evidence(
        self,
        project_id: UUID,
        source_id: UUID,
        claim: str,
        excerpt: str | None = None,
        source_location: str | None = None,
        observed_at: datetime | None = None,
    ) -> "Evidence":
        from intentforge_api.projects.models import Evidence

        evidence = Evidence(
            project_id=project_id,
            source_id=source_id,
            claim=claim,
            excerpt=excerpt,
            source_location=source_location,
            observed_at=observed_at,
        )
        self.session.add(evidence)

        await self.session.flush()
        await self.session.refresh(evidence)
        return evidence

    async def list_evidence(self, *, project_id: UUID) -> list["Evidence"]:
        from intentforge_api.projects.models import Evidence

        result = await self.session.execute(
            select(Evidence)
            .where(Evidence.project_id == project_id)
            .order_by(Evidence.created_at.asc(), Evidence.id.asc())
        )
        return list(result.scalars().all())

    async def get_evidence_by_id(self, project_id: UUID, evidence_id: UUID) -> "Evidence" | None:
        from intentforge_api.projects.models import Evidence

        result = await self.session.execute(
            select(Evidence).where(
                Evidence.id == evidence_id,
                Evidence.project_id == project_id,
            )
        )
        return result.scalar_one_or_none()

    async def save_evidence(self, evidence: "Evidence") -> "Evidence":
        await self.session.flush()
        await self.session.refresh(evidence)
        return evidence


class SqlAlchemyEvidenceRequirementRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_evidence_requirement_link(
        self,
        project_id: UUID,
        evidence_id: UUID,
        requirement_id: UUID,
        relationship_type: str,
    ) -> "EvidenceRequirementLink":
        from intentforge_api.projects.models import EvidenceRequirementLink

        link = EvidenceRequirementLink(
            project_id=project_id,
            evidence_id=evidence_id,
            requirement_id=requirement_id,
            relationship_type=relationship_type,
        )
        self.session.add(link)

        await self.session.flush()
        await self.session.refresh(link)
        return link

    async def find_link(
        self,
        project_id: UUID,
        evidence_id: UUID,
        requirement_id: UUID,
        relationship_type: str,
    ) -> "EvidenceRequirementLink" | None:
        from intentforge_api.projects.models import EvidenceRequirementLink

        result = await self.session.execute(
            select(EvidenceRequirementLink).where(
                EvidenceRequirementLink.project_id == project_id,
                EvidenceRequirementLink.evidence_id == evidence_id,
                EvidenceRequirementLink.requirement_id == requirement_id,
                EvidenceRequirementLink.relationship_type == relationship_type,
            )
        )
        return result.scalar_one_or_none()

    async def list_requirements_for_evidence(
        self,
        project_id: UUID,
        evidence_id: UUID,
    ) -> list["EvidenceRequirementLink"]:
        from intentforge_api.projects.models import EvidenceRequirementLink

        result = await self.session.execute(
            select(EvidenceRequirementLink)
            .where(
                EvidenceRequirementLink.project_id == project_id,
                EvidenceRequirementLink.evidence_id == evidence_id,
            )
            .order_by(EvidenceRequirementLink.created_at.asc(), EvidenceRequirementLink.id.asc())
        )
        return list(result.scalars().all())

    async def list_evidence_for_requirement(
        self,
        project_id: UUID,
        requirement_id: UUID,
    ) -> list["EvidenceRequirementLink"]:
        from intentforge_api.projects.models import EvidenceRequirementLink

        result = await self.session.execute(
            select(EvidenceRequirementLink)
            .where(
                EvidenceRequirementLink.project_id == project_id,
                EvidenceRequirementLink.requirement_id == requirement_id,
            )
            .order_by(EvidenceRequirementLink.created_at.asc(), EvidenceRequirementLink.id.asc())
        )
        return list(result.scalars().all())
