from aiogram import Bot, Router
from aiogram.types import Message
from aiogram.filters import Command

from core.config import MASTER_ID
from core.messages import HELLO_MSG

from core.sp_clients import user_client
from core.sp_clients.sp_user.user_service_client.api.user import post_user_route_user_post
from core.sp_clients.sp_user.user_service_client.models.user_create_dto import UserCreateDTO

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
        MASTER_ID,
        f"""#user #{message.text.split(maxsplit=2)[-1]}\n\nid=`{message.from_user.id}`\nfirst\_name=`{message.from_user.first_name}`\nlast\_name=`{message.from_user.last_name}`\nusername=@{username}""",
        parse_mode="Markdown",
    )

    await post_user_route_user_post.asyncio(
        client=user_client,
        body=UserCreateDTO(
            user_id=message.from_user.id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
        )
    )
