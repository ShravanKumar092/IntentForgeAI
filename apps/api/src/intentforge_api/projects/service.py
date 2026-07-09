from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from intentforge_api.auth.schemas import AuthenticationPrincipal
from intentforge_api.projects.errors import (
    DuplicateEvidenceRelationshipError,
    DuplicateSourceError,
    EvidenceNotFoundError,
    ProjectIntentNotFoundError,
    ProjectNotFoundError,
    RequirementNotFoundError,
    SourceNotFoundError,
)
from intentforge_api.projects.repository import (
    SqlAlchemyEvidenceRepository,
    SqlAlchemyEvidenceRequirementRepository,
    SqlAlchemyProjectRepository,
    SqlAlchemySourceRepository,
)
from intentforge_api.projects.schemas import (
    EvidenceCreateRequest,
    EvidenceRequirementLinkRequest,
    EvidenceUpdateRequest,
    ProjectCreateRequest,
    ProjectIntentRequest,
    ProjectUpdateRequest,
    RequirementCreateRequest,
    RequirementLifecycleStatus,
    RequirementUpdateRequest,
    SourceCreateRequest,
    SourceUpdateRequest,
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


class SourceService:
    def __init__(
        self,
        source_repository: SqlAlchemySourceRepository,
        project_repository: SqlAlchemyProjectRepository,
        session: AsyncSession,
    ) -> None:
        self._source_repository = source_repository
        self._project_repository = project_repository
        self._session = session

    async def _require_owned_project(
        self,
        principal: AuthenticationPrincipal,
        project_id: UUID,
    ):
        project = await self._project_repository.find_owned_by_id(
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

    async def create_source(
        self,
        principal: AuthenticationPrincipal,
        project_id: UUID,
        payload: SourceCreateRequest,
    ):
        await self._require_owned_project(principal, project_id)
        existing_source = await self._source_repository.get_source_by_locator(
            project_id=project_id,
            locator=payload.locator,
        )
        if existing_source is not None:
            raise DuplicateSourceError("source already exists")

        async with self._session.begin():
            source = await self._source_repository.create_source(
                project_id=project_id,
                source_type=payload.source_type.value,
                title=payload.title,
                locator=payload.locator,
                observed_at=payload.observed_at,
            )

        logger.info(
            "Project source created",
            extra={
                "event": "project_source_created",
                "identity_id": str(principal.user.id),
                "project_id": str(project_id),
                "source_id": str(source.id),
                "source_type": source.source_type,
            },
        )
        return source

    async def list_sources(
        self,
        principal: AuthenticationPrincipal,
        project_id: UUID,
    ):
        await self._require_owned_project(principal, project_id)
        sources = await self._source_repository.list_sources(project_id=project_id)

        logger.info(
            "Project sources listed",
            extra={
                "event": "project_sources_listed",
                "identity_id": str(principal.user.id),
                "project_id": str(project_id),
                "source_count": len(sources),
            },
        )
        return sources

    async def get_source(
        self,
        principal: AuthenticationPrincipal,
        project_id: UUID,
        source_id: UUID,
    ):
        await self._require_owned_project(principal, project_id)
        source = await self._source_repository.get_source_by_id(
            project_id=project_id,
            source_id=source_id,
        )
        if source is None:
            raise SourceNotFoundError("source not found")

        logger.info(
            "Project source retrieved",
            extra={
                "event": "project_source_retrieved",
                "identity_id": str(principal.user.id),
                "project_id": str(project_id),
                "source_id": str(source.id),
            },
        )
        return source

    async def update_source(
        self,
        principal: AuthenticationPrincipal,
        project_id: UUID,
        source_id: UUID,
        payload: SourceUpdateRequest,
    ):
        await self._require_owned_project(principal, project_id)
        source = await self._source_repository.get_source_by_id(
            project_id=project_id,
            source_id=source_id,
        )
        if source is None:
            raise SourceNotFoundError("source not found")

        if payload.locator is not None:
            existing_source = await self._source_repository.get_source_by_locator(
                project_id=project_id,
                locator=payload.locator,
            )
            if existing_source is not None and existing_source.id != source.id:
                raise DuplicateSourceError("source already exists")
            source.locator = payload.locator
        if payload.title is not None:
            source.title = payload.title
        if payload.observed_at is not None:
            source.observed_at = payload.observed_at

        async with self._session.begin():
            source = await self._source_repository.save_source(source)

        logger.info(
            "Project source updated",
            extra={
                "event": "project_source_updated",
                "identity_id": str(principal.user.id),
                "project_id": str(project_id),
                "source_id": str(source.id),
            },
        )
        return source


class EvidenceService:
    def __init__(
        self,
        evidence_repository: SqlAlchemyEvidenceRepository,
        source_repository: SqlAlchemySourceRepository,
        project_repository: SqlAlchemyProjectRepository,
        session: AsyncSession,
    ) -> None:
        self._evidence_repository = evidence_repository
        self._source_repository = source_repository
        self._project_repository = project_repository
        self._session = session

    async def _require_owned_project(
        self,
        principal: AuthenticationPrincipal,
        project_id: UUID,
    ):
        project = await self._project_repository.find_owned_by_id(
            owner_id=principal.user.id,
            project_id=project_id,
        )
        if project is None:
            raise ProjectNotFoundError("project not found")
        return project

    async def create_evidence(
        self,
        principal: AuthenticationPrincipal,
        project_id: UUID,
        payload: EvidenceCreateRequest,
    ):
        await self._require_owned_project(principal, project_id)
        source = await self._source_repository.get_source_by_id(
            project_id=project_id,
            source_id=payload.source_id,
        )
        if source is None:
            raise SourceNotFoundError("source not found")

        async with self._session.begin():
            evidence = await self._evidence_repository.create_evidence(
                project_id=project_id,
                source_id=payload.source_id,
                claim=payload.claim,
                excerpt=payload.excerpt,
                source_location=payload.source_location,
                observed_at=payload.observed_at,
            )

        logger.info(
            "Project evidence created",
            extra={
                "event": "project_evidence_created",
                "identity_id": str(principal.user.id),
                "project_id": str(project_id),
                "evidence_id": str(evidence.id),
                "source_id": str(evidence.source_id),
            },
        )
        return evidence

    async def list_evidence(
        self,
        principal: AuthenticationPrincipal,
        project_id: UUID,
    ):
        await self._require_owned_project(principal, project_id)
        evidence_items = await self._evidence_repository.list_evidence(project_id=project_id)

        logger.info(
            "Project evidence listed",
            extra={
                "event": "project_evidence_listed",
                "identity_id": str(principal.user.id),
                "project_id": str(project_id),
                "evidence_count": len(evidence_items),
            },
        )
        return evidence_items

    async def get_evidence(
        self,
        principal: AuthenticationPrincipal,
        project_id: UUID,
        evidence_id: UUID,
    ):
        await self._require_owned_project(principal, project_id)
        evidence = await self._evidence_repository.get_evidence_by_id(
            project_id=project_id,
            evidence_id=evidence_id,
        )
        if evidence is None:
            raise EvidenceNotFoundError("evidence not found")

        logger.info(
            "Project evidence retrieved",
            extra={
                "event": "project_evidence_retrieved",
                "identity_id": str(principal.user.id),
                "project_id": str(project_id),
                "evidence_id": str(evidence.id),
            },
        )
        return evidence

    async def update_evidence(
        self,
        principal: AuthenticationPrincipal,
        project_id: UUID,
        evidence_id: UUID,
        payload: EvidenceUpdateRequest,
    ):
        await self._require_owned_project(principal, project_id)
        evidence = await self._evidence_repository.get_evidence_by_id(
            project_id=project_id,
            evidence_id=evidence_id,
        )
        if evidence is None:
            raise EvidenceNotFoundError("evidence not found")

        if payload.claim is not None:
            evidence.claim = payload.claim
        if payload.excerpt is not None:
            evidence.excerpt = payload.excerpt
        if payload.source_location is not None:
            evidence.source_location = payload.source_location
        if payload.observed_at is not None:
            evidence.observed_at = payload.observed_at

        async with self._session.begin():
            evidence = await self._evidence_repository.save_evidence(evidence)

        logger.info(
            "Project evidence updated",
            extra={
                "event": "project_evidence_updated",
                "identity_id": str(principal.user.id),
                "project_id": str(project_id),
                "evidence_id": str(evidence.id),
            },
        )
        return evidence


class EvidenceRequirementService:
    def __init__(
        self,
        record_repository: SqlAlchemyEvidenceRequirementRepository,
        evidence_repository: SqlAlchemyEvidenceRepository,
        project_repository: SqlAlchemyProjectRepository,
        session: AsyncSession,
    ) -> None:
        self._record_repository = record_repository
        self._evidence_repository = evidence_repository
        self._project_repository = project_repository
        self._session = session

    async def _require_owned_project(
        self,
        principal: AuthenticationPrincipal,
        project_id: UUID,
    ):
        project = await self._project_repository.find_owned_by_id(
            owner_id=principal.user.id,
            project_id=project_id,
        )
        if project is None:
            raise ProjectNotFoundError("project not found")
        return project

    async def link_evidence_to_requirement(
        self,
        principal: AuthenticationPrincipal,
        project_id: UUID,
        evidence_id: UUID,
        payload: EvidenceRequirementLinkRequest,
    ):
        await self._require_owned_project(principal, project_id)
        evidence = await self._evidence_repository.get_evidence_by_id(
            project_id=project_id,
            evidence_id=evidence_id,
        )
        if evidence is None:
            raise EvidenceNotFoundError("evidence not found")

        requirement = await self._project_repository.get_requirement_by_id(
            project_id=project_id,
            requirement_id=payload.requirement_id,
        )
        if requirement is None:
            raise RequirementNotFoundError("requirement not found")

        existing_link = await self._record_repository.find_link(
            project_id=project_id,
            evidence_id=evidence_id,
            requirement_id=payload.requirement_id,
            relationship_type=payload.relationship_type.value,
        )
        if existing_link is not None:
            raise DuplicateEvidenceRelationshipError("relationship already exists")

        async with self._session.begin():
            link = await self._record_repository.create_evidence_requirement_link(
                project_id=project_id,
                evidence_id=evidence_id,
                requirement_id=payload.requirement_id,
                relationship_type=payload.relationship_type.value,
            )

        logger.info(
            "Evidence linked to requirement",
            extra={
                "event": "evidence_requirement_link_created",
                "identity_id": str(principal.user.id),
                "project_id": str(project_id),
                "evidence_id": str(evidence_id),
                "requirement_id": str(payload.requirement_id),
                "relationship_type": payload.relationship_type.value,
            },
        )
        return link

    async def list_requirements_for_evidence(
        self,
        principal: AuthenticationPrincipal,
        project_id: UUID,
        evidence_id: UUID,
    ):
        await self._require_owned_project(principal, project_id)
        return await self._record_repository.list_requirements_for_evidence(
            project_id=project_id,
            evidence_id=evidence_id,
        )

    async def list_evidence_for_requirement(
        self,
        principal: AuthenticationPrincipal,
        project_id: UUID,
        requirement_id: UUID,
    ):
        await self._require_owned_project(principal, project_id)
        return await self._record_repository.list_evidence_for_requirement(
            project_id=project_id,
            requirement_id=requirement_id,
        )
