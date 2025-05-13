from sqlalchemy import (
    BigInteger, 
    Column, 
    String, 
    Boolean, 
    DateTime, 
    ForeignKey,
    Text,
    Enum,
    UUID,
    Index
)
from sqlalchemy.orm import relationship

from core.db import Base
from core.db.mixins import TimestampMixin

import enum


class SourceType(str, enum.Enum):
    RSS = "rss"
    WEBSITE = "website"


class Source(Base, TimestampMixin):
    __tablename__ = "sources"
    
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    
    url = Column(String(2048), nullable=False)
    type = Column(Enum(SourceType), nullable=False)
    
    user = relationship("User", back_populates="sources")
    articles = relationship("Article", back_populates="source", cascade="all, delete")
    
    __table_args__ = (
        Index("ix_user_source_url", "user_id", "url", unique=True),
    )


class Article(Base, TimestampMixin):
    __tablename__ = "articles"

    source_id = Column(UUID, ForeignKey("sources.id", ondelete="CASCADE"))
    
    original_url = Column(String(2048), nullable=False)
    external_id = Column(String(512), nullable=True)
    
    title = Column(String(1024), nullable=True)
    raw_content = Column(Text, nullable=True)
    published_at = Column(DateTime, nullable=False)
    
    is_processed = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    
    source = relationship("Source", back_populates="articles")
    
    __table_args__ = (
        Index("ix_source_external_id", "source_id", "external_id", unique=True),
    )
