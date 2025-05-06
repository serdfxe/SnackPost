import uuid
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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

    async def filter(self, *args) -> list[Model]:
        query = select(self.model)
        if args:
            query = query.where(*args)
        return list(await self.session.scalars(query))

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
