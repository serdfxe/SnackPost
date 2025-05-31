from sqlalchemy import (
    Column,
    Date,
    UniqueConstraint,
    JSON,
    BigInteger,
    Text,
)

from sqlalchemy.schema import Identity

from core.db import Base
from core.db.mixins import TimestampMixin


class Digest(Base, TimestampMixin):
    __tablename__ = "digests"

    user_id = Column(BigInteger, nullable=False)
    date = Column(Date, nullable=False)

    articles = Column(JSON)

    __table_args__ = (UniqueConstraint("user_id", "date", name="_user_date_uc"),)


class Article(Base):
    __tablename__ = "articles"

    article_id = Column(BigInteger, Identity(start=1, increment=1), primary_key=True)
    url = Column(Text, nullable=False)
