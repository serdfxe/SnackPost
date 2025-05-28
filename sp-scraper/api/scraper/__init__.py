from fastapi import APIRouter, HTTPException

from fastapi_cache.decorator import cache

import logging

from utils.page_content_extractor import PageContentExtractor

from .dto import ScraperResponse


scraper_router = APIRouter(
    prefix="/scraper",
    tags=["scraper"],
)
logger = logging.getLogger(__name__)


@scraper_router.get("/scrape")
@cache(expire=89280*7)
async def scrape_article_route(url: str) -> ScraperResponse:
    """
    Parse article by URL.
    """
    try:
        logger.info(f"Starting scraping for URL: {url}")
        
        scraper = PageContentExtractor()
        result = scraper.get_page_content(url)

        if not result:
            logger.warning(f"Empty response received for URL: {url}")
            raise HTTPException(
                status_code=400,
                detail="Empty content received from scraping service",
            )

        logger.info(f"Successfully scraped URL: {url}")
        logger.info(f"\n\nRESPONSE:\n\n{result}\n\n")
        return ScraperResponse(content=result)

    except Exception as e:
        logger.error(f"Error scraping URL {url}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Scraping failed: {str(e)}",
        )
