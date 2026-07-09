from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from intentforge_api.auth.schemas import AuthenticationPrincipal
from intentforge_api.projects.errors import ProjectNotFoundError
from intentforge_api.projects.models import (
    Project,
    ProjectIntent,
    ProjectLifecycleStatus,
    Requirement,
    RequirementClassification,
    RequirementPriority,
)
from intentforge_api.projects.schemas import (
    ProjectCreateRequest,
    ProjectIntentRequest,
    ProjectUpdateRequest,
    RequirementCreateRequest,
    RequirementUpdateRequest,
)
from intentforge_api.projects.service import ProjectService


class _NoopTransaction:
    async def __aenter__(self):
        return None

    async def __aexit__(self, exc_type, exc, traceback):
        return None


class _FakeSession:
    def __init__(self):
        self.began = False

    def begin(self):
        self.began = True
        return _NoopTransaction()


class _FakeProjectRepository:
    def __init__(self, project: Project | None = None):
        self.project = project
        self.saved = None
        self.created = None
        self.listed_owner = None
        self.intent: ProjectIntent | None = None
        self.requirements: list[Requirement] = []

    async def create(self, *, owner_id, name):
        self.created = (owner_id, name)
        now = datetime.now(UTC)
        self.project = Project(
            id=uuid4(),
            owner_id=owner_id,
            name=name,
            lifecycle_status=ProjectLifecycleStatus.ACTIVE.value,
            created_at=now,
            updated_at=now,
        )
        return self.project

    async def list_owned(self, *, owner_id):
        self.listed_owner = owner_id
        return [self.project] if self.project is not None else []

    async def find_owned_by_id(self, *, owner_id, project_id):
        if self.project is None or self.project.id != project_id or self.project.owner_id != owner_id:
            return None
        return self.project

    async def save(self, project):
        self.saved = project
        return project

    async def get_intent_by_project_id(self, project_id):
        return self.intent if self.intent is not None and self.intent.project_id == project_id else None

    async def create_intent_for_project(
        self,
        project_id,
        problem_statement=None,
        desired_outcome=None,
        goals=None,
        non_goals=None,
        constraints=None,
        success_criteria=None,
    ):
        now = datetime.now(UTC)
        self.intent = ProjectIntent(
            id=uuid4(),
            project_id=project_id,
            problem_statement=problem_statement,
            desired_outcome=desired_outcome,
            goals=goals,
            non_goals=non_goals,
            constraints=constraints,
            success_criteria=success_criteria,
            created_at=now,
            updated_at=now,
        )
        return self.intent

    async def save_intent(self, intent):
        self.intent = intent
        return intent

    async def create_requirement(
        self,
        project_id,
        title,
        description,
        classification,
        priority,
        lifecycle_status,
    ):
        requirement = Requirement(
            id=uuid4(),
            project_id=project_id,
            title=title,
            description=description,
            classification=classification,
            priority=priority,
            lifecycle_status=lifecycle_status,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        self.requirements.append(requirement)
        return requirement

    async def list_requirements(self, *, project_id):
        return [requirement for requirement in self.requirements if requirement.project_id == project_id]

    async def get_requirement_by_id(self, *, project_id, requirement_id):
        for requirement in self.requirements:
            if requirement.project_id == project_id and requirement.id == requirement_id:
                return requirement
        return None

    async def save_requirement(self, requirement):
        self.saved = requirement
        return requirement


def build_principal():
    from intentforge_api.auth.models import User

    now = datetime.now(UTC)
    user = User(
        id=uuid4(),
        email="admin@example.com",
        password_hash="hash",
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    return AuthenticationPrincipal(
        user=user,
        token_subject=user.id,
        token_type="access",
        token_expires_at=now,
    )


@pytest.mark.asyncio
async def test_create_project_returns_created_project() -> None:
    repository = _FakeProjectRepository()
    service = ProjectService(repository=repository, session=_FakeSession())
    principal = build_principal()
    payload = ProjectCreateRequest(name="New project")

    project = await service.create_project(principal, payload)

    assert project.name == "New project"
    assert project.owner_id == principal.user.id
    assert repository.created == (principal.user.id, "New project")


@pytest.mark.asyncio
async def test_list_projects_returns_owned_projects() -> None:
    repository = _FakeProjectRepository()
    service = ProjectService(repository=repository, session=_FakeSession())
    principal = build_principal()

    projects = await service.list_projects(principal)

    assert projects == []
    assert repository.listed_owner == principal.user.id


@pytest.mark.asyncio
async def test_get_project_raises_not_found_when_missing() -> None:
    repository = _FakeProjectRepository()
    service = ProjectService(repository=repository, session=_FakeSession())
    principal = build_principal()

    with pytest.raises(ProjectNotFoundError):
        await service.get_project(principal, uuid4())


@pytest.mark.asyncio
async def test_update_project_saves_and_returns_project() -> None:
    repository = _FakeProjectRepository()
    service = ProjectService(repository=repository, session=_FakeSession())
    principal = build_principal()
    existing_project = await repository.create(owner_id=principal.user.id, name="Old name")

    payload = ProjectUpdateRequest(name="Updated project")
    project = await service.update_project(principal, existing_project.id, payload)

    assert project.name == "Updated project"
    assert repository.saved is project


@pytest.mark.asyncio
async def test_update_project_raises_not_found_when_missing() -> None:
    repository = _FakeProjectRepository()
    service = ProjectService(repository=repository, session=_FakeSession())
    principal = build_principal()

    with pytest.raises(ProjectNotFoundError):
        await service.update_project(principal, uuid4(), ProjectUpdateRequest(name="Any"))


@pytest.mark.asyncio
async def test_upsert_project_intent_creates_intent() -> None:
    repository = _FakeProjectRepository()
    principal = build_principal()
    existing_project = await repository.create(owner_id=principal.user.id, name="Old name")
    service = ProjectService(repository=repository, session=_FakeSession())
    payload = ProjectIntentRequest(problem_statement="Describe problem")

    intent = await service.upsert_project_intent(principal, existing_project.id, payload)

    assert intent.project_id == existing_project.id
    assert intent.problem_statement == "Describe problem"


@pytest.mark.asyncio
async def test_get_project_intent_raises_not_found_when_missing() -> None:
    repository = _FakeProjectRepository()
    service = ProjectService(repository=repository, session=_FakeSession())
    principal = build_principal()

    with pytest.raises(ProjectNotFoundError):
        await service.get_project_intent(principal, uuid4())


@pytest.mark.asyncio
async def test_create_requirement_returns_requirement() -> None:
    repository = _FakeProjectRepository()
    principal = build_principal()
    existing_project = await repository.create(owner_id=principal.user.id, name="Old name")
    service = ProjectService(repository=repository, session=_FakeSession())
    payload = RequirementCreateRequest(
        title="Need feature",
        description="Detailed requirement description",
        classification=RequirementClassification.FUNCTIONAL,
        priority=RequirementPriority.HIGH,
    )

    requirement = await service.create_requirement(principal, existing_project.id, payload)

    assert requirement.project_id == existing_project.id
    assert requirement.title == "Need feature"
    assert requirement.priority == RequirementPriority.HIGH.value


@pytest.mark.asyncio
async def test_list_requirements_returns_empty_list_when_no_requirements() -> None:
    repository = _FakeProjectRepository()
    principal = build_principal()
    existing_project = await repository.create(owner_id=principal.user.id, name="Old name")
    service = ProjectService(repository=repository, session=_FakeSession())

    requirements = await service.list_requirements(principal, existing_project.id)

    assert requirements == []


@pytest.mark.asyncio
async def test_get_requirement_raises_not_found_when_missing() -> None:
    repository = _FakeProjectRepository()
    principal = build_principal()
    await repository.create(owner_id=principal.user.id, name="Old name")
    service = ProjectService(repository=repository, session=_FakeSession())

    with pytest.raises(ProjectNotFoundError):
        await service.get_requirement(principal, uuid4(), uuid4())


@pytest.mark.asyncio
async def test_update_requirement_raises_not_found_when_missing() -> None:
    repository = _FakeProjectRepository()
    principal = build_principal()
    await repository.create(owner_id=principal.user.id, name="Old name")
    service = ProjectService(repository=repository, session=_FakeSession())

    with pytest.raises(ProjectNotFoundError):
        await service.update_requirement(
            principal,
            uuid4(),
            uuid4(),
            RequirementUpdateRequest(title="Updated"),
        )
