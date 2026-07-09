from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from intentforge_api.auth.schemas import AuthenticationPrincipal
from intentforge_api.projects.errors import (
    DuplicateEvidenceRelationshipError,
    DuplicateSourceError,
    ProjectNotFoundError,
    SourceNotFoundError,
)
from intentforge_api.projects.models import (
    EvidenceRequirementLink,
    Project,
    ProjectIntent,
    ProjectLifecycleStatus,
    Requirement,
    RequirementClassification,
    RequirementLifecycleStatus,
    RequirementPriority,
    SourceType,
)
from intentforge_api.projects.schemas import (
    EvidenceCreateRequest,
    EvidenceRequirementLinkRequest,
    ProjectCreateRequest,
    ProjectIntentRequest,
    ProjectUpdateRequest,
    RequirementCreateRequest,
    RequirementUpdateRequest,
    SourceCreateRequest,
)
from intentforge_api.projects.service import (
    EvidenceRequirementService,
    EvidenceService,
    ProjectService,
    SourceService,
)


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


class _FakeSourceRepository:
    def __init__(self):
        self.sources: list = []
        self.created = None
        self.saved = None

    async def get_source_by_locator(self, project_id, locator):
        for source in self.sources:
            if source.project_id == project_id and source.locator == locator:
                return source
        return None

    async def create_source(self, project_id, source_type, title, locator, observed_at=None):
        from intentforge_api.projects.models import Source

        source = Source(
            id=uuid4(),
            project_id=project_id,
            source_type=source_type,
            title=title,
            locator=locator,
            observed_at=observed_at,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        self.sources.append(source)
        self.created = source
        return source

    async def get_source_by_id(self, project_id, source_id):
        for source in self.sources:
            if source.project_id == project_id and source.id == source_id:
                return source
        return None

    async def save_source(self, source):
        self.saved = source
        return source


class _FakeEvidenceRepository:
    def __init__(self):
        self.evidence: list = []
        self.created = None
        self.saved = None

    async def create_evidence(self, project_id, source_id, claim, excerpt=None, source_location=None, observed_at=None):
        from intentforge_api.projects.models import Evidence

        evidence = Evidence(
            id=uuid4(),
            project_id=project_id,
            source_id=source_id,
            claim=claim,
            excerpt=excerpt,
            source_location=source_location,
            observed_at=observed_at,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        self.evidence.append(evidence)
        self.created = evidence
        return evidence

    async def get_evidence_by_id(self, project_id, evidence_id):
        for evidence in self.evidence:
            if evidence.project_id == project_id and evidence.id == evidence_id:
                return evidence
        return None

    async def list_evidence(self, project_id):
        return [item for item in self.evidence if item.project_id == project_id]

    async def save_evidence(self, evidence):
        self.saved = evidence
        return evidence


class _FakeEvidenceRequirementRepository:
    def __init__(self):
        self.links: list = []
        self.created = None

    async def find_link(self, project_id, evidence_id, requirement_id, relationship_type):
        for link in self.links:
            if (
                link.project_id == project_id
                and link.evidence_id == evidence_id
                and link.requirement_id == requirement_id
                and link.relationship_type == relationship_type
            ):
                return link
        return None

    async def create_evidence_requirement_link(self, project_id, evidence_id, requirement_id, relationship_type):
        link = EvidenceRequirementLink(
            id=uuid4(),
            project_id=project_id,
            evidence_id=evidence_id,
            requirement_id=requirement_id,
            relationship_type=relationship_type,
            created_at=datetime.now(UTC),
        )
        self.links.append(link)
        self.created = link
        return link

    async def list_requirements_for_evidence(self, project_id, evidence_id):
        return [link for link in self.links if link.project_id == project_id and link.evidence_id == evidence_id]

    async def list_evidence_for_requirement(self, project_id, requirement_id):
        return [link for link in self.links if link.project_id == project_id and link.requirement_id == requirement_id]


@pytest.mark.asyncio
async def test_create_source_returns_created_source() -> None:
    repository = _FakeProjectRepository()
    source_repository = _FakeSourceRepository()
    service = SourceService(
        source_repository=source_repository,
        project_repository=repository,
        session=_FakeSession(),
    )
    principal = build_principal()
    project = await repository.create(owner_id=principal.user.id, name="Owned project")
    payload = SourceCreateRequest(
        source_type=SourceType.DOCUMENT,
        title="Project source",
        locator="https://example.com/spec",
    )

    source = await service.create_source(principal, project.id, payload)

    assert source.title == "Project source"
    assert source.locator == "https://example.com/spec"
    assert source_repository.created is source


@pytest.mark.asyncio
async def test_create_source_raises_duplicate_source() -> None:
    repository = _FakeProjectRepository()
    source_repository = _FakeSourceRepository()
    service = SourceService(
        source_repository=source_repository,
        project_repository=repository,
        session=_FakeSession(),
    )
    principal = build_principal()
    project = await repository.create(owner_id=principal.user.id, name="Owned project")
    existing = await source_repository.create_source(
        project_id=project.id,
        source_type=SourceType.DOCUMENT.value,
        title="Existing source",
        locator="https://example.com/spec",
    )
    payload = SourceCreateRequest(
        source_type=SourceType.DOCUMENT,
        title="Duplicate source",
        locator=existing.locator,
    )

    with pytest.raises(DuplicateSourceError):
        await service.create_source(principal, project.id, payload)


@pytest.mark.asyncio
async def test_create_evidence_requires_existing_source() -> None:
    repository = _FakeProjectRepository()
    source_repository = _FakeSourceRepository()
    evidence_repository = _FakeEvidenceRepository()
    service = EvidenceService(
        evidence_repository=evidence_repository,
        source_repository=source_repository,
        project_repository=repository,
        session=_FakeSession(),
    )
    principal = build_principal()
    project = await repository.create(owner_id=principal.user.id, name="Owned project")
    payload = EvidenceCreateRequest(
        source_id=uuid4(),
        claim="A relevant claim",
    )

    with pytest.raises(SourceNotFoundError):
        await service.create_evidence(principal, project.id, payload)


@pytest.mark.asyncio
async def test_link_evidence_to_requirement_creates_relationship() -> None:
    repository = _FakeProjectRepository()
    source_repository = _FakeSourceRepository()
    evidence_repository = _FakeEvidenceRepository()
    record_repository = _FakeEvidenceRequirementRepository()
    service = EvidenceRequirementService(
        record_repository=record_repository,
        evidence_repository=evidence_repository,
        project_repository=repository,
        session=_FakeSession(),
    )
    principal = build_principal()
    project = await repository.create(owner_id=principal.user.id, name="Owned project")
    source = await source_repository.create_source(
        project_id=project.id,
        source_type=SourceType.DOCUMENT.value,
        title="Project source",
        locator="https://example.com/spec",
    )
    evidence = await evidence_repository.create_evidence(
        project_id=project.id,
        source_id=source.id,
        claim="A supporting claim",
    )
    requirement = await repository.create_requirement(
        project_id=project.id,
        title="Need it",
        description="Must be tracked",
        classification=RequirementClassification.FUNCTIONAL.value,
        priority=RequirementPriority.MEDIUM.value,
        lifecycle_status=RequirementLifecycleStatus.ACTIVE.value,
    )
    payload = EvidenceRequirementLinkRequest(
        requirement_id=requirement.id,
        relationship_type="supports",
    )

    link = await service.link_evidence_to_requirement(principal, project.id, evidence.id, payload)

    assert link.evidence_id == evidence.id
    assert link.requirement_id == requirement.id
    assert link.relationship_type == "supports"


@pytest.mark.asyncio
async def test_link_evidence_to_requirement_raises_duplicate() -> None:
    repository = _FakeProjectRepository()
    source_repository = _FakeSourceRepository()
    evidence_repository = _FakeEvidenceRepository()
    record_repository = _FakeEvidenceRequirementRepository()
    service = EvidenceRequirementService(
        record_repository=record_repository,
        evidence_repository=evidence_repository,
        project_repository=repository,
        session=_FakeSession(),
    )
    principal = build_principal()
    project = await repository.create(owner_id=principal.user.id, name="Owned project")
    source = await source_repository.create_source(
        project_id=project.id,
        source_type=SourceType.DOCUMENT.value,
        title="Project source",
        locator="https://example.com/spec",
    )
    evidence = await evidence_repository.create_evidence(
        project_id=project.id,
        source_id=source.id,
        claim="A supporting claim",
    )
    requirement = await repository.create_requirement(
        project_id=project.id,
        title="Need it",
        description="Must be tracked",
        classification=RequirementClassification.FUNCTIONAL.value,
        priority=RequirementPriority.MEDIUM.value,
        lifecycle_status=RequirementLifecycleStatus.ACTIVE.value,
    )
    payload = EvidenceRequirementLinkRequest(
        requirement_id=requirement.id,
        relationship_type="supports",
    )

    await service.link_evidence_to_requirement(principal, project.id, evidence.id, payload)

    with pytest.raises(DuplicateEvidenceRelationshipError):
        await service.link_evidence_to_requirement(principal, project.id, evidence.id, payload)
