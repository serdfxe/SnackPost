from sqlalchemy import (
    Column,
    String,
    Enum,
    Index,
    BigInteger,
)

from core.db import Base
from core.db.mixins import TimestampMixin

import enum


class SourceType(str, enum.Enum):
    RSS = "rss"
    WEBSITE = "website"


class Source(Base, TimestampMixin):
    __tablename__ = "sources"

    user_id = Column(BigInteger, nullable=False)

    url = Column(String(2048), nullable=False)
    type = Column(Enum(SourceType), nullable=False)

    __table_args__ = (Index("ix_user_source_url", "user_id", "url", unique=True),)
