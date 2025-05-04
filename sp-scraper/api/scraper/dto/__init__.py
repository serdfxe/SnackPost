from pydantic import BaseModel, Field
from typing import Optional, Dict


class ScrapeRequest(BaseModel):
    url: str = Field(..., description="URL статьи для парсинга")


class ScrapeResponse(BaseModel):
    success: bool = Field(..., description="Статус операции")
    content: Optional[str] = Field(None, description="Текст статьи")
    metadata: Optional[Dict] = Field(
        None, description="Метаданные (title, source, date)"
    )
    error: Optional[str] = Field(None, description="Сообщение об ошибке")
