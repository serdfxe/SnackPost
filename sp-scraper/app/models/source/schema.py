from enum import Enum

from pydantic import BaseModel

from uuid import UUID


class SourceType(str, Enum):
    RSS = "rss"
    WEBSITE = "website"


class SourceBase(BaseModel):
    url: str
    type: SourceType

    class Config:
        from_attributes = True


class SourceSchema(SourceBase):
    id: UUID
