from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException

from fastapi_cache.decorator import cache

import feedparser

import logging

from zenrows import ZenRowsClient

from core.config import ZENROWS_TOKEN

from utils.rss_finder import find_feed

from .dto import ScraperResponse, UrlResponse, Article


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
    # return ScraperResponse(content=f"Scraped text from {url}")
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
        logger.info(f"\n\nRESPONSE:\n\n{response.text}\n\n")
        return ScraperResponse(content=response.text)

    except Exception as e:
        logger.error(f"Error scraping URL {url}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Scraping failed: {str(e)}",
        )


@scraper_router.get("/rss")
async def get_rss_route(url: str) -> UrlResponse:
    """
    Get rss feed by URL.
    """
    try:
        rss_url = find_feed(url)

        assert rss_url

        return UrlResponse(url=rss_url)
    except Exception:
        raise HTTPException(status_code=404, detail="RSS feed not found")


@scraper_router.get("/scrape/rss-feed")
async def scrape_rss_feed_route(
    url: str,
    days: int,
    limit: int
) -> list[Article]:
    """
    Scrape RSS-feed, returns articles
    """
    try:
        feed = feedparser.parse(url)
        
        if not len(feed.entries):
            raise HTTPException(status_code=400, detail="Неверный формат RSS-ленты")
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        articles = []
        for entry in feed.entries:
            published_time = getattr(entry, 'published_parsed', None) or getattr(entry, 'published', None)
            
            if published_time:
                published_date = datetime(*published_time[:6])
                if published_date >= cutoff_date:
                    articles.append(Article(
                        title=entry.title,
                        link=entry.link,
                        published=published_date.isoformat()
                    ))
            
            if len(articles) >= limit:
                break
        
        return articles
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при парсинге RSS: {str(e)}")
