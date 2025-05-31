from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from enum import Enum


class SourceType(str, Enum):
    RSS = "rss"
    WEBSITE = "website"


class SourceBaseDTO(BaseModel):
    url: str
    type: SourceType = Field(..., description="Тип источника")

    @field_validator("url")
    def normalize_url(cls, v):
        return str(v).lower().strip()


class SourceCreateDTO(SourceBaseDTO):
    pass


class SourceUpdateDTO(BaseModel):
    url: Optional[str] = Field(None, description="URL источника контента")
    type: Optional[SourceType] = Field(None, description="Тип источника")


class SourceResponseDTO(SourceBaseDTO):
    id: UUID = Field(..., description="UUID источника")


class ArticleResponseDTO(BaseModel):
    id: UUID = Field(..., description="ID статьи")
    source_id: UUID = Field(..., description="UUID источника")
    original_url: str = Field(..., description="Оригинальный URL")
    title: Optional[str] = Field(None, description="Заголовок статьи")
    published_at: datetime = Field(..., description="Дата публикации")
    is_processed: bool = Field(..., description="Флаг обработки")
    is_sent: bool = Field(..., description="Флаг отправки")


class SourceListResponseDTO(BaseModel):
    data: list[SourceResponseDTO] = Field(..., description="Список источников")
    count: int = Field(..., description="Общее количество источников")
    skip: int = Field(0, description="Количество пропущенных элементов")
    limit: int = Field(100, description="Лимит на количество элементов")
