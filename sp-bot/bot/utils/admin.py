from aiogram import Bot
from aiogram.types import Message, CallbackQuery

import logging

from core.config import MASTER_ID


logger = logging.getLogger(__name__)


async def notify_admin(bot: Bot, message: Message | CallbackQuery, action: str, details: str = ""):
    """Send notification to admin about user action"""
    try:
        if MASTER_ID:
            user = message.from_user
            text = (f"👤 <b>User action</b>\n"
                    f"ID: {user.id}\n"
                    f"Name: {user.full_name}\n"
                    f"Username: @{user.username}\n"
                    f"Action: {action}\n"
                    f"Details: \n{details}")
            await bot.send_message(MASTER_ID, text, parse_mode="HTML", disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Error sending admin notification: {e}")