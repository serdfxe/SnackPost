from typing import Generic, TypeVar, Optional, Dict, Any, List, Union, Type

import logging

from uuid import UUID

from pydantic import BaseModel

from core.db.repository import DatabaseRepository
from core.db.uow import get_uow


logger = logging.getLogger(__name__)


T = TypeVar('T')
S = TypeVar('S', bound=BaseModel)


class BaseCRUDService(Generic[T, S]):
    def __init__(self, repo: DatabaseRepository[T], schema: Type[S]):
        self.repo = repo
        self.uow = get_uow(repo.session)
        self.schema = schema

    async def create(self, data: Union[Dict[str, Any], S], **kwargs) -> S:
        """Create a new record"""
        if isinstance(data, BaseModel):
            data = data.model_dump()
        
        created = await self.repo.create(**data, **kwargs)
        
        return self._to_schema(created)

    async def get(self, id: UUID, **kwargs) -> Optional[S]:
        """Get single record by ID"""
        record = await self.repo.get(self.repo.model.id == id, **kwargs)
        if record:
            return self._to_schema(record)
        return None

    async def get_all(self, **kwargs) -> List[S]:
        """Get all records"""
        records = await self.repo.filter(**kwargs)
        return [self._to_schema(record) for record in records]

    async def update(self, id: UUID, data: Union[Dict[str, Any], S], **kwargs) -> S:
        """Update existing record"""
        if isinstance(data, BaseModel):
            data = data.model_dump(exclude_unset=True)
        
        updated = await self.repo.update(id, data, **kwargs)
        
        return self._to_schema(updated)

    async def delete(self, id: UUID, **kwargs) -> Dict[str, str]:
        """Delete record by ID"""
        await self.repo.delete(self.repo.model.id == id, **kwargs)

        return {"message": "Record deleted successfully"}

    def _to_schema(self, record: T) -> S:
        """Convert database model to schema"""
        return self.schema(**record.as_dict())