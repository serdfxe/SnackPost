import json
from redis import asyncio as aioredis

from core.config import REDIS_URL

from .get_articles import get_articles


class ContentTracker:
    def __init__(self, redis_url: str = REDIS_URL):
        self.redis = aioredis.from_url(url=redis_url, decode_responses=True)

    async def track_source(self, source_url: str, user_id: int) -> None:
        """
        Track a new source by saving the initial snapshot of articles.
        
        Args:
            source_url: URL of the source to track
            user_id: ID of the user who wants to track the source
        """
        current_articles = await get_articles(source_url)
        redis_key = f"content_tracker:{user_id}:{source_url}"
        await self.redis.set(redis_key, json.dumps(current_articles))
    
    async def get_new_content(self, source_url: str, user_id: int) -> list[dict[str, str]]:
        """
        Get only new articles since the last check for this user and source.
        
        Args:
            source_url: URL of the source to check
            user_id: ID of the user who is checking
            
        Returns:
            List of new articles since last check (each article is a dict with title and link)
        """
        current_articles = None
        while not current_articles:
            try:
                current_articles = await get_articles(source_url)
            except Exception:
                ...
        
        redis_key = f"content_tracker:{user_id}:{source_url}"
        last_snapshot_json = await self.redis.get(redis_key)

        if not last_snapshot_json:
            new_articles = current_articles
        else:
            last_snapshot = json.loads(last_snapshot_json)
            current_links = {article['link'] for article in current_articles}
            last_links = {article['link'] for article in last_snapshot}
            new_links = current_links - last_links
            new_articles = [article for article in current_articles if article['link'] in new_links]
        
        if current_articles:
            await self.redis.set(redis_key, json.dumps(current_articles))
        
        return new_articles

    async def close(self) -> None:
        """Close the Redis connection"""
        await self.redis.close()