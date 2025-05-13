import asyncio
from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import logging
from urllib.parse import urlparse

from core.messages import (
    SOURCES_MENU_MSG,
    ADD_SOURCE_MSG,
    SOURCE_ADDED_MSG,
    INVALID_SOURCE_MSG,
    SOURCE_LIST_MSG,
    DELETE_SOURCE_MSG,
    SOURCE_DELETED_MSG,
    NOTIFICATION_SETTINGS_MSG,
    TIME_UPDATED_MSG,
    SOURCES_SUBSCRIPTION_REQUIRED_MSG,
    SUBSCRIPTION_REQUIRED_MSG
)
from core.config import MASTER_ID
from bot.filters.subscription import IsSubscribed

logger = logging.getLogger(__name__)
source_router = Router(name="source_router")

class SourcesStates(StatesGroup):
    """FSM states for sources management"""
    waiting_for_source_url = State()
    waiting_for_delete_confirmation = State()
    waiting_for_time_selection = State()

# Заглушки для работы с бэкендом
async def add_user_source(user_id: int, url: str, source_type: str) -> bool:
    """Add new source for user (stub)"""
    logger.info(f"Adding source for user {user_id}: {url} ({source_type})")
    return True

async def get_user_sources(user_id: int) -> list[dict]:
    """Get user sources list (stub)"""
    return [
        {"id": 1, "url": "https://example.com/rss", "type": "rss"},
        {"id": 2, "url": "https://example.com/blog", "type": "website"}
    ]

async def delete_user_source(user_id: int, source_id: int) -> bool:
    """Delete user source (stub)"""
    logger.info(f"Deleting source {source_id} for user {user_id}")
    return True

async def set_user_notification_time(user_id: int, time: str) -> bool:
    """Set notification time for user (stub)"""
    logger.info(f"Setting notification time for user {user_id}: {time}")
    return True

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
                   f"Details: {details}")
            await bot.send_message(MASTER_ID, text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error sending admin notification: {e}")

def is_valid_source_url(url: str) -> bool:
    """Validate source URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme in ('http', 'https'), result.netloc])
    except ValueError:
        return False

def determine_source_type(url: str) -> str:
    """Determine source type by URL"""
    if url.endswith(('.rss', '.xml')) or '/rss' in url:
        return 'rss'
    return 'website'

@source_router.message(Command("sources"), IsSubscribed())
async def handle_sources_command(message: Message, state: FSMContext, bot: Bot):
    """Handle the sources command"""
    try:
        await notify_admin(bot, message, "Opened sources menu")
        await show_sources_menu(message)
    except Exception as e:
        logger.error(f"Error in handle_sources_command: {e}", exc_info=True)
        await message.answer("⚠️ Ошибка при открытии меню источников")

@source_router.message(Command("sources"), ~IsSubscribed())
async def handle_sources_command_not_sub(message: Message):
    """Handle sources command when not subscribed"""
    await message.answer(SOURCES_SUBSCRIPTION_REQUIRED_MSG, parse_mode="HTML")

async def show_sources_menu(message: Message):
    """Show main sources management menu"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить источник", callback_data="add_source")],
        [InlineKeyboardButton(text="🗂 Мои источники", callback_data="list_sources")],
        [InlineKeyboardButton(text="⏰ Настроить время", callback_data="set_notification_time")],
    ])
    await message.answer(SOURCES_MENU_MSG, parse_mode="HTML", reply_markup=keyboard)

@source_router.callback_query(F.data == "sources_menu")
async def back_to_sources_menu(callback: CallbackQuery, state: FSMContext):
    """Return to sources menu"""
    await state.clear()
    await callback.message.edit_text(SOURCES_MENU_MSG, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить источник", callback_data="add_source")],
        [InlineKeyboardButton(text="🗂 Мои источники", callback_data="list_sources")],
        [InlineKeyboardButton(text="⏰ Настроить время", callback_data="set_notification_time")],
    ]))
    await callback.answer()

@source_router.callback_query(F.data == "add_source")
async def add_source_callback(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Start adding new source"""
    await notify_admin(bot, callback, "Started adding source")
    await callback.message.edit_text(ADD_SOURCE_MSG, parse_mode="HTML")
    await state.set_state(SourcesStates.waiting_for_source_url)
    await callback.answer()

@source_router.message(SourcesStates.waiting_for_source_url, F.text & ~F.text.startswith("/"))
async def handle_source_url_input(message: Message, state: FSMContext, bot: Bot):
    """Process user-provided source URL"""
    try:
        url = message.text.strip()
        if not is_valid_source_url(url):
            await message.reply(INVALID_SOURCE_MSG, parse_mode="HTML")
            return
        
        source_type = determine_source_type(url)
        success = await add_user_source(message.from_user.id, url, source_type)
        
        if not success:
            raise Exception("Failed to add source")
        
        await notify_admin(bot, message, "Added new source", f"{url} ({source_type})")
        await message.answer(SOURCE_ADDED_MSG, parse_mode="HTML")
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error in handle_source_url_input: {e}", exc_info=True)
        await message.answer("⚠️ Ошибка при добавлении источника")
        await state.clear()

@source_router.callback_query(F.data == "list_sources")
async def list_user_sources(callback: CallbackQuery, bot: Bot):
    """Show list of user's sources"""
    try:
        sources = await get_user_sources(callback.from_user.id)
        if not sources:
            await callback.message.edit_text("📭 У вас пока нет добавленных источников", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="sources_menu")]
            ]))
            return
        
        source_list = "\n".join(
            f"{i+1}. <code>{source['url']}</code> ({source['type']})"
            for i, source in enumerate(sources))
        
        await callback.message.edit_text(
            SOURCE_LIST_MSG.format(count=len(sources), source_list=source_list),
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🗑 Удалить", callback_data="delete_source")],
                [InlineKeyboardButton(text="🔙 Назад", callback_data="sources_menu")]
            ])
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in list_user_sources: {e}", exc_info=True)
        await callback.message.edit_text("⚠️ Ошибка при загрузке списка источников")
        await callback.answer()

@source_router.callback_query(F.data == "delete_source")
async def start_delete_source(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Start source deletion process"""
    try:
        sources = await get_user_sources(callback.from_user.id)
        if not sources:
            await callback.answer("Нет источников для удаления")
            return
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"❌ {source['url']}", callback_data=f"confirm_delete_{source['id']}")]
            for source in sources
        ] + [
            [InlineKeyboardButton(text="🔙 Назад", callback_data="list_sources")]
        ])
        
        await callback.message.edit_text(DELETE_SOURCE_MSG, parse_mode="HTML", reply_markup=keyboard)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in start_delete_source: {e}", exc_info=True)
        await callback.message.edit_text("⚠️ Ошибка при подготовке удаления")
        await callback.answer()

@source_router.callback_query(F.data.startswith("confirm_delete_"))
async def confirm_delete_source(callback: CallbackQuery, bot: Bot):
    """Confirm and delete source"""
    try:
        source_id = int(callback.data.split("_")[-1])
        success = await delete_user_source(callback.from_user.id, source_id)
        
        if not success:
            raise Exception("Failed to delete source")
        
        await notify_admin(bot, callback, "Deleted source", f"ID: {source_id}")
        await callback.message.edit_text(SOURCE_DELETED_MSG, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 К списку", callback_data="list_sources")]
        ]))
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in confirm_delete_source: {e}", exc_info=True)
        await callback.message.edit_text("⚠️ Ошибка при удалении источника")
        await callback.answer()

@source_router.callback_query(F.data == "set_notification_time")
async def set_notification_time(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Set notification time for daily updates"""
    try:
        await callback.message.edit_text(
            NOTIFICATION_SETTINGS_MSG,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Утро (09:00)", callback_data="set_time_09:00")],
                [InlineKeyboardButton(text="День (14:00)", callback_data="set_time_14:00")],
                [InlineKeyboardButton(text="Вечер (19:00)", callback_data="set_time_19:00")],
                [InlineKeyboardButton(text="🔙 Назад", callback_data="sources_menu")]
            ])
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in set_notification_time: {e}", exc_info=True)
        await callback.message.edit_text("⚠️ Ошибка при настройке времени")
        await callback.answer()

@source_router.callback_query(F.data.startswith("set_time_"))
async def handle_time_selection(callback: CallbackQuery, bot: Bot):
    """Handle notification time selection"""
    try:
        time = callback.data.replace("set_time_", "")
        success = await set_user_notification_time(callback.from_user.id, time)
        
        if not success:
            raise Exception("Failed to set notification time")
        
        await notify_admin(bot, callback, "Set notification time", time)
        await callback.message.edit_text(
            TIME_UPDATED_MSG.format(time=time),
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="sources_menu")]
            ])
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in handle_time_selection: {e}", exc_info=True)
        await callback.message.edit_text("⚠️ Ошибка при сохранении времени")
        await callback.answer()
