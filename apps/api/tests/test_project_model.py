from uuid import uuid4

from intentforge_api.projects.models import Project, ProjectLifecycleStatus


def test_project_lifecycle_status_enum_values() -> None:
    assert list(ProjectLifecycleStatus) == [
        ProjectLifecycleStatus.ACTIVE,
        ProjectLifecycleStatus.ARCHIVED,
    ]


def test_project_default_lifecycle_status_is_active() -> None:
    project = Project(
        owner_id=uuid4(),
        name="Example Project",
        lifecycle_status=ProjectLifecycleStatus.ACTIVE.value,
    )

    assert project.lifecycle_status == ProjectLifecycleStatus.ACTIVE.value
    assert str(project.lifecycle_status) == "active"
