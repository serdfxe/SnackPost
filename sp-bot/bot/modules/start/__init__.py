from aiogram import Bot, Router
from aiogram.types import Message
from aiogram.filters import Command

from core.config import ADMIN_ID
from core.messages import HELLO_MSG


start_router = Router(name="start_router")


@start_router.message(Command("start"))
async def registered_start_message_handler(message: Message, bot: Bot):
    await message.answer(HELLO_MSG)

    username = (
        message.from_user.username.replace("_", "\\_")
        if message.from_user.username
        else None
    )
    await bot.send_message(
        ADMIN_ID,
        f"""#user #{message.text.split(maxsplit=2)[-1]}\n\nid=`{message.from_user.id}`\nfirst\_name=`{message.from_user.first_name}`\nlast\_name=`{message.from_user.last_name}`\nusername=@{username}""",
        parse_mode="Markdown",
    )
