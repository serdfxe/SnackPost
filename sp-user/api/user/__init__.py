from typing import Annotated
from fastapi import APIRouter

user_router = APIRouter(
    prefix="/scraper",
    tags=["scraper"],
)


@scraper_router.post("/check-subscription")
async def scrape_article_route(x_user_id: Annotated[int, Header()],) -> bool:
    """
    Check subscription by user id
    """

    return True
