from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from intentforge_api.auth.dependencies import get_authenticated_principal
from intentforge_api.auth.schemas import AuthenticationPrincipal
from intentforge_api.projects.dependencies import get_project_service
from intentforge_api.projects.errors import (
    ProjectIntentNotFoundError,
    ProjectNotFoundError,
    RequirementNotFoundError,
)
from intentforge_api.projects.schemas import (
    ProjectCreateRequest,
    ProjectIntentPublic,
    ProjectIntentRequest,
    ProjectPublic,
    ProjectUpdateRequest,
    RequirementCreateRequest,
    RequirementPublic,
    RequirementUpdateRequest,
)
from intentforge_api.projects.service import ProjectService


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
