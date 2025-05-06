from sqlalchemy import orm
import uuid


class Base(orm.DeclarativeBase):
    """Base database model."""

    id: orm.Mapped[uuid.UUID] = orm.mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    def as_dict(self):
        return {
            c.name: (
                getattr(self, c.name)
                if not (
                    isinstance(getattr(self, c.name), float)
                    and isnan(getattr(self, c.name))
                )
                else None
            )
            for c in self.__table__.columns
        }
