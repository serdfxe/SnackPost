from sqlalchemy import BigInteger, Column, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func

from core.db import Base
from core.db.mixins import TimestampMixin


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    user_id = Column(
        BigInteger, ForeignKey("users.user_id"), nullable=False, unique=True
    )
    is_active = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
