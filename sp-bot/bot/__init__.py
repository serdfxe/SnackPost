from aiogram import Bot, Dispatcher

from bot.modules.start import start_router

from core.config import ADMIN_ID, API_TOKEN


def create_dp() -> Dispatcher:
    dp = Dispatcher()

    dp.include_routers(
        start_router,
    )

    return dp


async def main():
    bot = Bot(token=API_TOKEN)

    await bot.send_message(ADMIN_ID, "START!!!")

    dp = create_dp()

    await dp.start_polling(bot)
