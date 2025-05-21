"""
Web Scraper Module for tracking URL changes with Redis backend

Provides WebsiteTracker class for:
- Initial scraping of new URLs
- Comparing snapshots
- Detecting new links
"""
import logging

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import json
from datetime import datetime
import redis

from core.config import GH_TOKEN


logger = logging.getLogger(__name__)


import os

os.environ['GH_TOKEN'] = GH_TOKEN


class WebsiteTracker:
    def __init__(self, url):
        """Initialize the link tracker with Redis connection"""
        self.redis = redis.Redis.from_url(url=url, decode_responses=True)
        self.options = Options()
        self.options.add_argument('--headless')
        
        from webdriver_manager.firefox import GeckoDriverManager
        self.driver = webdriver.Firefox(
            service=Service(GeckoDriverManager().install()),
            options=self.options
        )

    def _get_links(self, url):
        """Internal method to scrape links from a URL"""
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            time.sleep(5)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            return [urljoin(url, link['href']) 
                    for link in soup.find_all('a', href=True)]
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return []

    def scrape_new_url(self, base_url):
        """
        Perform initial scrape of a new base URL
        
        Args:
            base_url: URL to scrape
            
        Returns:
            list: All links found on the page
        """
        links = self._get_links(base_url)
        if links:
            self._save_snapshot(base_url, links)
        return links

    def compare_snapshots(self, base_url):
        """
        Compare current state with saved snapshot
        
        Args:
            base_url: URL to compare
            
        Returns:
            dict: {
                'added': list of new links,
                'removed': list of removed links,
                'total': current total links
            }
        """
        current_links = self._get_links(base_url)
        if not current_links:
            return {'added': [], 'removed': [], 'total': 0}
            
        return self._save_snapshot(base_url, current_links)

    def get_new_links(self, base_url):
        """
        Get only new links since last snapshot
        
        Args:
            base_url: URL to check
            
        Returns:
            list: New links found
        """
        result = self.compare_snapshots(base_url)
        return [{"link": i} for i in result['added']]

    def _save_snapshot(self, base_url, links):
        """Internal method to save and compare snapshots in Redis"""
        # Redis key structure: "snapshot:<base_url>"
        key = f"test:snapshot:{base_url}"
        
        # Get previous snapshot
        old_links_json = self.redis.get(key)
        old_links = set(json.loads(old_links_json)["links"]) if old_links_json else set()
        new_links_set = set(links)

        logger.info(f"\n\n{old_links}\n\n")
        logger.info(f"\n\n{new_links_set}\n\n")
        
        # Find differences
        added = new_links_set - old_links
        removed = old_links - new_links_set
        
        # Save new snapshot with timestamp
        snapshot_data = {
            'links': links,
            'timestamp': datetime.now().isoformat()
        }
        
        self.redis.set(key, json.dumps(snapshot_data))
        
        return {
            'added': sorted(added),
            'removed': sorted(removed),
            'total': len(links)
        }

    def close(self):
        """Clean up resources"""
        self.driver.quit()
        self.redis.close()

# Example usage
if __name__ == "__main__":
    tracker = WebsiteTracker()
    try:
        url = input("Enter URL to track: ").strip()
        if not url.startswith(('http://', 'https://')):
            print("Error: Invalid URL format")
            exit(1)
            
        print(f"\nTracking: {url}")
        new_links = tracker.get_new_links(url)
        if new_links:
            print(f"\nFound {len(new_links)} new links:")
            for link in new_links[:10]:  # Show first 10
                print(f"- {link}")
        else:
            print("\nNo new links found")
    finally:
        tracker.close()