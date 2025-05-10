from core.config import SCRAPER_URL, USER_URL, CONTENT_URL

from .sp_scraper.scraper_service_client import Client as ScraperClient
from .sp_user.user_service_client import Client as UserClient
from .sp_content_processing.content_processing_service_client import Client as ContentClient

scraper_client = ScraperClient(base_url=SCRAPER_URL)
user_client = UserClient(base_url=USER_URL)
content_client = ContentClient(base_url=CONTENT_URL)
