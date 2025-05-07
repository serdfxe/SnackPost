import os
from dotenv import load_dotenv


load_dotenv(override=True)


DEBUG: bool = os.environ.get("DEBUG", "False") == "True"
API_HOST: str = os.environ.get("APP_HOST", "0.0.0.0")
API_PORT: int = int(os.environ.get("APP_PORT", "8000"))
OPENROUTER_API_KEY: str = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL: str = os.environ.get("OPENROUTER_BASE_URL")
OPENROUTER_MODEL: str = os.environ.get("OPENROUTER_MODEL")
