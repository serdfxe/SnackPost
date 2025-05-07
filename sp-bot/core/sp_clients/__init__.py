from core.config import PROXY_URL

from sp_scraper.scraper_service_client import Client as ScraperClient
from sp_user.user_service_client import Client as UserClient
from sp_content_processing.content_processing_service_client import Client as ContentClient

scraper_client = ScraperClient(base_url=PROXY_URL + "/scraper")
user_client = UserClient(base_url=PROXY_URL + "/user")
content_client = ContentClient(base_url=PROXY_URL + "/content-processing")
