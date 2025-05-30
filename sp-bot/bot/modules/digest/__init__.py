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
    
    if message.from_user.id in (894361829, 148636247):
        await message.answer(
"""\
🔍 <b>Так же вот, что на мой взгляд стоит перечитать или открыть для себя заново:</b>

1. <b>«Критическое мышление для продуктовых команд»</b>

🧠 Методики Терезы Торрес для принятия взвешенных продуктовых решений
🔗 <a href="https://www.mindtheproduct.com/critical-thinking-product-teams-teresa-torres/">Читать на Mind the Product</a>
🤔 "Как часто вы подвергаете сомнению свои ключевые предположения?"

2. <b>«Продукт, дизайн и ИИ»</b>

🎨 Как нейросети меняют подход к проектированию пользовательского опыта
🔗 <a href="https://www.svpg.com/product-design-and-ai/">Читать на SVPG</a>
🖌️ Кейс: "Какие элементы дизайна уже можно доверить ИИ?"

3. <b>«Как Binance и N26 строят продуктовые процессы»</b>

⚡ Нестандартные подходы от топ-компаний: от плоских структур до ежедневных воркшопов
🔗 <a href="https://www.lennysnewsletter.com/p/unorthodox-product-lessons-from-n26-and-more">Читать в Lenny's Newsletter</a>
💼 "Какой необычный процесс вы внедряли в своей команде?"
""",
            parse_mode="HTML",
            disable_web_page_preview=True,
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
