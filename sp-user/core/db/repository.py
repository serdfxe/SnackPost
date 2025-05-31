import uuid
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy.sql.expression import BinaryExpression

from core.db import Base


Model = TypeVar("Model", bound=Base)


class DatabaseRepository(Generic[Model]):
    """Repository for performing database queries."""

    def __init__(self, model: type[Model], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def create(self, **kwargs) -> Model:
        instance = self.model(**kwargs)

        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)

        return instance

    async def get(self, *args) -> Model | None:
        query = select(self.model)
        if args:
            query = query.where(*args)
        return await self.session.scalar(query)

    async def filter(
        self, *where: BinaryExpression, skip: int = 0, limit: int = 100, **filters
    ) -> list[Model]:
        """Filter models with pagination support."""
        query = select(self.model)

        if where:
            query = query.where(*where)
        if filters:
            query = query.filter_by(**filters)

        query = query.offset(skip).limit(limit)
        result: Result = await self.session.execute(query)
        return list(result.scalars())

    async def count(self, *where: BinaryExpression) -> int:
        """Count models matching conditions."""
        query = select(self.model).where(*where) if where else select(self.model)
        result: Result = await self.session.execute(query)
        return len(list(result.scalars()))

    async def delete(self, *args):
        obj = await self.get(*args)

        if obj is not None:
            await self.session.delete(obj)
            await self.session.commit()

    async def update(self, id: uuid.UUID, data: dict):
        obj = await self.get(self.model.id == id)
        if obj is not None:
            for key, value in data.items():
                setattr(obj, key, value)
            await self.session.commit()

        await self.session.refresh(obj)
        self.session.expunge(obj)

        return obj

    async def add(self, obj):
        self.session.add(obj)
        await self.session.commit()
