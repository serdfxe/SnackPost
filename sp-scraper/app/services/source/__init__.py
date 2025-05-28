from fastapi import Depends

import logging

from core.db.repository import DatabaseRepository
from core.fastapi.dependencies import get_repository

from app.models.source import Source
from app.models.source.schema import SourceSchema

from utils.content_tracker import ContentTracker

from app.services import BaseCRUDService


logger = logging.getLogger(__name__)


class SourceService(BaseCRUDService[Source, SourceSchema]):
    def __init__(self, repo: DatabaseRepository[Source]):
        super().__init__(repo, SourceSchema)
    
    async def create_with_user(self, user_id: int, source_data: dict) -> SourceSchema:
        source_data['user_id'] = user_id

        res = await self.create(source_data)

        tracker = ContentTracker()

        await tracker.track_source(source_data['url'], user_id)

        return res

    async def get_user_sources(self, user_id: int) -> list[SourceSchema]:
        return await self.get_all(user_id=user_id)


def get_source_service():
    def func(repo: DatabaseRepository[Source] = Depends(get_repository(Source))):
        return SourceService(repo)
    
    return func
