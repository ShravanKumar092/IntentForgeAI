from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from intentforge_api.auth.schemas import AuthenticationPrincipal
from intentforge_api.projects.errors import (
    ProjectIntentNotFoundError,
    ProjectNotFoundError,
    RequirementNotFoundError,
)
from intentforge_api.projects.repository import SqlAlchemyProjectRepository
from intentforge_api.projects.schemas import (
    ProjectCreateRequest,
    ProjectIntentRequest,
    ProjectUpdateRequest,
    RequirementCreateRequest,
    RequirementLifecycleStatus,
    RequirementUpdateRequest,
)


logger = logging.getLogger("intentforge.project")


class ProjectService:
    def __init__(self, repository: SqlAlchemyProjectRepository, session: AsyncSession) -> None:
        self._repository = repository
        self._session = session

    async def create_project(
        self,
        principal: AuthenticationPrincipal,
        payload: ProjectCreateRequest,
    ):
        async with self._session.begin():
            project = await self._repository.create(
                owner_id=principal.user.id,
                name=payload.name,
            )

        logger.info(
            "Project created",
            extra={
                "event": "project_created",
                "identity_id": str(principal.user.id),
                "project_id": str(project.id),
                "lifecycle_status": project.lifecycle_status,
            },
        )
        return project

    async def list_projects(self, principal: AuthenticationPrincipal):
        projects = await self._repository.list_owned(owner_id=principal.user.id)

        logger.info(
            "Projects listed",
            extra={
                "event": "projects_listed",
                "identity_id": str(principal.user.id),
                "project_count": len(projects),
            },
        )
        return projects

    async def get_project(
        self,
        principal: AuthenticationPrincipal,
        project_id: UUID,
    ):
        project = await self._repository.find_owned_by_id(
            owner_id=principal.user.id,
            project_id=project_id,
        )
        if project is None:
            logger.info(
                "Project access denied",
                extra={
                    "event": "project_access_denied",
                    "identity_id": str(principal.user.id),
                    "project_id": str(project_id),
                    "reason": "not_found_or_unauthorized",
                },
            )
            raise ProjectNotFoundError("project not found")

        logger.info(
            "Project retrieved",
            extra={
                "event": "project_retrieved",
                "identity_id": str(principal.user.id),
                "project_id": str(project.id),
                "lifecycle_status": project.lifecycle_status,
            },
        )
        return project

    async def update_project(
        self,
        principal: AuthenticationPrincipal,
        project_id: UUID,
        payload: ProjectUpdateRequest,
    ):
        async with self._session.begin():
            project = await self._repository.find_owned_by_id(
                owner_id=principal.user.id,
                project_id=project_id,
            )
            if project is None:
                logger.info(
                    "Project access denied",
                    extra={
                        "event": "project_access_denied",
                        "identity_id": str(principal.user.id),
                        "project_id": str(project_id),
                        "reason": "not_found_or_unauthorized",
                    },
                )
                raise ProjectNotFoundError("project not found")

            project.name = payload.name
            await self._repository.save(project)

        logger.info(
            "Project updated",
            extra={
                "event": "project_updated",
                "identity_id": str(principal.user.id),
                "project_id": str(project.id),
                "changed_fields": ["name"],
            },
        )
        return project

    async def _require_owned_project(
        self,
        principal: AuthenticationPrincipal,
        project_id: UUID,
    ):
        project = await self._repository.find_owned_by_id(
            owner_id=principal.user.id,
            project_id=project_id,
        )
        if project is None:
            logger.info(
                "Project access denied",
                extra={
                    "event": "project_access_denied",
                    "identity_id": str(principal.user.id),
                    "project_id": str(project_id),
                    "reason": "not_found_or_unauthorized",
                },
            )
            raise ProjectNotFoundError("project not found")
        return project

    async def get_project_intent(
        self,
        principal: AuthenticationPrincipal,
        project_id: UUID,
    ):
        await self._require_owned_project(principal, project_id)
        intent = await self._repository.get_intent_by_project_id(project_id)
        if intent is None:
            logger.info(
                "Project intent not found",
                extra={
                    "event": "project_intent_not_found",
                    "identity_id": str(principal.user.id),
                    "project_id": str(project_id),
                },
            )
            raise ProjectIntentNotFoundError("project intent not found")

        logger.info(
            "Project intent retrieved",
            extra={
                "event": "project_intent_retrieved",
                "identity_id": str(principal.user.id),
                "project_id": str(project_id),
                "project_intent_id": str(intent.id),
            },
        )
        return intent

    async def upsert_project_intent(
        self,
        principal: AuthenticationPrincipal,
        project_id: UUID,
        payload: ProjectIntentRequest,
    ):
        await self._require_owned_project(principal, project_id)
        intent = await self._repository.get_intent_by_project_id(project_id)
        if intent is None:
            intent = await self._repository.create_intent_for_project(
                project_id=project_id,
                problem_statement=payload.problem_statement,
                desired_outcome=payload.desired_outcome,
                goals=payload.goals,
                non_goals=payload.non_goals,
                constraints=payload.constraints,
                success_criteria=payload.success_criteria,
            )
            event_name = "project_intent_created"
        else:
            intent.problem_statement = payload.problem_statement
            intent.desired_outcome = payload.desired_outcome
            intent.goals = payload.goals
            intent.non_goals = payload.non_goals
            intent.constraints = payload.constraints
            intent.success_criteria = payload.success_criteria
            intent = await self._repository.save_intent(intent)
            event_name = "project_intent_updated"

        logger.info(
            "Project intent upserted",
            extra={
                "event": event_name,
                "identity_id": str(principal.user.id),
                "project_id": str(project_id),
                "project_intent_id": str(intent.id),
            },
        )
        return intent

    async def create_requirement(
        self,
        principal: AuthenticationPrincipal,
        project_id: UUID,
        payload: RequirementCreateRequest,
    ):
        await self._require_owned_project(principal, project_id)
        requirement = await self._repository.create_requirement(
            project_id=project_id,
            title=payload.title,
            description=payload.description,
            classification=payload.classification.value,
            priority=payload.priority.value,
            lifecycle_status=RequirementLifecycleStatus.ACTIVE.value,
        )

        logger.info(
            "Project requirement created",
            extra={
                "event": "project_requirement_created",
                "identity_id": str(principal.user.id),
                "project_id": str(project_id),
                "requirement_id": str(requirement.id),
                "classification": requirement.classification,
                "priority": requirement.priority,
            },
        )
        return requirement

    async def list_requirements(
        self,
        principal: AuthenticationPrincipal,
        project_id: UUID,
    ):
        await self._require_owned_project(principal, project_id)
        requirements = await self._repository.list_requirements(project_id=project_id)

        logger.info(
            "Project requirements listed",
            extra={
                "event": "project_requirements_listed",
                "identity_id": str(principal.user.id),
                "project_id": str(project_id),
                "requirement_count": len(requirements),
            },
        )
        return requirements

    async def get_requirement(
        self,
        principal: AuthenticationPrincipal,
        project_id: UUID,
        requirement_id: UUID,
    ):
        await self._require_owned_project(principal, project_id)
        requirement = await self._repository.get_requirement_by_id(
            project_id=project_id,
            requirement_id=requirement_id,
        )
        if requirement is None:
            logger.info(
                "Project requirement access denied",
                extra={
                    "event": "project_requirement_not_found",
                    "identity_id": str(principal.user.id),
                    "project_id": str(project_id),
                    "requirement_id": str(requirement_id),
                },
            )
            raise RequirementNotFoundError("requirement not found")

        logger.info(
            "Project requirement retrieved",
            extra={
                "event": "project_requirement_retrieved",
                "identity_id": str(principal.user.id),
                "project_id": str(project_id),
                "requirement_id": str(requirement.id),
                "lifecycle_status": requirement.lifecycle_status,
            },
        )
        return requirement

    async def update_requirement(
        self,
        principal: AuthenticationPrincipal,
        project_id: UUID,
        requirement_id: UUID,
        payload: RequirementUpdateRequest,
    ):
        await self._require_owned_project(principal, project_id)
        requirement = await self._repository.get_requirement_by_id(
            project_id=project_id,
            requirement_id=requirement_id,
        )
        if requirement is None:
            logger.info(
                "Project requirement access denied",
                extra={
                    "event": "project_requirement_not_found",
                    "identity_id": str(principal.user.id),
                    "project_id": str(project_id),
                    "requirement_id": str(requirement_id),
                },
            )
            raise RequirementNotFoundError("requirement not found")

        if payload.title is not None:
            requirement.title = payload.title
        if payload.description is not None:
            requirement.description = payload.description
        if payload.classification is not None:
            requirement.classification = payload.classification.value
        if payload.priority is not None:
            requirement.priority = payload.priority.value
        if payload.lifecycle_status is not None:
            requirement.lifecycle_status = payload.lifecycle_status.value

        requirement = await self._repository.save_requirement(requirement)

        logger.info(
            "Project requirement updated",
            extra={
                "event": "project_requirement_updated",
                "identity_id": str(principal.user.id),
                "project_id": str(project_id),
                "requirement_id": str(requirement.id),
                "lifecycle_status": requirement.lifecycle_status,
            },
        )
        return requirement
