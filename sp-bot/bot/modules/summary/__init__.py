import asyncio
from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import logging

from core.sp_clients import scraper_client, content_client
from core.sp_clients.sp_content_processing.content_processing_service_client.models import (
    GenerationRequest,
    Message as SPMessage,
)
from core.sp_clients.sp_scraper.scraper_service_client.api.scraper import (
    scrape_article_route_scraper_scrape_get,
)
from core.sp_clients.sp_scraper.scraper_service_client.api.digest import (
    get_digest_article_route_digest_article_get,
)
from core.sp_clients.sp_content_processing.content_processing_service_client.api.content import (
    generate_content_content_generate_system_content_router_post,
)

from core.messages import SUBSCRIPTION_REQUIRED_MSG

from bot.filters.subscription import IsSubscribed
from bot.utils.admin import notify_admin


logger = logging.getLogger(__name__)
summary_router = Router(name="summary_router")


class SummaryStates(StatesGroup):
    """FSM states for summary generation workflow"""

    waiting_for_url = State()
    waiting_for_edit = State()


user_contexts = {}


@summary_router.message(Command("summarize", "s"), IsSubscribed())
async def handle_summary_command(message: Message, state: FSMContext, bot: Bot):
    """Handle the summarize command with optional URL parameter"""
    try:
        args = message.text.split(maxsplit=1)

        if len(args) > 1 and is_valid_url(args[1]):
            await notify_admin(bot, message, "Started summary with URL", args[1])
            await process_url(message, message.from_user.id, args[1], state, bot)
        else:
            await notify_admin(bot, message, "Started summary without URL")
            await message.answer("📝 Отправьте ссылку на статью:")
            await state.set_state(SummaryStates.waiting_for_url)

    except Exception as e:
        logger.error(f"Error in handle_summary_command: {e}", exc_info=True)
        await message.answer("⚠️ Ошибка при обработке команды")


@summary_router.message(Command("summarize", "s"), ~IsSubscribed())
async def handle_summary_command_not_sub(message: Message, state: FSMContext, bot: Bot):
    """Handle the summarize command when not subscribed"""
    await notify_admin(bot, message, "Tried to use summary without subscription")
    await message.answer(SUBSCRIPTION_REQUIRED_MSG, parse_mode="HTML")


@summary_router.message(SummaryStates.waiting_for_url, F.text & ~F.text.startswith("/"))
async def handle_url_input(message: Message, state: FSMContext, bot: Bot):
    """Process user-provided URL for article scraping"""
    try:
        if not is_valid_url(message.text):
            await message.reply("⚠️ Неверный формат ссылки. Попробуйте еще раз:")
            return

        await notify_admin(bot, message, "Submitted URL for summary", message.text)
        await process_url(message, message.from_user.id, message.text, state, bot)

    except Exception as e:
        logger.error(f"Error in handle_url_input: {e}", exc_info=True)
        await message.answer("⚠️ Ошибка при обработке ссылки")
        await state.clear()


@summary_router.callback_query(F.data.startswith("create_post:"))
async def handle_url_callback_input(
    callback: CallbackQuery, state: FSMContext, bot: Bot
):
    """Process article URL from callback with article_id"""
    logger.info(f"!!!!!!!!!!!!!!!!!!!! {callback.data}")

    await state.set_state(SummaryStates.waiting_for_url)

    try:
        # Extract article_id from callback data
        article_id = int(callback.data.split(":")[1])

        # Get article details from API
        response = await get_digest_article_route_digest_article_get.asyncio(
            client=scraper_client, article_id=article_id
        )

        url = response["url"]

        if not is_valid_url(url):
            await callback.message.reply("⚠️ Неверный формат ссылки в данных статьи")
            return

        await notify_admin(bot, callback.message, "Submitted URL from callback", url)
        await process_url(callback.message, callback.from_user.id, url, state, bot)

    except Exception as e:
        logger.error(f"Error in handle_url_callback_input: {e}", exc_info=True)
        await callback.message.answer("⚠️ Ошибка при обработке ссылки из callback")
        await state.clear()


@summary_router.message(
    SummaryStates.waiting_for_edit,
    F.text & ~F.text.startswith("/") & ~F.text.startswith("http"),
)
async def handle_edit_mode(message: Message, state: FSMContext, bot: Bot):
    """Handle user edits to the generated summary"""
    try:
        user_id = message.from_user.id
        context = user_contexts.get(user_id)

        if not context:
            await message.answer("❌ Сессия устарела. Начните заново с /s")
            await state.clear()
            return

        await notify_admin(
            bot,
            message,
            "Edited summary",
            f"Original URL: {context['url']}\nEdit: {message.text}",
        )

        context["messages"].append({"role": "user", "content": message.text})

        progress_msg = await message.reply("🔄 Обновляю выжимку...")

        new_summary = (
            (await generate_summary(context["messages"]))
            .replace("\\n", "\n")
            .replace('\\"', '"')
        )
        await progress_msg.edit_text(
            "📝 <b>Обновлённая выжимка:</b>", parse_mode="HTML"
        )

        try:
            mess = await progress_msg.reply(
                new_summary,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
        except Exception:
            mess = await progress_msg.reply(new_summary)

        await mess.reply(
            "✏️ Можете продолжить редактирование или нажать /s для новой статьи",
            parse_mode="HTML",
        )

        context["messages"].append({"role": "assistant", "content": new_summary})

    except Exception as e:
        logger.error(f"Error in handle_edit_mode: {e}", exc_info=True)
        await message.answer(f"⚠️ Ошибка при обновлении выжимки")


async def process_url(
    message: Message, user_id: int, url: str, state: FSMContext, bot: Bot
):
    """Process article URL and generate initial summary"""
    try:
        progress_msg = await message.reply(
            f"🔎 Проверяю доступность статьи...\n\n<code>{url}</code>",
            parse_mode="HTML",
        )

        try:
            article_text = await fetch_article_text(url)
        except Exception as e:
            await progress_msg.edit_text(
                "❌ Не удалось получить текст статьи. Проверьте URL или попробуйте другую статью."
            )
            await state.clear()
            return

        await progress_msg.edit_text(
            f"📖 Статья получена ({len(article_text)//1000}к символов)\n",
        )

        await asyncio.sleep(2)

        await progress_msg.edit_text(
            "🔍 Анализирую содержание...",
        )

        messages = [{"role": "user", "content": f"[{url}]\n\n {article_text}"}]

        request = GenerationRequest(messages=[SPMessage.from_dict(m) for m in messages])
        response = (
            await generate_content_content_generate_system_content_router_post.asyncio(
                client=content_client,
                system_content_router="article_summary",
                body=request,
            )
        )

        if not response or not response.content:
            raise ValueError("Не удалось получить выжимку от сервиса")

        user_contexts[user_id] = {
            "url": url,
            "messages": [
                {"role": "user", "content": f"{article_text}"},
                {"role": "assistant", "content": response.content},
            ],
        }

        await progress_msg.edit_text("📝 <b>Готовая выжимка:</b>", parse_mode="HTML")

        content = response.content.replace("\\n", "\n").replace('\\"', '"')

        try:
            mess = await progress_msg.reply(
                content,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
        except Exception as e:
            logger.error(f"Error in process_url: {e}", exc_info=True)
            mess = await progress_msg.reply(content)

        await mess.reply("✏️ Напишите свои правки текстом, и я адаптирую выжимку.")
        await state.set_state(SummaryStates.waiting_for_edit)

        # Notify admin about successful summary generation
        await notify_admin(
            bot,
            message,
            "Generated summary",
            f"URL: {url}\nLength: {len(article_text)} chars\nSummary length: {len(response.content)} chars",
        )

    except Exception as e:
        logger.error(f"Error in process_url: {e}", exc_info=True)
        await message.answer(f"⚠️ Ошибка")
        await state.clear()


async def fetch_article_text(url: str) -> str:
    """Fetch article content using scraping service"""
    try:
        response = await scrape_article_route_scraper_scrape_get.asyncio(
            client=scraper_client, url_query=url
        )
        if isinstance(response, dict):
            if not response or not response["content"]:
                raise ValueError("Не удалось получить текст статьи")

            return response["content"]
        else:
            if not response or not response.content:
                raise ValueError("Не удалось получить текст статьи")

            return response.content
    except Exception as e:
        logger.error(f"Error fetching article text: {e}", exc_info=True)
        raise


async def generate_summary(messages: list) -> str:
    """Generate updated summary based on user edits"""
    try:
        request = GenerationRequest(messages=[SPMessage.from_dict(m) for m in messages])
        response = (
            await generate_content_content_generate_system_content_router_post.asyncio(
                client=content_client,
                system_content_router="article_summary",
                body=request,
            )
        )

        if not response or not response.content:
            logger.error(response.__repr__())
            logger.error(response.content.__repr__())
            raise ValueError("Не удалось сгенерировать обновленную выжимку")

        return response.content
    except Exception as e:
        logger.error(f"Error generating summary: {e}", exc_info=True)
        raise


def is_valid_url(text: str) -> bool:
    """Validate URL format"""
    return text.startswith(("http://", "https://"))
