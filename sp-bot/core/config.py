import os
from dotenv import load_dotenv


load_dotenv(override=True)


MASTER_ID: int = int(os.getenv("MASTER_ID"))
ADMINS: set[int] = set([int(i) for i in os.getenv("ADMINS", str(MASTER_ID)).strip().replace(" ", "").split(",")])
API_TOKEN: str = os.getenv("API_TOKEN")
WEBHOOK_URL: str = os.getenv("WEBHOOK_URL")
PROXY_URL: str = os.getenv("PROXY_URL", "http://nginx-proxy.snackpost.svc.cluster.local:80")
SCRAPER_URL: str = os.getenv("SCRAPER_URL", PROXY_URL + "/scraper")
USER_URL: str = os.getenv("USER_URL", PROXY_URL + "/user")
CONTENT_URL: str = os.getenv("CONTENT_URL", PROXY_URL + "/content")
