from pydantic import BaseModel


class ScraperResponse(BaseModel):
    content: str
