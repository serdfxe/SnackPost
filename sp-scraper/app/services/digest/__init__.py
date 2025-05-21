from datetime import date

from fastapi import Depends

from itertools import chain

import logging

from app.models.source import Source

from core.db.repository import DatabaseRepository
from core.fastapi.dependencies import get_repository

from utils.tracker import ContentTracker

from app.models.digest import Digest
from app.models.digest.schema import DigestSchema

from app.services.source import SourceService
from app.services import BaseCRUDService


logger = logging.getLogger(__name__)


class DigestService(BaseCRUDService[Digest, DigestSchema]):
    def __init__(self, digest_repo: DatabaseRepository[Digest], source_repo: DatabaseRepository[Source]):
        self.digest_repo = digest_repo
        self.source_repo = source_repo
        
        super().__init__(digest_repo, DigestSchema)
    
    async def create(self, user_id: int, date: date) -> DigestSchema:
        source_service = SourceService(self.source_repo)

        try:
            sources = await source_service.get_all(user_id=user_id)

            tracker = ContentTracker()

            result = list(chain(*[tracker.get_new_content(s) for s in sources]))

            digest = await super().create({
                "user_id": user_id,
                "articles": [i["link"] for i in result],
                "date": date,
            })

            return digest

        except Exception as e:
            logger.error(f"Error while creating digest: {e}")
            raise e
    
    async def get(self, user_id: int, date: date):
        """
        Get digest by date. Or create digest if not exists.
        """

        try:
            digest = await self.digest_repo.filter(Digest.user_id == user_id, Digest.date == date)
            
            if len(digest):
                return self._to_schema(digest[0])

            return await self.create(user_id, date)
        except Exception as e:
            logger.error(f"Error while creating digest: {e}")
            raise e


def get_digest_service():
    def func(digest_repo: DatabaseRepository[Digest] = Depends(get_repository(Digest)), source_repo: DatabaseRepository[Source] = Depends(get_repository(Source))):
        return DigestService(digest_repo, source_repo)

    return func