from fastapi import APIRouter

import logging

from zenrows import ZenRowsClient

from core.config import ZENROWS_TOKEN


scraper_router = APIRouter(
    prefix="/scraper",
    tags=["scraper"],
)
logger = logging.getLogger(__name__)


@scraper_router.post("/scrape")
async def scrape_article_route(url: str) -> str:
    """
    Parse article by URL.
    """
    try:
        logger.info(f"Starting scraping for URL: {url}")
        
        client = ZenRowsClient(ZENROWS_TOKEN)
        params = {
            "js_render": "true", 
            "wait": "10000", 
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
        return response.text

    except Exception as e:
        logger.error(f"Error scraping URL {url}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Scraping failed: {str(e)}",
        )
