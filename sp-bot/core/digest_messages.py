from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

DIGEST_HEADER_MSG = """\
📅 <b>Ежедневный дайджест • {date}</b>

Я нашел {new_articles_count} новых статей из ваших источников.

👇 Ниже список с кратким описанием. Нажмите на кнопку под каждой, чтобы создать пост."""

EMPTY_DIGEST_MSG = """\
🕵️‍♂️ <b>Сегодня новых статей нет</b>

Я проверил все ваши источники, но обновлений не нашел. Следующая проверка — завтра!

Хотите добавить больше источников? Используйте /sources."""

DIGEST_FOOTER_MSG = """\
✨ <b>Итого за сегодня:</b>
• Новых статей: {total_articles}
• Самый активный источник: {top_source} ({top_source_count} статей)

<blockquote>💡 Совет дня: {random_tip}</blockquote>"""

ARTICLE_CARD_MSG = """\
📌<a href="{article_url}">{article_url}</a>"""

def get_article_card_buttons(article_id: str, article_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Создать пост", callback_data=f"create_post:{article_id}")],
        # [InlineKeyboardButton(text="🔍 Подробнее", url=article_url)]
    ])

DIGEST_TIPS = [
    "Попробуйте добавить вопрос в конец поста — это увеличит вовлеченность.",
    "Лучшее время для публикации в вашем канале — 14:00-16:00 (по данным за месяц).",
    "Статья от {source} набрала +{X}% просмотров — возможно, стоит сделать репост?",
    "Используйте эмодзи в заголовках — такие посты получают на 25% больше кликов.",
    "Опросы увеличивают вовлеченность на 40%. Попробуйте добавить один сегодня!"
]