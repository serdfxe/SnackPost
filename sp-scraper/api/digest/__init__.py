from datetime import date
import logging

from typing import Annotated

from fastapi import APIRouter, Header, Depends

from core.fastapi.dependencies import DatabaseRepository, get_repository

from app.models.digest import Article

from app.models.digest.schema import DigestSchema
from app.services.digest import DigestService, get_digest_service


digest_router = APIRouter(
    prefix="/digest",
    tags=["digest"],
)
logger = logging.getLogger(__name__)


@digest_router.get("/")
async def get_digest_route(
    service: Annotated[DigestService, Depends(get_digest_service())],
    x_user_id: Annotated[int, Header()],
) -> DigestSchema:
    return await service.get(x_user_id, date.today())


ArticleRepository = Annotated[
    DatabaseRepository[Article],
    Depends(get_repository(Article)),
]


@digest_router.get("/article")
async def get_digest_article_route(
    article_id: int,
    article_repo: ArticleRepository,
) -> dict[str, str]:
    return {"url": (await article_repo.get(Article.article_id == article_id)).url}
