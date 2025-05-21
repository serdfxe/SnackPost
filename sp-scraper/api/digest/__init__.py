from datetime import date
import logging

from typing import Annotated

from fastapi import APIRouter, Header, Depends

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
