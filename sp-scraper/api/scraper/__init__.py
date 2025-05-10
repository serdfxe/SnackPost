from fastapi import APIRouter, HTTPException

from fastapi_cache.decorator import cache

import logging

from zenrows import ZenRowsClient

from core.config import ZENROWS_TOKEN

from .dto import ScraperResponse


scraper_router = APIRouter(
    prefix="/scraper",
    tags=["scraper"],
)
logger = logging.getLogger(__name__)


@scraper_router.get("/scrape")
@cache(expire=89280)
async def scrape_article_route(url: str) -> ScraperResponse:
    """
    Parse article by URL.
    """
    try:
        logger.info(f"Starting scraping for URL: {url}")
        
        client = ZenRowsClient(ZENROWS_TOKEN)
        params = {
            "js_render": "true", 
            "wait": "15000", 
            "response_type": "markdown"
        }

        response = client.get(str(url), params=params)

        if not response.text:
            logger.warning(f"Empty response received for URL: {url}")
            raise HTTPException(
                status_code=400,
                detail="Empty content received from scraping service",
            )

        logger.info(f"Successfully scraped URL: {url}")
        return ScraperResponse(content=response.text)

    except Exception as e:
        logger.error(f"Error scraping URL {url}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Scraping failed: {str(e)}",
        )
