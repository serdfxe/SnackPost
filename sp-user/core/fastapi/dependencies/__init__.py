from collections.abc import Callable

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import Base, session
from core.db.repository import DatabaseRepository


def get_repository(
    model: type[Base],
) -> Callable[[AsyncSession], DatabaseRepository]:
    def func(session: AsyncSession = Depends(session.get_db_session)):
        return DatabaseRepository(model, session)

    return func
