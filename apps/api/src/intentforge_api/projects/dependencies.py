from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from intentforge_api.db.session import get_async_session
from intentforge_api.projects.repository import SqlAlchemyProjectRepository
from intentforge_api.projects.service import ProjectService


def get_project_service(
    session: AsyncSession = Depends(get_async_session),
) -> ProjectService:
    repository = SqlAlchemyProjectRepository(session)
    return ProjectService(repository=repository, session=session)
