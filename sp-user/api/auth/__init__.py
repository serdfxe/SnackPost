from typing import Annotated
from fastapi import APIRouter, Header

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@auth_router.get("/check-subscription")
async def scrape_article_route(x_user_id: Annotated[int, Header()],) -> bool:
    """
    Check subscription by user id
    """
