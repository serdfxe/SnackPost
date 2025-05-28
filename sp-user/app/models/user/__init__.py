from sqlalchemy import BigInteger, Column, String

from sqlalchemy.orm import relationship

from core.db import Base
from core.db.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    username = Column(String, nullable=False, unique=True)
