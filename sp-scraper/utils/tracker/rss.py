"""
rss_tracker.py - RSS Feed Tracker with Redis backend

Provides RSSFeedTracker class for:
- Initial parsing of RSS feeds
- Comparing feed versions
- Detecting new entries
"""

import feedparser
import redis
import json
from datetime import datetime
from urllib.parse import urlparse
import hashlib

from core.config import REDIS_URL


class RSSFeedTracker:
    def __init__(self, url):
        """Initialize the RSS tracker with Redis connection"""
        self.redis = redis.Redis.from_url(url=REDIS_URL, decode_responses=True)
    
    def _get_feed_entries(self, feed_url):
        """Internal method to parse RSS feed and return entries"""
        try:
            feed = feedparser.parse(feed_url)
            # if feed.bozo:  # Check for parsing errors
            #     raise ValueError(f"Feed parsing error: {feed.bozo_exception}")
            return feed.entries
        except Exception as e:
            print(f"Error parsing feed {feed_url}: {e}")
            return []

    def _generate_entry_id(self, entry):
        """Generate unique ID for feed entry using combination of fields"""
        unique_str = ""
        for field in ['id', 'link', 'title', 'published']:
            if field in entry:
                unique_str += str(entry[field])
        return hashlib.md5(unique_str.encode()).hexdigest()

    def track_new_feed(self, feed_url):
        """
        Perform initial tracking of a new RSS feed
        
        Args:
            feed_url: URL of RSS feed
            
        Returns:
            list: All entries found in the feed
        """
        entries = self._get_feed_entries(feed_url)
        if entries:
            self._save_feed_state(feed_url, entries)
        return entries

    def check_feed_updates(self, feed_url):
        """
        Check for updates in RSS feed compared to last saved state
        
        Args:
            feed_url: URL of RSS feed
            
        Returns:
            dict: {
                'added': list of new entries,
                'removed': list of removed entries,
                'updated': list of updated entries,
                'total': current total entries
            }
        """
        current_entries = self._get_feed_entries(feed_url)
        if not current_entries:
            return {'added': [], 'removed': [], 'updated': [], 'total': 0}
            
        return self._save_feed_state(feed_url, current_entries)

    def get_new_entries(self, feed_url):
        """
        Get only new entries since last check
        
        Args:
            feed_url: URL of RSS feed
            
        Returns:
            list: New entries found
        """
        result = self.check_feed_updates(feed_url)
        return result['added']

    def _save_feed_state(self, feed_url, entries):
        """Internal method to save and compare feed states in Redis"""
        # Redis key structure: "rss:<normalized_feed_url>"
        parsed_url = urlparse(feed_url)
        normalized_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        key = f"test:rss:{normalized_url}"
        
        # Create current state (dict of entry_id: entry_data)
        current_state = {}
        for entry in entries:
            entry_id = self._generate_entry_id(entry)
            current_state[entry_id] = {
                'title': entry.get('title', 'No title'),
                'link': entry.get('link', ''),
                'published': entry.get('published', ''),
                'summary': entry.get('summary', ''),
                'updated': entry.get('updated', '')
            }
        
        # Get previous state
        old_state_json = self.redis.get(key)
        old_state = json.loads(old_state_json)["entries"] if old_state_json else {}
        
        # Find differences
        current_ids = set(current_state.keys())
        old_ids = set(old_state.keys())
        
        added_ids = current_ids - old_ids
        removed_ids = old_ids - current_ids
        common_ids = current_ids & old_ids
        
        # Check for updated entries
        updated_ids = set()
        for entry_id in common_ids:
            if current_state[entry_id] != old_state[entry_id]:
                updated_ids.add(entry_id)
        
        # Prepare results
        added_entries = [current_state[entry_id] for entry_id in added_ids]
        updated_entries = [current_state[entry_id] for entry_id in updated_ids]
        
        # Save new state with timestamp
        feed_data = {
            'entries': current_state,
            'last_checked': datetime.now().isoformat(),
            'etag': getattr(feedparser.parse(feed_url), 'etag', ''),
            'modified': getattr(feedparser.parse(feed_url), 'modified', '')
        }
        
        self.redis.set(key, json.dumps(feed_data))
        
        return {
            'added': added_entries,
            'removed': [old_state[entry_id] for entry_id in removed_ids],
            'updated': updated_entries,
            'total': len(entries)
        }

    def close(self):
        """Clean up resources"""
        self.redis.close()


if __name__ == "__main__":
    tracker = RSSFeedTracker()
    try:
        feed_url = input("Enter RSS feed URL to track: ").strip()
        if not feed_url.startswith(('http://', 'https://')):
            print("Error: Invalid URL format")
            exit(1)
            
        print(f"\nTracking: {feed_url}")
        new_entries = tracker.get_new_entries(feed_url)
        
        if new_entries:
            print(f"\nFound {len(new_entries)} new entries:")
            for entry in new_entries[:5]:  # Show first 5
                print(f"\nTitle: {entry.get('title')}")
                print(f"Link: {entry.get('link')}")
                print(f"Published: {entry.get('published')}")
        else:
            print("\nNo new entries found")
    finally:
        tracker.close()
