from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from intentforge_api.projects.models import (
    Project,
    ProjectIntent,
    ProjectLifecycleStatus,
    Requirement,
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
