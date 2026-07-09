from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from intentforge_api.auth.dependencies import get_authenticated_principal
from intentforge_api.auth.models import User
from intentforge_api.auth.schemas import AuthenticationPrincipal
from intentforge_api.main import create_app
from intentforge_api.projects.dependencies import (
    get_evidence_requirement_service,
    get_evidence_service,
    get_project_service,
    get_source_service,
)
from intentforge_api.projects.errors import ProjectNotFoundError
from intentforge_api.projects.models import (
    Project,
    ProjectIntent,
    ProjectLifecycleStatus,
    Requirement,
    RequirementClassification,
    RequirementLifecycleStatus,
    RequirementPriority,
)
from intentforge_api.core.config import Settings


class _FakeProjectService:
    def __init__(self, project: Project | None = None):
        self.project = project
        self.intent: ProjectIntent | None = None
        self.requirements: list[Requirement] = []
        self.created_payload = None
        self.updated_payload = None
        self.requested_project_id = None

    async def create_project(self, principal, payload):
        self.created_payload = payload
        now = datetime.now(UTC)
        self.project = Project(
            id=uuid4(),
            owner_id=principal.user.id,
            name=payload.name,
            lifecycle_status=ProjectLifecycleStatus.ACTIVE.value,
            created_at=now,
            updated_at=now,
        )
        return self.project

    async def list_projects(self, principal):
        return [self.project] if self.project is not None else []

    async def get_project(self, principal, project_id):
        self.requested_project_id = project_id
        if self.project is None or self.project.id != project_id:
            raise ProjectNotFoundError("project not found")
        return self.project

    async def update_project(self, principal, project_id, payload):
        self.requested_project_id = project_id
        if self.project is None or self.project.id != project_id:
            raise ProjectNotFoundError("project not found")
        self.project.name = payload.name
        self.updated_payload = payload
        return self.project

    async def get_project_intent(self, principal, project_id):
        if self.project is None or self.project.id != project_id:
            raise ProjectNotFoundError("project not found")
        if self.intent is None:
            from intentforge_api.projects.errors import ProjectIntentNotFoundError

            raise ProjectIntentNotFoundError("project intent not found")
        return self.intent

    async def upsert_project_intent(self, principal, project_id, payload):
        if self.project is None or self.project.id != project_id:
            raise ProjectNotFoundError("project not found")
        now = datetime.now(UTC)
        if self.intent is None:
            self.intent = ProjectIntent(
                id=uuid4(),
                project_id=project_id,
                problem_statement=payload.problem_statement,
                desired_outcome=payload.desired_outcome,
                goals=payload.goals,
                non_goals=payload.non_goals,
                constraints=payload.constraints,
                success_criteria=payload.success_criteria,
                created_at=now,
                updated_at=now,
            )
        else:
            self.intent.problem_statement = payload.problem_statement
            self.intent.desired_outcome = payload.desired_outcome
            self.intent.goals = payload.goals
            self.intent.non_goals = payload.non_goals
            self.intent.constraints = payload.constraints
            self.intent.success_criteria = payload.success_criteria
            self.intent.updated_at = now
        return self.intent

    async def list_requirements(self, principal, project_id):
        if self.project is None or self.project.id != project_id:
            raise ProjectNotFoundError("project not found")
        return self.requirements

    async def create_requirement(self, principal, project_id, payload):
        if self.project is None or self.project.id != project_id:
            raise ProjectNotFoundError("project not found")
        requirement = Requirement(
            id=uuid4(),
            project_id=project_id,
            title=payload.title,
            description=payload.description,
            classification=payload.classification.value,
            priority=payload.priority.value,
            lifecycle_status=RequirementLifecycleStatus.ACTIVE.value,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        self.requirements.append(requirement)
        return requirement

    async def get_requirement(self, principal, project_id, requirement_id):
        if self.project is None or self.project.id != project_id:
            raise ProjectNotFoundError("project not found")
        for requirement in self.requirements:
            if requirement.id == requirement_id:
                return requirement
        from intentforge_api.projects.errors import RequirementNotFoundError

        raise RequirementNotFoundError("requirement not found")

    async def update_requirement(self, principal, project_id, requirement_id, payload):
        requirement = await self.get_requirement(principal, project_id, requirement_id)
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
        requirement.updated_at = datetime.now(UTC)
        return requirement


def build_settings() -> Settings:
    return Settings(
        _env_file=None,
        app_environment="testing",
        app_debug=False,
        token_signing_secret="super-secret-super-secret-super-secret",
        token_issuer="intentforge-api",
        token_audience="intentforge-api",
    )


def build_client() -> TestClient:
    return TestClient(create_app(build_settings()))


def build_principal() -> AuthenticationPrincipal:
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


def test_create_project_route_returns_created_project() -> None:
    client = build_client()
    service = _FakeProjectService()
    principal = build_principal()
    client.app.dependency_overrides[get_authenticated_principal] = lambda: principal
    client.app.dependency_overrides[get_project_service] = lambda: service

    response = client.post(
        "/api/v1/projects",
        json={"name": "Important project"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "Important project"
    assert payload["lifecycle_status"] == "active"
    assert payload["id"]

    client.app.dependency_overrides.clear()


def test_list_projects_route_returns_owned_projects() -> None:
    client = build_client()
    project = Project(
        id=uuid4(),
        owner_id=uuid4(),
        name="Owned project",
        lifecycle_status=ProjectLifecycleStatus.ACTIVE.value,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    service = _FakeProjectService(project=project)
    principal = build_principal()
    client.app.dependency_overrides[get_authenticated_principal] = lambda: principal
    client.app.dependency_overrides[get_project_service] = lambda: service

    response = client.get("/api/v1/projects")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) == 1
    project_payload = payload[0]
    assert project_payload["id"] == str(project.id)
    assert project_payload["name"] == "Owned project"
    assert project_payload["lifecycle_status"] == "active"
    assert project_payload["created_at"]
    assert project_payload["updated_at"]

    client.app.dependency_overrides.clear()


def test_get_project_route_returns_project() -> None:
    client = build_client()
    project = Project(
        id=uuid4(),
        owner_id=uuid4(),
        name="Owned project",
        lifecycle_status=ProjectLifecycleStatus.ACTIVE.value,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    service = _FakeProjectService(project=project)
    principal = build_principal()
    client.app.dependency_overrides[get_authenticated_principal] = lambda: principal
    client.app.dependency_overrides[get_project_service] = lambda: service

    response = client.get(f"/api/v1/projects/{project.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(project.id)
    assert response.json()["name"] == "Owned project"

    client.app.dependency_overrides.clear()


def test_update_project_route_returns_updated_project() -> None:
    client = build_client()
    project = Project(
        id=uuid4(),
        owner_id=uuid4(),
        name="Owned project",
        lifecycle_status=ProjectLifecycleStatus.ACTIVE.value,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    service = _FakeProjectService(project=project)
    principal = build_principal()
    client.app.dependency_overrides[get_authenticated_principal] = lambda: principal
    client.app.dependency_overrides[get_project_service] = lambda: service

    response = client.patch(
        f"/api/v1/projects/{project.id}",
        json={"name": "Updated project"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated project"
    assert service.updated_payload.name == "Updated project"

    client.app.dependency_overrides.clear()


def test_get_project_route_returns_404_for_unauthorized_project() -> None:
    client = build_client()
    service = _FakeProjectService()
    principal = build_principal()
    client.app.dependency_overrides[get_authenticated_principal] = lambda: principal
    client.app.dependency_overrides[get_project_service] = lambda: service

    response = client.get(f"/api/v1/projects/{uuid4()}")

    assert response.status_code == 404

    client.app.dependency_overrides.clear()


def test_upsert_project_intent_route_creates_intent() -> None:
    client = build_client()
    project = Project(
        id=uuid4(),
        owner_id=uuid4(),
        name="Owned project",
        lifecycle_status=ProjectLifecycleStatus.ACTIVE.value,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    service = _FakeProjectService(project=project)
    principal = build_principal()
    client.app.dependency_overrides[get_authenticated_principal] = lambda: principal
    client.app.dependency_overrides[get_project_service] = lambda: service

    response = client.post(
        f"/api/v1/projects/{project.id}/intent",
        json={
            "problem_statement": "A clear problem",
            "desired_outcome": "Solve it",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["project_id"] == str(project.id)
    assert payload["problem_statement"] == "A clear problem"
    assert payload["desired_outcome"] == "Solve it"

    client.app.dependency_overrides.clear()


def test_list_project_requirements_route_returns_expected_items() -> None:
    project = Project(
        id=uuid4(),
        owner_id=uuid4(),
        name="Owned project",
        lifecycle_status=ProjectLifecycleStatus.ACTIVE.value,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    requirement = Requirement(
        id=uuid4(),
        project_id=project.id,
        title="Requirement title",
        description="Requirement description",
        classification=RequirementClassification.FUNCTIONAL.value,
        priority=RequirementPriority.MEDIUM.value,
        lifecycle_status=RequirementLifecycleStatus.ACTIVE.value,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    service = _FakeProjectService(project=project)
    service.requirements = [requirement]
    principal = build_principal()
    client = build_client()
    client.app.dependency_overrides[get_authenticated_principal] = lambda: principal
    client.app.dependency_overrides[get_project_service] = lambda: service

    response = client.get(f"/api/v1/projects/{project.id}/requirements")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload[0]["id"] == str(requirement.id)
    assert payload[0]["title"] == "Requirement title"

    client.app.dependency_overrides.clear()


def test_create_project_requirement_route_returns_created_requirement() -> None:
    project = Project(
        id=uuid4(),
        owner_id=uuid4(),
        name="Owned project",
        lifecycle_status=ProjectLifecycleStatus.ACTIVE.value,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    service = _FakeProjectService(project=project)
    principal = build_principal()
    client = build_client()
    client.app.dependency_overrides[get_authenticated_principal] = lambda: principal
    client.app.dependency_overrides[get_project_service] = lambda: service

    response = client.post(
        f"/api/v1/projects/{project.id}/requirements",
        json={
            "title": "Requirement title",
            "description": "Requirement description",
            "classification": "functional",
            "priority": "high",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["title"] == "Requirement title"
    assert payload["priority"] == "high"
    assert payload["lifecycle_status"] == "active"

    client.app.dependency_overrides.clear()


def test_get_project_requirement_route_returns_requirement() -> None:
    project = Project(
        id=uuid4(),
        owner_id=uuid4(),
        name="Owned project",
        lifecycle_status=ProjectLifecycleStatus.ACTIVE.value,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    requirement = Requirement(
        id=uuid4(),
        project_id=project.id,
        title="Requirement title",
        description="Requirement description",
        classification=RequirementClassification.FUNCTIONAL.value,
        priority=RequirementPriority.MEDIUM.value,
        lifecycle_status=RequirementLifecycleStatus.ACTIVE.value,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    service = _FakeProjectService(project=project)
    service.requirements = [requirement]
    principal = build_principal()
    client = build_client()
    client.app.dependency_overrides[get_authenticated_principal] = lambda: principal
    client.app.dependency_overrides[get_project_service] = lambda: service

    response = client.get(f"/api/v1/projects/{project.id}/requirements/{requirement.id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == str(requirement.id)
    assert payload["title"] == "Requirement title"

    client.app.dependency_overrides.clear()


def test_update_project_requirement_route_updates_requirement() -> None:
    project = Project(
        id=uuid4(),
        owner_id=uuid4(),
        name="Owned project",
        lifecycle_status=ProjectLifecycleStatus.ACTIVE.value,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    requirement = Requirement(
        id=uuid4(),
        project_id=project.id,
        title="Requirement title",
        description="Requirement description",
        classification=RequirementClassification.FUNCTIONAL.value,
        priority=RequirementPriority.MEDIUM.value,
        lifecycle_status=RequirementLifecycleStatus.ACTIVE.value,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    service = _FakeProjectService(project=project)
    service.requirements = [requirement]
    principal = build_principal()
    client = build_client()
    client.app.dependency_overrides[get_authenticated_principal] = lambda: principal
    client.app.dependency_overrides[get_project_service] = lambda: service

    response = client.patch(
        f"/api/v1/projects/{project.id}/requirements/{requirement.id}",
        json={"title": "Updated title"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "Updated title"

    client.app.dependency_overrides.clear()


class _FakeSourceService:
    def __init__(self, source=None):
        self.source = source
        self.sources = [source] if source is not None else []
        self.created_payload = None
        self.updated_payload = None

    async def create_source(self, principal, project_id, payload):
        self.created_payload = payload
        from intentforge_api.projects.models import Source

        source = Source(
            id=uuid4(),
            project_id=project_id,
            source_type=payload.source_type.value,
            title=payload.title,
            locator=payload.locator,
            observed_at=payload.observed_at,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        self.sources.append(source)
        return source

    async def list_sources(self, principal, project_id):
        return [source for source in self.sources if source.project_id == project_id]

    async def get_source(self, principal, project_id, source_id):
        for source in self.sources:
            if source.project_id == project_id and source.id == source_id:
                return source
        from intentforge_api.projects.errors import SourceNotFoundError

        raise SourceNotFoundError("source not found")

    async def update_source(self, principal, project_id, source_id, payload):
        for source in self.sources:
            if source.project_id == project_id and source.id == source_id:
                if payload.title is not None:
                    source.title = payload.title
                if payload.locator is not None:
                    source.locator = payload.locator
                if payload.observed_at is not None:
                    source.observed_at = payload.observed_at
                self.updated_payload = payload
                return source
        from intentforge_api.projects.errors import SourceNotFoundError

        raise SourceNotFoundError("source not found")


class _FakeEvidenceService:
    def __init__(self, evidence=None):
        self.evidence = evidence
        self.evidence_items = [evidence] if evidence is not None else []
        self.created_payload = None
        self.updated_payload = None

    async def create_evidence(self, principal, project_id, payload):
        self.created_payload = payload
        from intentforge_api.projects.models import Evidence

        evidence = Evidence(
            id=uuid4(),
            project_id=project_id,
            source_id=payload.source_id,
            claim=payload.claim,
            excerpt=payload.excerpt,
            source_location=payload.source_location,
            observed_at=payload.observed_at,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        self.evidence_items.append(evidence)
        return evidence

    async def list_evidence(self, principal, project_id):
        return [item for item in self.evidence_items if item.project_id == project_id]

    async def get_evidence(self, principal, project_id, evidence_id):
        for evidence in self.evidence_items:
            if evidence.project_id == project_id and evidence.id == evidence_id:
                return evidence
        from intentforge_api.projects.errors import EvidenceNotFoundError

        raise EvidenceNotFoundError("evidence not found")

    async def update_evidence(self, principal, project_id, evidence_id, payload):
        for evidence in self.evidence_items:
            if evidence.project_id == project_id and evidence.id == evidence_id:
                if payload.claim is not None:
                    evidence.claim = payload.claim
                if payload.excerpt is not None:
                    evidence.excerpt = payload.excerpt
                if payload.source_location is not None:
                    evidence.source_location = payload.source_location
                if payload.observed_at is not None:
                    evidence.observed_at = payload.observed_at
                self.updated_payload = payload
                return evidence
        from intentforge_api.projects.errors import EvidenceNotFoundError

        raise EvidenceNotFoundError("evidence not found")


class _FakeEvidenceRequirementService:
    def __init__(self, links=None):
        self.links = links or []
        self.created_payload = None

    async def link_evidence_to_requirement(self, principal, project_id, evidence_id, payload):
        from intentforge_api.projects.models import EvidenceRequirementLink

        link = EvidenceRequirementLink(
            id=uuid4(),
            project_id=project_id,
            evidence_id=evidence_id,
            requirement_id=payload.requirement_id,
            relationship_type=payload.relationship_type.value,
            created_at=datetime.now(UTC),
        )
        self.links.append(link)
        self.created_payload = payload
        return link

    async def list_requirements_for_evidence(self, principal, project_id, evidence_id):
        return [link for link in self.links if link.project_id == project_id and link.evidence_id == evidence_id]

    async def list_evidence_for_requirement(self, principal, project_id, requirement_id):
        return [link for link in self.links if link.project_id == project_id and link.requirement_id == requirement_id]


def test_create_project_source_route_returns_created_source() -> None:
    client = build_client()
    service = _FakeSourceService()
    principal = build_principal()
    client.app.dependency_overrides[get_authenticated_principal] = lambda: principal
    client.app.dependency_overrides[get_source_service] = lambda: service

    response = client.post(
        "/api/v1/projects/{}/sources".format(uuid4()),
        json={
            "source_type": "document",
            "title": "Project source",
            "locator": "https://example.com/spec",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["source_type"] == "document"
    assert payload["locator"] == "https://example.com/spec"

    client.app.dependency_overrides.clear()


def test_create_project_evidence_route_returns_created_evidence() -> None:
    client = build_client()
    service = _FakeEvidenceService()
    principal = build_principal()
    client.app.dependency_overrides[get_authenticated_principal] = lambda: principal
    client.app.dependency_overrides[get_evidence_service] = lambda: service

    response = client.post(
        "/api/v1/projects/{}/evidence".format(uuid4()),
        json={
            "source_id": str(uuid4()),
            "claim": "A clear claim",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["claim"] == "A clear claim"

    client.app.dependency_overrides.clear()


def test_link_project_evidence_requirement_route_returns_link() -> None:
    project_id = uuid4()
    evidence_id = uuid4()
    client = build_client()
    service = _FakeEvidenceRequirementService()
    principal = build_principal()
    client.app.dependency_overrides[get_authenticated_principal] = lambda: principal
    client.app.dependency_overrides[get_evidence_requirement_service] = lambda: service

    response = client.post(
        f"/api/v1/projects/{project_id}/evidence/{evidence_id}/requirements",
        json={
            "requirement_id": str(uuid4()),
            "relationship_type": "supports",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["evidence_id"] == str(evidence_id)
    assert payload["relationship_type"] == "supports"

    client.app.dependency_overrides.clear()
