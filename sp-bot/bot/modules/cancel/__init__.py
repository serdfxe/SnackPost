from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State

cancel_router = Router(name="cancel_router")


@cancel_router.message(Command("cancel"))
@cancel_router.callback_query(F.data == "cancel")
async def cancel_handler(
    message_or_callback: Message | CallbackQuery, state: FSMContext
):
    """Universal cancel command that works in any state"""
    try:
        # Получаем текущее состояние
        current_state = await state.get_state()

        # Если состояние не установлено - ничего не делаем
        if current_state is None:
            if isinstance(message_or_callback, Message):
                await message_or_callback.answer("ℹ️ Нет активных действий для отмены")
            else:
                await message_or_callback.answer()
            return

        # Отменяем текущее состояние
        await state.clear()

        # Отправляем ответ в зависимости от типа входящего сообщения
        if isinstance(message_or_callback, Message):
            await message_or_callback.answer(
                "❌ Действие отменено",
                reply_markup=None,  # Удаляем клавиатуру если была
            )
        else:
            await message_or_callback.message.edit_text(
                "❌ Действие отменено", reply_markup=None
            )
            await message_or_callback.answer()

    except Exception as e:
        logger.error(f"Error in cancel_handler: {e}", exc_info=True)
        if isinstance(message_or_callback, Message):
            await message_or_callback.answer("⚠️ Ошибка при отмене действия")
        else:
            await message_or_callback.message.answer("⚠️ Ошибка при отмене действия")
            await message_or_callback.answer()
