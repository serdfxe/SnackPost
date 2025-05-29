from aiogram import Bot, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, LinkPreviewOptions
from aiogram.filters import Command

from datetime import date

import logging

from bot.filters.subscription import IsSubscribed
from bot.utils.admin import notify_admin

from core.sp_clients import scraper_client
from core.sp_clients.sp_scraper.scraper_service_client.api.digest import get_digest_route_digest_get
from core.sp_clients.sp_scraper.scraper_service_client.models.digest_schema import DigestSchema 

from core.digest_messages import (
    DIGEST_FOOTER_MSG,
    DIGEST_HEADER_MSG,
    DIGEST_TIPS,
    get_article_card_buttons,
    EMPTY_DIGEST_MSG,
    ARTICLE_CARD_MSG,
)


logger = logging.getLogger(__name__)
digest_router = Router(name="digest_router")


async def show_article(article, bot: Bot):
    ...

async def show_digest(message: Message, edit: bool = False):
    mess = await message.answer(
        "🔎 Загружаю дайджест...",
        parse_mode="HTML",
    )

    if message.from_user.id in (894361829, 148636247):
        await mess.edit_text(
            EMPTY_DIGEST_MSG,
            parse_mode="HTML",
        )

        await message.answer(
"""\
🔍 <b>Новых статей не нашлось, но вот что стоит перечитать или открыть для себя заново:</b>

1. <b>«Признание: я больше не знаю, как писать стратегические документы без ИИ»</b>

🤖 Провокационный взгляд на изменившиеся workflows в эпоху ChatGPT
🔗 <a href="https://creatoreconomy.so/p/confession-i-dont-know-how-to-write">Читать в Creator Economy</a>
📊 Опрос: "Вы уже не можете работать без ИИ-ассистентов?"

2. <b>«Карты идей 101: как использовать их в вашей стратегии»</b>

🗺️ Альтернатива скучным дорожным картам — визуальный метод приоритизации
🔗 <a href="https://theproductmanager.com/topics/idea-maps/">Гайд на The Product Manager</a>
✂️ Совет: сохраните в закладки — пригодится для следующего планирования

3. <b>«Продукт на практике: Оценка необходимости нового API»</b>

📌 Практический гайд от Терезы Торрес с чек-листом для принятия технических решений
🔗 <a href="https://www.producttalk.org/2025/05/evaluating-a-new-api/">Читать на Product Talk</a>
💡 "Как вы оцениваете необходимость интеграции нового API?"
""",
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        
        return


    digest = await get_digest_route_digest_get.asyncio(
        client=scraper_client,
        x_user_id=message.from_user.id,
    )

    if len(digest.articles) == 0:
        await mess.edit_text(
            EMPTY_DIGEST_MSG,
            parse_mode="HTML",
        )
        return

    await mess.edit_text(
        DIGEST_HEADER_MSG.format(date=date.today().strftime('%d.%m.%Y'), new_articles_count=len(digest.articles)),
        parse_mode="HTML",
    )

    for i in digest.articles:
        await message.answer(
            ARTICLE_CARD_MSG.format(
                article_url=f"{i['title'] or i['link']}",
            ),
            reply_markup=get_article_card_buttons(i["id"], i["link"]),
            parse_mode="HTML",
            link_preview_options=LinkPreviewOptions(is_disabled=False, prefer_small_media=True, show_above_text=True, url=i["link"]),
        )
    
    # await message.answer(
    #     DIGEST_FOOTER_MSG,
    #     parse_mode="HTML",
    # )


@digest_router.message(Command("digest"), IsSubscribed())
async def handle_digest_command(message: Message, bot: Bot):
    """Handle the sources command"""
    try:
        await notify_admin(bot, message, "Opened digest")
        await show_digest(message)
    except Exception as e:
        logger.error(f"Error in handle_sources_command: {e}", exc_info=True)
        await message.answer("⚠️ Ошибка при открытии дайджеста")


@digest_router.message(Command("digest"), ~IsSubscribed())
async def handle_sources_command_not_sub(message: Message):
    """Handle sources command when not subscribed"""
    await message.answer("!!!", parse_mode="HTML")
