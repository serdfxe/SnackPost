from aiogram import Bot, Dispatcher

from bot.modules.start import start_router
from bot.modules.summary import summary_router
from bot.modules.admin import admin_router
from bot.modules.profile import profile_router

from core.config import MASTER_ID, API_TOKEN


def create_dp() -> Dispatcher:
    dp = Dispatcher()

    dp.include_routers(
        start_router,
        summary_router,
        admin_router,
        profile_router,
    )

    return dp


async def main():
    bot = Bot(token=API_TOKEN)

    await bot.send_message(MASTER_ID, "START!!!")

    dp = create_dp()

    await dp.start_polling(bot)
