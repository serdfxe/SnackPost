from pydantic import BaseModel
from typing import List, Optional, Dict


class GenerationRequest(BaseModel):
    messages: List[Dict[str, str]]
    variables: Optional[Dict[str, str]] = None


class GenerationResponse(BaseModel):
    content: str
    usage: Dict[str, int]


class EditRequest(BaseModel):
    current_context: List[Dict[str, str]]
    user_message: str


class PromptTemplate(BaseModel):
    name: str
    system_prompt: str
    description: str
    temperature: float = 0.3
    model: str
    max_tokens: int = 5000
    is_active: bool = True
