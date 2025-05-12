from fastapi import APIRouter, HTTPException
from openai import OpenAI
import logging

from core.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL

from .prompts import summary

from .dto import (
    GenerationRequest,
    GenerationResponse,
    Usage,
    PromptTemplate,
)


content_router = APIRouter(prefix="/content", tags=["content"])
logger = logging.getLogger(__name__)


PROMPT_TEMPLATES = {
    "chat": PromptTemplate(
        name="chat", system_prompt="", description="Чат", model=OPENROUTER_MODEL
    ),
    "article_summary": PromptTemplate(
        name="article_summary",
        system_prompt=summary.SYSTEM_PROMPT,
        description="Генерация выжимок из статей",
        model=OPENROUTER_MODEL,
    ),
}


client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY)


@content_router.post("/generate/{system_content_router}")
async def generate_content(
    system_content_router: str, request: GenerationRequest
) -> GenerationResponse:
    try:
        template = PROMPT_TEMPLATES.get(system_content_router)
        if not template or not template.is_active:
            raise HTTPException(status_code=404, detail="Prompt template not found")

        system_prompt = template.system_prompt
        if request.variables:
            for var in request.variables.items():
                key, value = var.key, var.value
                system_prompt = system_prompt.replace(f"{{{key}}}", value)

        messages = [{"role": "system", "content": system_prompt}] + [i.model_dump() for i in request.messages]

        completion = client.chat.completions.create(
            model=template.model,
            messages=messages,
            temperature=template.temperature,
            max_tokens=template.max_tokens,
        )

        logger.info(f"REASONING: \n\n{completion.choices[0].message.reasoning}\n\n")
        logger.info(f"CONTENT: \n\n{completion.choices[0].message.content}\n\n")

        return GenerationResponse(
            content=completion.choices[0].message.reasoning,
            usage=Usage(
                prompt_tokens=completion.usage.prompt_tokens,
                completion_tokens=completion.usage.completion_tokens,
            ),
        )

    except Exception as e:
        logger.error(f"Generation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Content generation failed")
