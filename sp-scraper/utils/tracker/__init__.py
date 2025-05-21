"""
combined_tracker.py - Unified tracking system with Strategy pattern
"""

from pydantic import BaseModel, Field

import logging

from core.config import REDIS_URL

from app.models.source.schema import (
    SourceType,
    SourceSchema,
)

from .rss import RSSFeedTracker
from .website import WebsiteTracker


class ContentUpdate(BaseModel):
    source: SourceSchema
    added: list = Field(default_factory=list)
    removed: list = Field(default_factory=list)
    updated: list = Field(default_factory=list)
    total: int = 0


logger = logging.getLogger(__name__)


class ContentTracker:
    website_tracker = WebsiteTracker(REDIS_URL)
    rssfeed_tracker = RSSFeedTracker(REDIS_URL)

    def __init__(self):
        self._strategies = {
            SourceType.RSS: self.rssfeed_tracker,
            SourceType.WEBSITE: self.website_tracker,
        }

    def _get_strategy(self, source_type: SourceType):
        """Get appropriate strategy based on source type"""
        strategy = self._strategies.get(source_type)
        if not strategy:
            raise ValueError(f"No strategy available for {source_type}")
        return strategy

    def track_source(self, source: SourceSchema) -> ContentUpdate:
        """
        Track a new source (initial setup)
        
        Args:
            source: SourceSchema object with url and type
            
        Returns:
            ContentUpdate with initial content state
        """
        strategy = self._get_strategy(source.type)
        
        if source.type == SourceType.RSS:
            entries = strategy.track_new_feed(source.url)
            return ContentUpdate(
                source=source,
                added=entries,
                total=len(entries)
            )
        else:  # website
            links = strategy.scrape_new_url(source.url)
            return ContentUpdate(
                source=source,
                added=links,
                total=len(links)
            )

    def check_updates(self, source: SourceSchema) -> ContentUpdate:
        """
        Check for updates in the source
        
        Args:
            source: SourceSchema object to check
            
        Returns:
            ContentUpdate with detected changes
        """
        strategy = self._get_strategy(source.type)
        
        if source.type == SourceType.RSS:
            result = strategy.check_feed_updates(source.url)
            return ContentUpdate(
                source=source,
                added=result['added'],
                removed=result['removed'],
                updated=result['updated'],
                total=result['total']
            )
        else:  # website
            result = strategy.compare_snapshots(source.url)
            return ContentUpdate(
                source=source,
                added=result['added'],
                removed=result['removed'],
                total=result['total']
            )

    def get_new_content(self, source: SourceSchema) -> list:
        """
        Get only new content since last check
        
        Args:
            source: SourceSchema object to check
            
        Returns:
            list of new items (entries or links)
        """
        strategy = self._get_strategy(source.type)
        
        logger.info(f"\n\n{strategy}\n\n")
        logger.info(f"\n\n{source}\n\n")
        
        return strategy.get_new_entries(source.url) if source.type == SourceType.RSS else strategy.get_new_links(source.url)

    def close(self):
        """Clean up all resources"""
        for strategy in self._strategies.values():
            strategy.close()


# Example usage
if __name__ == "__main__":
    from pydantic import ValidationError
    
    tracker = ContentTracker()
    try:
        # Example RSS source
        rss_source = SourceSchema(
            url="https://example.com/feed.rss",
            type=SourceType.RSS,
        )
        
        # Example website source
        web_source = SourceSchema(
            url="https://example.com",
            type=SourceType.WEBSITE,
        )
        
        # Track new sources
        print("Tracking RSS feed...")
        rss_update = tracker.track_source(rss_source)
        print(f"Found {rss_update.total} initial entries")
        
        print("\nTracking website...")
        web_update = tracker.track_source(web_source)
        print(f"Found {web_update.total} initial links")
        
        # Check updates
        print("\nChecking RSS feed updates...")
        rss_updates = tracker.check_updates(rss_source)
        print(f"New entries: {len(rss_updates.added)}")
        
        print("\nChecking website updates...")
        web_updates = tracker.check_updates(web_source)
        print(f"New links: {len(web_updates.added)}")
        
    except ValidationError as e:
        print(f"Invalid source configuration: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        tracker.close()