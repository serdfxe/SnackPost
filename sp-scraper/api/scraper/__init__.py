from fastapi import APIRouter, HTTPException
from .dto import ScrapeRequest, ScrapeResponse

scraper_router = APIRouter(
    prefix="/scraper",
    tags=["scraper"],
)


@scraper_router.post("/scrape", response_model=ScrapeResponse)
async def scrape_article_route(request: ScrapeRequest):
    """
    Parse article by URL
    """
