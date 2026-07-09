from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from intentforge_api.db.session import get_async_session
from intentforge_api.projects.repository import (
    SqlAlchemyEvidenceRepository,
    SqlAlchemyEvidenceRequirementRepository,
    SqlAlchemyProjectRepository,
    SqlAlchemySourceRepository,
)
from intentforge_api.projects.service import (
    EvidenceRequirementService,
    EvidenceService,
    ProjectService,
    SourceService,
)


def get_project_service(
    session: AsyncSession = Depends(get_async_session),
) -> ProjectService:
    repository = SqlAlchemyProjectRepository(session)
    return ProjectService(repository=repository, session=session)


def get_source_service(
    session: AsyncSession = Depends(get_async_session),
) -> SourceService:
    source_repository = SqlAlchemySourceRepository(session)
    project_repository = SqlAlchemyProjectRepository(session)
    return SourceService(
        source_repository=source_repository,
        project_repository=project_repository,
        session=session,
    )


def get_evidence_service(
    session: AsyncSession = Depends(get_async_session),
) -> EvidenceService:
    evidence_repository = SqlAlchemyEvidenceRepository(session)
    source_repository = SqlAlchemySourceRepository(session)
    project_repository = SqlAlchemyProjectRepository(session)
    return EvidenceService(
        evidence_repository=evidence_repository,
        source_repository=source_repository,
        project_repository=project_repository,
        session=session,
    )


def get_evidence_requirement_service(
    session: AsyncSession = Depends(get_async_session),
) -> EvidenceRequirementService:
    record_repository = SqlAlchemyEvidenceRequirementRepository(session)
    evidence_repository = SqlAlchemyEvidenceRepository(session)
    project_repository = SqlAlchemyProjectRepository(session)
    return EvidenceRequirementService(
        record_repository=record_repository,
        evidence_repository=evidence_repository,
        project_repository=project_repository,
        session=session,
    )
