from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class SubscriptionBase(BaseModel):
    user_id: int
    is_active: bool
    expires_at: datetime | None

    class Config:
        from_attributes = True


class SubscriptionResponseDTO(SubscriptionBase):
    id: UUID


class SubscriptionCreateDTO(SubscriptionBase):
    ...


class SubscriptionUpdateDTO(BaseModel):
    is_active: bool | None = None
    expires_at: datetime | None = None
