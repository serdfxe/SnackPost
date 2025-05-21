from sqlalchemy import (
    Column,
    Date,
    UniqueConstraint,
    JSON,
    BigInteger,
)

from core.db import Base
from core.db.mixins import TimestampMixin


class Digest(Base, TimestampMixin):
    __tablename__ = "digests"
    
    user_id = Column(BigInteger, nullable=False)
    date = Column(Date, nullable=False)
    
    articles = Column(JSON)

    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='_user_date_uc'),
    )
