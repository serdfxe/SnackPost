from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging
from datetime import datetime

from core.sp_clients import user_client
from core.sp_clients.sp_user.user_service_client.api.subscription import (
    get_subscription_route_subscription_get,
    check_subscription_route_subscription_check_get
)
from core.messages import (
    PROFILE_MSG,
    NO_SUBSCRIPTION_MSG,
    SUBSCRIPTION_INFO_MSG,
    PAYMENT_OPTIONS_MSG
)

from bot.filters.subscription import IsSubscribed

logger = logging.getLogger(__name__)
profile_router = Router(name="profile_router")

@profile_router.message(Command("profile", "p"))
async def handle_profile_command(message: Message):
    """Show user profile with subscription info"""
    try:
        builder = InlineKeyboardBuilder()
        builder.button(text="🔄 Проверить подписку", callback_data="check_subscription")
        # builder.button(text="💳 Оформить подписку", callback_data="buy_subscription")
        builder.adjust(1)
        
        await message.answer(
            PROFILE_MSG,
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in handle_profile_command: {e}", exc_info=True)
        await message.answer("⚠️ Ошибка при загрузке профиля")

@profile_router.callback_query(F.data == "check_subscription")
async def handle_check_subscription(callback: CallbackQuery):
    """Check user subscription status"""
    try:
        user_id = callback.from_user.id
        has_subscription = await check_subscription_route_subscription_check_get.asyncio(
            client=user_client,
            x_user_id=user_id
        )
        
        if has_subscription:
            subscription = await get_subscription_route_subscription_get.asyncio(
                client=user_client,
                x_user_id=user_id
            )
            
            expires_at = subscription.expires_at.strftime("%d.%m.%Y") if subscription.expires_at else "не указана"
            status = "✅ Активна" if subscription.is_active else "❌ Неактивна"
            
            await callback.message.edit_text(
                SUBSCRIPTION_INFO_MSG.format(
                    status=status,
                    expires_at=expires_at
                ),
                parse_mode="HTML"
            )
        else:
            await callback.message.edit_text(
                NO_SUBSCRIPTION_MSG,
                parse_mode="HTML"
            )
            
        # Show payment options if no active subscription
        # if not has_subscription:
        #     builder = InlineKeyboardBuilder()
        #     builder.button(text="1 месяц - 299₽", callback_data="sub_1_month")
        #     builder.button(text="3 месяца - 799₽", callback_data="sub_3_months")
        #     builder.button(text="1 год - 2999₽", callback_data="sub_1_year")
        #     builder.adjust(1)
            
        #     await callback.message.answer(
        #         PAYMENT_OPTIONS_MSG,
        #         reply_markup=builder.as_markup(),
        #         parse_mode="HTML"
        #     )
            
    except Exception as e:
        logger.error(f"Error in handle_check_subscription: {e}", exc_info=True)
        await callback.message.answer("⚠️ Ошибка при проверке подписки")

@profile_router.callback_query(F.data.startswith("sub_"))
async def handle_subscription_purchase(callback: CallbackQuery):
    """Handle subscription purchase"""
    try:
        # Here you would integrate with your payment provider
        # For now, we'll just show a message
        duration = {
            "sub_1_month": "1 месяц",
            "sub_3_months": "3 месяца",
            "sub_1_year": "1 год"
        }.get(callback.data, "неизвестный период")
        
        await callback.message.edit_text(
            f"💳 Вы выбрали подписку на <b>{duration}</b>.\n\n"
            "Для завершения оплаты следуйте инструкциям платежного сервиса.\n\n"
            "После успешной оплаты подписка будет активирована автоматически.",
            parse_mode="HTML"
        )
        
        # In a real implementation, you would:
        # 1. Create a payment invoice
        # 2. Send it to user
        # 3. Handle payment confirmation
        # 4. Activate subscription via API
        
    except Exception as e:
        logger.error(f"Error in handle_subscription_purchase: {e}", exc_info=True)
        await callback.message.answer("⚠️ Ошибка при оформлении подписки")
