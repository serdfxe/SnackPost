from pydantic import BaseModel


class ScraperResponse(BaseModel):
    content: str


class Article(BaseModel):
    title: str
    link: str
    published: str | None = None
