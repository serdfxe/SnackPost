import os
from dotenv import load_dotenv


load_dotenv(override=True)


ADMIN_ID: int = int(os.getenv("ADMIN_ID"))
API_TOKEN: str = os.getenv("API_TOKEN")
WEBHOOK_URL: str = os.getenv("WEBHOOK_URL")
PROXY_URL: str = os.getenv("PROXY_URL", "http://nginx-proxy.snackpost.svc.cluster.local:80")
