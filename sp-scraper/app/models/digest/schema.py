from datetime import date

from uuid import UUID

from pydantic import BaseModel


class DigestBase(BaseModel):
    articles: list[str]
    date: date

    class Config:
        from_attributes = True


class DigestSchema(DigestBase):
    id: UUID
