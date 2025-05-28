import logging

import json
from typing import Dict

from openai import OpenAI

from core.config import OPENROUTER_BASE_URL, OPENROUTER_API_KEY


logger = logging.getLogger(__name__)
client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY)

system_prompt = """
You are a data processing assistant specialized in content link extraction. 

Input: A dictionary of {"url": "title"} pairs.

Processing rules:
1. Filter to keep ONLY links to articles, blog posts, podcasts, or similar content pieces
2. Exclude: 
    - Main pages (/home, /blog, /courses)
    - Service pages (/pricing, /terms, /contact)
    - Non-content pages (login, careers, legal)
3. For valid content links:
    - Keep only URLs present in the original input
    - Translate non-Russian titles to Russian
    - Preserve the original URL casing

Output format: 
Return ONLY a valid Python dictionary in this format:
{"https://domain.com/path": "Translated Title", ...}

Critical requirements:
- NEVER invent URLs not in the original input
- NEVER include Markdown/JSON formatting
- NEVER add explanations or notes
- ALWAYS return parsable Python dict syntax
"""

def process_links(data: Dict[str, str]):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": str(data)},
    ]

    completion = client.chat.completions.create(
        model="deepseek/deepseek-chat:free",
        messages=messages,
        temperature=0.3,
    )

    logger.info(f"\n\n{completion.choices[0].message.__repr__()}\n\n")

    n = 3

    while (not completion.choices[0].message.content) and n:
        n -= 1
        completion = client.chat.completions.create(
            model="deepseek/deepseek-chat:free",
            messages=messages,
            temperature=0.3,
        )

    return extract_and_filter_articles(completion.choices[0].message.content.strip(), data)


def extract_and_filter_articles(llm_response: str, original_links: Dict[str, str]) -> Dict[str, str]:
    """
    Извлекает словарь из ответа LLM и фильтрует несуществующие ссылки.
    
    Args:
        llm_response (str): Ответ LLM в виде строки (ожидается JSON-подобный dict).
        original_links (Dict[str, str]): Исходный словарь ссылок для проверки.
    
    Returns:
        Dict[str, str]: Отфильтрованный словарь с существующими ссылками.
    """
    try:
        # Пытаемся извлечь JSON из ответа LLM
        extracted_dict = json.loads(llm_response.strip("`").replace("'", '"'))
    except json.JSONDecodeError:
        # Если ответ не JSON, ищем в тексте структуру dict
        try:
            extracted_dict = eval(llm_response.split("{", 1)[-1].rsplit("}", 1)[0].strip("`"))
        except:
            return {}

    # Фильтруем ссылки, оставляя только те, что есть в исходных данных
    filtered_articles = {
        url: title
        for url, title in extracted_dict.items()
    }

    return filtered_articles