from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from intentforge_api.auth.dependencies import get_authenticated_principal
from intentforge_api.auth.schemas import AuthenticationPrincipal
from intentforge_api.projects.dependencies import (
    get_evidence_requirement_service,
    get_evidence_service,
    get_project_service,
    get_source_service,
)
from intentforge_api.projects.errors import (
    DuplicateEvidenceRelationshipError,
    DuplicateSourceError,
    EvidenceNotFoundError,
    ProjectIntentNotFoundError,
    ProjectNotFoundError,
    RequirementNotFoundError,
    SourceNotFoundError,
)
from intentforge_api.projects.schemas import (
    EvidenceCreateRequest,
    EvidencePublic,
    EvidenceRequirementLinkPublic,
    EvidenceRequirementLinkRequest,
    EvidenceUpdateRequest,
    ProjectCreateRequest,
    ProjectIntentPublic,
    ProjectIntentRequest,
    ProjectPublic,
    ProjectUpdateRequest,
    RequirementCreateRequest,
    RequirementPublic,
    RequirementUpdateRequest,
    SourceCreateRequest,
    SourcePublic,
    SourceUpdateRequest,
)
from intentforge_api.projects.service import (
    EvidenceRequirementService,
    EvidenceService,
    ProjectService,
    SourceService,
)


router = APIRouter(tags=["projects"])


def _project_response(project) -> ProjectPublic:
    return ProjectPublic.model_validate(project)


def _raise_not_found() -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")


@router.post("/projects", response_model=ProjectPublic, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreateRequest,
    principal: AuthenticationPrincipal = Depends(get_authenticated_principal),
    service: ProjectService = Depends(get_project_service),
) -> ProjectPublic:
    project = await service.create_project(principal, payload)
    return _project_response(project)


@router.get("/projects", response_model=list[ProjectPublic])
async def list_projects(
    principal: AuthenticationPrincipal = Depends(get_authenticated_principal),
    service: ProjectService = Depends(get_project_service),
) -> list[ProjectPublic]:
    projects = await service.list_projects(principal)
    return [_project_response(project) for project in projects]


@router.get("/projects/{project_id}", response_model=ProjectPublic)
async def get_project(
    project_id: UUID,
    principal: AuthenticationPrincipal = Depends(get_authenticated_principal),
    service: ProjectService = Depends(get_project_service),
) -> ProjectPublic:
    try:
        project = await service.get_project(principal, project_id)
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from exc

    return _project_response(project)


@router.patch("/projects/{project_id}", response_model=ProjectPublic)
async def update_project(
    payload: ProjectUpdateRequest,
    project_id: UUID,
    principal: AuthenticationPrincipal = Depends(get_authenticated_principal),
    service: ProjectService = Depends(get_project_service),
) -> ProjectPublic:
    try:
        project = await service.update_project(principal, project_id, payload)
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from exc

    return _project_response(project)


@router.get(
    "/projects/{project_id}/intent",
    response_model=ProjectIntentPublic,
)
async def get_project_intent(
    project_id: UUID,
    principal: AuthenticationPrincipal = Depends(get_authenticated_principal),
    service: ProjectService = Depends(get_project_service),
) -> ProjectIntentPublic:
    try:
        intent = await service.get_project_intent(principal, project_id)
    except (ProjectNotFoundError, ProjectIntentNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project intent not found",
        ) from exc

    return ProjectIntentPublic.model_validate(intent)


@router.post(
    "/projects/{project_id}/intent",
    response_model=ProjectIntentPublic,
)
async def upsert_project_intent(
    payload: ProjectIntentRequest,
    project_id: UUID,
    principal: AuthenticationPrincipal = Depends(get_authenticated_principal),
    service: ProjectService = Depends(get_project_service),
) -> ProjectIntentPublic:
    try:
        intent = await service.upsert_project_intent(principal, project_id, payload)
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from exc

    return ProjectIntentPublic.model_validate(intent)


@router.get(
    "/projects/{project_id}/requirements",
    response_model=list[RequirementPublic],
)
async def list_project_requirements(
    project_id: UUID,
    principal: AuthenticationPrincipal = Depends(get_authenticated_principal),
    service: ProjectService = Depends(get_project_service),
) -> list[RequirementPublic]:
    try:
        requirements = await service.list_requirements(principal, project_id)
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from exc
    return [RequirementPublic.model_validate(requirement) for requirement in requirements]


@router.post(
    "/projects/{project_id}/requirements",
    response_model=RequirementPublic,
    status_code=status.HTTP_201_CREATED,
)
async def create_project_requirement(
    payload: RequirementCreateRequest,
    project_id: UUID,
    principal: AuthenticationPrincipal = Depends(get_authenticated_principal),
    service: ProjectService = Depends(get_project_service),
) -> RequirementPublic:
    try:
        requirement = await service.create_requirement(principal, project_id, payload)
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from exc
    return RequirementPublic.model_validate(requirement)


@router.get(
    "/projects/{project_id}/requirements/{requirement_id}",
    response_model=RequirementPublic,
)
async def get_project_requirement(
    project_id: UUID,
    requirement_id: UUID,
    principal: AuthenticationPrincipal = Depends(get_authenticated_principal),
    service: ProjectService = Depends(get_project_service),
) -> RequirementPublic:
    try:
        requirement = await service.get_requirement(principal, project_id, requirement_id)
    except (ProjectNotFoundError, RequirementNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project requirement not found",
        ) from exc
    return RequirementPublic.model_validate(requirement)


@router.patch(
    "/projects/{project_id}/requirements/{requirement_id}",
    response_model=RequirementPublic,
)
async def update_project_requirement(
    payload: RequirementUpdateRequest,
    project_id: UUID,
    requirement_id: UUID,
    principal: AuthenticationPrincipal = Depends(get_authenticated_principal),
    service: ProjectService = Depends(get_project_service),
) -> RequirementPublic:
    try:
        requirement = await service.update_requirement(
            principal, project_id, requirement_id, payload
        )
    except (ProjectNotFoundError, RequirementNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project requirement not found",
        ) from exc
    return RequirementPublic.model_validate(requirement)


@router.post(
    "/projects/{project_id}/sources",
    response_model=SourcePublic,
    status_code=status.HTTP_201_CREATED,
)
async def create_project_source(
    payload: SourceCreateRequest,
    project_id: UUID,
    principal: AuthenticationPrincipal = Depends(get_authenticated_principal),
    service: SourceService = Depends(get_source_service),
) -> SourcePublic:
    try:
        source = await service.create_source(principal, project_id, payload)
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from exc
    except DuplicateSourceError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Source already exists",
        ) from exc
    return SourcePublic.model_validate(source)


@router.get(
    "/projects/{project_id}/sources",
    response_model=list[SourcePublic],
)
async def list_project_sources(
    project_id: UUID,
    principal: AuthenticationPrincipal = Depends(get_authenticated_principal),
    service: SourceService = Depends(get_source_service),
) -> list[SourcePublic]:
    try:
        sources = await service.list_sources(principal, project_id)
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from exc
    return [SourcePublic.model_validate(source) for source in sources]


@router.get(
    "/projects/{project_id}/sources/{source_id}",
    response_model=SourcePublic,
)
async def get_project_source(
    project_id: UUID,
    source_id: UUID,
    principal: AuthenticationPrincipal = Depends(get_authenticated_principal),
    service: SourceService = Depends(get_source_service),
) -> SourcePublic:
    try:
        source = await service.get_source(principal, project_id, source_id)
    except (ProjectNotFoundError, SourceNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project source not found",
        ) from exc
    return SourcePublic.model_validate(source)


@router.patch(
    "/projects/{project_id}/sources/{source_id}",
    response_model=SourcePublic,
)
async def update_project_source(
    payload: SourceUpdateRequest,
    project_id: UUID,
    source_id: UUID,
    principal: AuthenticationPrincipal = Depends(get_authenticated_principal),
    service: SourceService = Depends(get_source_service),
) -> SourcePublic:
    try:
        source = await service.update_source(principal, project_id, source_id, payload)
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from exc
    except SourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project source not found",
        ) from exc
    except DuplicateSourceError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Source already exists",
        ) from exc
    return SourcePublic.model_validate(source)


@router.post(
    "/projects/{project_id}/evidence",
    response_model=EvidencePublic,
    status_code=status.HTTP_201_CREATED,
)
async def create_project_evidence(
    payload: EvidenceCreateRequest,
    project_id: UUID,
    principal: AuthenticationPrincipal = Depends(get_authenticated_principal),
    service: EvidenceService = Depends(get_evidence_service),
) -> EvidencePublic:
    try:
        evidence = await service.create_evidence(principal, project_id, payload)
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from exc
    except SourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project source not found",
        ) from exc
    return EvidencePublic.model_validate(evidence)


@router.get(
    "/projects/{project_id}/evidence",
    response_model=list[EvidencePublic],
)
async def list_project_evidence(
    project_id: UUID,
    principal: AuthenticationPrincipal = Depends(get_authenticated_principal),
    service: EvidenceService = Depends(get_evidence_service),
) -> list[EvidencePublic]:
    try:
        evidence_items = await service.list_evidence(principal, project_id)
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from exc
    return [EvidencePublic.model_validate(item) for item in evidence_items]


@router.get(
    "/projects/{project_id}/evidence/{evidence_id}",
    response_model=EvidencePublic,
)
async def get_project_evidence(
    project_id: UUID,
    evidence_id: UUID,
    principal: AuthenticationPrincipal = Depends(get_authenticated_principal),
    service: EvidenceService = Depends(get_evidence_service),
) -> EvidencePublic:
    try:
        evidence = await service.get_evidence(principal, project_id, evidence_id)
    except (ProjectNotFoundError, EvidenceNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project evidence not found",
        ) from exc
    return EvidencePublic.model_validate(evidence)


@router.patch(
    "/projects/{project_id}/evidence/{evidence_id}",
    response_model=EvidencePublic,
)
async def update_project_evidence(
    payload: EvidenceUpdateRequest,
    project_id: UUID,
    evidence_id: UUID,
    principal: AuthenticationPrincipal = Depends(get_authenticated_principal),
    service: EvidenceService = Depends(get_evidence_service),
) -> EvidencePublic:
    try:
        evidence = await service.update_evidence(principal, project_id, evidence_id, payload)
    except (ProjectNotFoundError, EvidenceNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project evidence not found",
        ) from exc
    return EvidencePublic.model_validate(evidence)


@router.post(
    "/projects/{project_id}/evidence/{evidence_id}/requirements",
    response_model=EvidenceRequirementLinkPublic,
    status_code=status.HTTP_201_CREATED,
)
async def link_project_evidence_requirement(
    payload: EvidenceRequirementLinkRequest,
    project_id: UUID,
    evidence_id: UUID,
    principal: AuthenticationPrincipal = Depends(get_authenticated_principal),
    service: EvidenceRequirementService = Depends(get_evidence_requirement_service),
) -> EvidenceRequirementLinkPublic:
    try:
        link = await service.link_evidence_to_requirement(principal, project_id, evidence_id, payload)
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from exc
    except SourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project source not found",
        ) from exc
    except EvidenceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project evidence not found",
        ) from exc
    except RequirementNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project requirement not found",
        ) from exc
    except DuplicateEvidenceRelationshipError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Evidence relationship already exists",
        ) from exc
    return EvidenceRequirementLinkPublic.model_validate(link)


@router.get(
    "/projects/{project_id}/evidence/{evidence_id}/requirements",
    response_model=list[EvidenceRequirementLinkPublic],
)
async def list_project_evidence_requirements(
    project_id: UUID,
    evidence_id: UUID,
    principal: AuthenticationPrincipal = Depends(get_authenticated_principal),
    service: EvidenceRequirementService = Depends(get_evidence_requirement_service),
) -> list[EvidenceRequirementLinkPublic]:
    try:
        requirements = await service.list_requirements_for_evidence(
            principal, project_id, evidence_id
        )
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from exc
    return [EvidenceRequirementLinkPublic.model_validate(requirement) for requirement in requirements]


@router.get(
    "/projects/{project_id}/requirements/{requirement_id}/evidence",
    response_model=list[EvidenceRequirementLinkPublic],
)
async def list_project_requirement_evidence(
    project_id: UUID,
    requirement_id: UUID,
    principal: AuthenticationPrincipal = Depends(get_authenticated_principal),
    service: EvidenceRequirementService = Depends(get_evidence_requirement_service),
) -> list[EvidenceRequirementLinkPublic]:
    try:
        evidence_requirements = await service.list_evidence_for_requirement(
            principal, project_id, requirement_id
        )
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from exc
    return [EvidenceRequirementLinkPublic.model_validate(link) for link in evidence_requirements]
