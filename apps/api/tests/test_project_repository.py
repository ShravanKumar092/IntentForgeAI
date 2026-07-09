from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from intentforge_api.projects.models import (
    Project,
    ProjectIntent,
    ProjectLifecycleStatus,
    Requirement,
    RequirementLifecycleStatus,
)
from intentforge_api.projects.repository import SqlAlchemyProjectRepository


class _Result:
    def __init__(self, scalar=None, all_items=None):
        self._scalar = scalar
        self._all_items = all_items or []

    def scalars(self):
        return self

    def all(self):
        return self._all_items

    def scalar_one_or_none(self):
        return self._scalar


class _Session:
    def __init__(self, result=None):
        self.result = result
        self.added = []
        self.flushed = False
        self.refreshed = []
        self.executed = []

    async def execute(self, statement):
        self.executed.append(statement)
        return _Result(scalar=self.result, all_items=[self.result] if self.result is not None else [])

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        self.flushed = True

    async def refresh(self, obj):
        self.refreshed.append(obj)


@pytest.mark.asyncio
async def test_repository_create_adds_and_refreshes_project() -> None:
    session = _Session()
    repository = SqlAlchemyProjectRepository(session)

    project = await repository.create(owner_id=uuid4(), name="Important project")

    assert project.name == "Important project"
    assert project.owner_id is not None
    assert project.lifecycle_status == ProjectLifecycleStatus.ACTIVE.value
    assert session.added[0] is project
    assert session.flushed is True
    assert session.refreshed[0] is project


@pytest.mark.asyncio
async def test_repository_list_owned_returns_ordered_projects() -> None:
    project = Project(
        id=uuid4(),
        owner_id=uuid4(),
        name="Owned project",
        lifecycle_status=ProjectLifecycleStatus.ACTIVE.value,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    session = _Session(result=project)
    repository = SqlAlchemyProjectRepository(session)

    projects = await repository.list_owned(owner_id=project.owner_id)

    assert projects == [project]
    assert len(session.executed) == 1


@pytest.mark.asyncio
async def test_repository_find_owned_by_id_returns_project_or_none() -> None:
    project_id = uuid4()
    owner_id = uuid4()
    project = Project(
        id=project_id,
        owner_id=owner_id,
        name="Owned project",
        lifecycle_status=ProjectLifecycleStatus.ACTIVE.value,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    session = _Session(result=project)
    repository = SqlAlchemyProjectRepository(session)

    found = await repository.find_owned_by_id(owner_id=owner_id, project_id=project_id)

    assert found is project
    assert session.executed


@pytest.mark.asyncio
async def test_repository_save_refreshes_project() -> None:
    project = Project(
        id=uuid4(),
        owner_id=uuid4(),
        name="Saved project",
        lifecycle_status=ProjectLifecycleStatus.ACTIVE.value,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    session = _Session()
    repository = SqlAlchemyProjectRepository(session)

    result = await repository.save(project)

    assert result is project
    assert session.flushed is True
    assert session.refreshed[0] is project


@pytest.mark.asyncio
async def test_repository_get_intent_by_project_id_returns_intent_or_none() -> None:
    intent = ProjectIntent(
        id=uuid4(),
        project_id=uuid4(),
        problem_statement="Problem",
        desired_outcome=None,
        goals=None,
        non_goals=None,
        constraints=None,
        success_criteria=None,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    session = _Session(result=intent)
    repository = SqlAlchemyProjectRepository(session)

    found = await repository.get_intent_by_project_id(intent.project_id)

    assert found is intent


@pytest.mark.asyncio
async def test_repository_create_intent_for_project_adds_and_refreshes_intent() -> None:
    session = _Session()
    repository = SqlAlchemyProjectRepository(session)

    intent = await repository.create_intent_for_project(
        project_id=uuid4(),
        problem_statement="Problem",
        desired_outcome="Outcome",
    )

    assert intent.problem_statement == "Problem"
    assert intent.desired_outcome == "Outcome"
    assert session.added[0] is intent
    assert session.flushed is True
    assert session.refreshed[0] is intent


@pytest.mark.asyncio
async def test_repository_list_requirements_returns_ordered_requirements() -> None:
    requirement = Requirement(
        id=uuid4(),
        project_id=uuid4(),
        title="Requirement title",
        description="Description",
        classification="functional",
        priority="medium",
        lifecycle_status=RequirementLifecycleStatus.ACTIVE.value,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    session = _Session(result=requirement)
    repository = SqlAlchemyProjectRepository(session)

    requirements = await repository.list_requirements(project_id=requirement.project_id)

    assert requirements == [requirement]


@pytest.mark.asyncio
async def test_repository_get_requirement_by_id_returns_requirement_or_none() -> None:
    requirement = Requirement(
        id=uuid4(),
        project_id=uuid4(),
        title="Requirement title",
        description="Description",
        classification="functional",
        priority="medium",
        lifecycle_status=RequirementLifecycleStatus.ACTIVE.value,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    session = _Session(result=requirement)
    repository = SqlAlchemyProjectRepository(session)

    found = await repository.get_requirement_by_id(
        project_id=requirement.project_id,
        requirement_id=requirement.id,
    )

    assert found is requirement
