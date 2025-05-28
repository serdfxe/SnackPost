import os
from dotenv import load_dotenv


load_dotenv(override=True)


DEBUG: bool = os.environ.get("DEBUG", "False") == "True"
API_HOST: str = os.environ.get("APP_HOST", "0.0.0.0")
API_PORT: int = int(os.environ.get("APP_PORT", "8000"))
ZENROWS_TOKEN: str = os.environ.get("ZENROWS_TOKEN")
REDIS_URL: str = os.environ.get("REDIS_URL") 
DB_URL: str = os.environ.get("DB_URL")
GH_TOKEN: str = os.environ.get("GH_TOKEN")
OPENROUTER_API_KEY: str = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL: str = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL: str = os.environ.get("OPENROUTER_MODEL", "deepseek/deepseek-chat:free")
