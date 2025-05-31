from uuid import UUID
from pydantic import BaseModel


class UserBase(BaseModel):
    user_id: int
    first_name: str
    last_name: str | None
    username: str

    class Config:
        from_attributes = True


class UserResponseDTO(UserBase):
    id: UUID


class UserCreateDTO(UserBase): ...
