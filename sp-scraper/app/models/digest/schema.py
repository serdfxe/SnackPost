from datetime import date

from uuid import UUID

from pydantic import BaseModel


class DigestBase(BaseModel):
    articles: list[dict[str, str]]
    date: date

    class Config:
        from_attributes = True


class DigestSchema(DigestBase):
    id: UUID

class ArticleSchema(BaseModel):
    id: UUID
    article_id: int
    url: str

    class Config:
        from_attributes = True