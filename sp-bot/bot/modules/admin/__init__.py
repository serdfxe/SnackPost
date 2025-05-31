# /sp-bot/bot/modules/subscription/__init__.py

from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging

from core.sp_clients import user_client
from core.sp_clients.sp_user.user_service_client.api.user import get_user_route_user_get
from core.sp_clients.sp_user.user_service_client.api.subscription import (
    get_subscription_route_subscription_get,
    create_subscription_route_subscription_post,
    delete_subscription_route_subscription_delete,
    check_subscription_route_subscription_check_get,
)
from core.sp_clients.sp_user.user_service_client.models import (
    SubscriptionCreateDTO,
)

from bot.filters.admin import IsAdmin


logger = logging.getLogger(__name__)
admin_router = Router(name="admin_router")


class SubscriptionStates(StatesGroup):
    """FSM states for subscription management"""

    waiting_for_user_id = State()
    waiting_for_duration = State()


@admin_router.message(Command("admin", "a"), IsAdmin())
async def handle_subscription_command(message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="Проверить подписку", callback_data="check_sub")
    builder.button(text="Выдать подписку", callback_data="grant_sub")
    builder.button(text="Отменить подписку", callback_data="revoke_sub")
    builder.adjust(1)

    await message.answer(
        "⚙️ <b>Управление подписками</b>\n\n" "Выберите действие:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )


@admin_router.callback_query(F.data == "check_sub", IsAdmin())
async def handle_check_subscription(callback: CallbackQuery, state: FSMContext):
    """Handle subscription check request"""
    await callback.message.answer("🔍 Введите ID пользователя для проверки подписки:")
    await state.set_state(SubscriptionStates.waiting_for_user_id)
    await state.update_data(action="check")
    await callback.answer()


@admin_router.callback_query(F.data == "grant_sub", IsAdmin())
async def handle_grant_subscription(callback: CallbackQuery, state: FSMContext):
    """Handle subscription grant request"""
    await callback.message.answer("👤 Введите ID пользователя для выдачи подписки:")
    await state.set_state(SubscriptionStates.waiting_for_user_id)
    await state.update_data(action="grant")
    await callback.answer()


@admin_router.callback_query(F.data == "revoke_sub", IsAdmin())
async def handle_revoke_subscription(callback: CallbackQuery, state: FSMContext):
    """Handle subscription revoke request"""
    await callback.message.answer("👤 Введите ID пользователя для отмены подписки:")
    await state.set_state(SubscriptionStates.waiting_for_user_id)
    await state.update_data(action="revoke")
    await callback.answer()


@admin_router.message(SubscriptionStates.waiting_for_user_id, F.text, IsAdmin())
async def handle_user_id_input(message: Message, state: FSMContext, bot: Bot):
    """Process user ID input for subscription actions"""
    try:
        user_id = int(message.text)
        state_data = await state.get_data()
        action = state_data.get("action")

        if action == "check":
            await check_user_subscription(message, user_id, bot)
        elif action == "grant":
            await state.update_data(user_id=user_id)
            await message.answer(
                "⏳ Введите продолжительность подписки в днях (например, 30):"
            )
            await state.set_state(SubscriptionStates.waiting_for_duration)
            return
        elif action == "revoke":
            await revoke_user_subscription(message, user_id, bot)

        await state.clear()

    except ValueError:
        await message.reply("⚠️ Неверный формат ID. Введите числовой ID пользователя.")
    except Exception as e:
        logger.error(f"Error in handle_user_id_input: {e}", exc_info=True)
        await message.answer("⚠️ Ошибка при обработке запроса")
        await state.clear()


@admin_router.message(SubscriptionStates.waiting_for_duration, F.text, IsAdmin())
async def handle_duration_input(message: Message, state: FSMContext, bot: Bot):
    """Process subscription duration input"""
    try:
        duration_days = int(message.text)
        if duration_days <= 0:
            raise ValueError("Duration must be positive")

        state_data = await state.get_data()
        user_id = state_data.get("user_id")

        await grant_user_subscription(message, user_id, duration_days, bot)
        await state.clear()

    except ValueError:
        await message.reply("⚠️ Неверный формат. Введите число дней (например, 30).")
    except Exception as e:
        logger.error(f"Error in handle_duration_input: {e}", exc_info=True)
        await message.answer("⚠️ Ошибка при создании подписки")
        await state.clear()


async def check_user_subscription(message: Message, user_id: int, bot: Bot):
    """Check user subscription status"""
    try:
        # First check if user exists
        user_response = await get_user_route_user_get.asyncio(
            client=user_client, x_user_id=user_id
        )

        if not user_response:
            await message.reply(f"❌ Пользователь с ID {user_id} не найден.")
            return

        # Check subscription status
        sub_response = await check_subscription_route_subscription_check_get.asyncio(
            client=user_client, x_user_id=user_id
        )

        if sub_response:
            subscription = await get_subscription_route_subscription_get.asyncio(
                client=user_client, x_user_id=user_id
            )

            expires_at = (
                subscription.expires_at.strftime("%d.%m.%Y %H:%M")
                if subscription.expires_at
                else "не указано"
            )
            status = "✅ Активна" if subscription.is_active else "❌ Неактивна"

            await message.reply(
                f"📋 <b>Информация о подписке</b>\n\n"
                f"👤 Пользователь: {user_response.first_name} (@{user_response.username})\n"
                f"🆔 ID: {user_id}\n"
                f"🔹 Статус: {status}\n"
                f"📅 Истекает: {expires_at}",
                parse_mode="HTML",
            )
        else:
            await message.reply(
                f"ℹ️ У пользователя {user_response.first_name} (@{user_response.username}) нет активной подписки."
            )

    except Exception as e:
        if "404" in str(e):
            await message.reply(f"ℹ️ У пользователя с ID {user_id} нет подписки.")
        else:
            logger.error(f"Error checking subscription: {e}", exc_info=True)
            await message.reply("⚠️ Ошибка при проверке подписки")


async def grant_user_subscription(
    message: Message, user_id: int, duration_days: int, bot: Bot
):
    """Grant subscription to user"""
    try:
        from datetime import datetime, timedelta

        expires_at = datetime.now() + timedelta(days=duration_days)

        # First check if user exists
        user_response = await get_user_route_user_get.asyncio(
            client=user_client, x_user_id=user_id
        )

        if not user_response:
            await message.reply(f"❌ Пользователь с ID {user_id} не найден.")
            return

        # Create or update subscription
        sub_data = SubscriptionCreateDTO(
            user_id=user_id, is_active=True, expires_at=expires_at
        )

        response = await create_subscription_route_subscription_post.asyncio(
            client=user_client, body=sub_data
        )

        expires_at_str = expires_at.strftime("%d.%m.%Y %H:%M")
        await message.reply(
            f"✅ <b>Подписка успешно выдана</b>\n\n"
            f"👤 Пользователь: {user_response.first_name} (@{user_response.username})\n"
            f"🆔 ID: {user_id}\n"
            f"📅 Истекает: {expires_at_str}\n"
            f"⏳ Срок: {duration_days} дней",
            parse_mode="HTML",
        )

        # Notify user
        try:
            await bot.send_message(
                user_id,
                f"🎉 Вам выдана подписка на {duration_days} дней!\n\n"
                f"Действует до: {expires_at_str}\n\n"
                f"Теперь вы можете пользоваться всеми функциями бота.",
            )
        except Exception as e:
            logger.warning(f"Could not notify user {user_id}: {e}")

    except Exception as e:
        logger.error(f"Error granting subscription: {e}", exc_info=True)
        if "409" in str(e):
            await message.reply(f"⚠️ У пользователя уже есть активная подписка.")
        else:
            await message.reply("⚠️ Ошибка при выдаче подписки")


async def revoke_user_subscription(message: Message, user_id: int, bot: Bot):
    """Revoke user subscription"""
    try:
        # First check if user exists
        user_response = await get_user_route_user_get.asyncio(
            client=user_client, x_user_id=user_id
        )

        if not user_response:
            await message.reply(f"❌ Пользователь с ID {user_id} не найден.")
            return

        # Check if subscription exists
        try:
            await get_subscription_route_subscription_get.asyncio(
                client=user_client, x_user_id=user_id
            )
        except Exception as e:
            if "404" in str(e):
                await message.reply(f"ℹ️ У пользователя с ID {user_id} нет подписки.")
                return
            raise

        # Delete subscription
        await delete_subscription_route_subscription_delete.asyncio(
            client=user_client, x_user_id=user_id
        )

        await message.reply(
            f"✅ <b>Подписка успешно отменена</b>\n\n"
            f"👤 Пользователь: {user_response.first_name} (@{user_response.username})\n"
            f"🆔 ID: {user_id}",
            parse_mode="HTML",
        )

        # Notify user
        try:
            await bot.send_message(
                user_id,
                "ℹ️ Ваша подписка была отменена администратором.\n\n"
                "Вы больше не можете пользоваться премиум-функциями бота.",
            )
        except Exception as e:
            logger.warning(f"Could not notify user {user_id}: {e}")

    except Exception as e:
        logger.error(f"Error revoking subscription: {e}", exc_info=True)
        await message.reply("⚠️ Ошибка при отмене подписки")
