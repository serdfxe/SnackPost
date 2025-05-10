from pydantic import BaseModel
from typing import List, Optional, Dict


class Message(BaseModel):
    role: str
    content: str

class Variable(BaseModel):
    name: str
    value: str

class GenerationRequest(BaseModel):
    messages: List[Message]
    variables: Optional[List[Variable]] = None


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int

class GenerationResponse(BaseModel):
    content: str
    usage: Usage


class EditRequest(BaseModel):
    current_context: List[Message]
    user_message: str


class PromptTemplate(BaseModel):
    name: str
    system_prompt: str
    description: str
    temperature: float = 0.3
    model: str
    max_tokens: int = 5000
    is_active: bool = True
