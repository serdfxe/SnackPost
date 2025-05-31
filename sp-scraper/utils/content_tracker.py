import json
from redis import asyncio as aioredis

from core.config import REDIS_URL

from .get_articles import get_articles, get_links
from .extract_and_filter_articles import process_links

import logging

logger = logging.getLogger(__name__)


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
        current_links = await get_links(source_url)

        logger.info(f"\n\n All extracted links:\n\n{current_links}\n\n")

        current_articles = process_links(current_links, set())

        redis_key = f"content_tracker:{user_id}:{source_url}"
        await self.redis.set(
            redis_key,
            json.dumps(
                {
                    "links": list(current_links.keys()),
                    "articles": {k: {"title": d} for k, d in current_articles.items()},
                }
            ),
        )

    async def get_new_content(
        self, source_url: str, user_id: int
    ) -> list[dict[str, str]]:
        """
        Get only new articles since the last check for this user and source.

        Args:
            source_url: URL of the source to check
            user_id: ID of the user who is checking

        Returns:
            List of new articles since last check (each article is a dict with title and link)
        """

        redis_key = f"content_tracker:{user_id}:{source_url}"
        last_snapshot = json.loads(await self.redis.get(redis_key))

        logger.info(f"\n\n LAST SNAPSHOT:\n\n{last_snapshot}\n\n")

        snapshot_links = set(last_snapshot["links"])
        snapshot_articles = last_snapshot["articles"]

        current_links = {}
        while not current_links:
            try:
                current_links = await get_links(source_url)
            except Exception:
                ...

        logger.info(f"\n\n CURRENT LINKS:\n\n{current_links}\n\n")

        new_links = process_links(current_links, set(snapshot_links))

        snapshot_links.update(current_links.keys())
        snapshot_articles.update({k: {"title": d} for k, d in new_links.items()})

        if last_snapshot:
            await self.redis.set(
                redis_key,
                json.dumps(
                    {"links": list(snapshot_links), "articles": snapshot_articles}
                ),
            )

        return [{"link": k, "title": d} for k, d in new_links.items()]

    async def get_content(self, source_url: str, user_id: int) -> list[dict[str, str]]:
        redis_key = f"content_tracker:{user_id}:{source_url}"
        last_snapshot = json.loads(await self.redis.get(redis_key))

        logger.info(f"\n\n LAST SNAPSHOT:\n\n{last_snapshot}\n\n")

        snapshot_articles = last_snapshot["articles"]

        return [{"link": k, "title": d["title"]} for k, d in snapshot_articles.items()]

    async def close(self) -> None:
        """Close the Redis connection"""
        await self.redis.close()
