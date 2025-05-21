from pydantic import BaseModel, HttpUrl


class ArticleBase(BaseModel):
    url: HttpUrl
    title: str


class DigestBase(BaseModel):
    articles: list[ArticleBase]


class DigestResponse(DigestBase):
    ...
