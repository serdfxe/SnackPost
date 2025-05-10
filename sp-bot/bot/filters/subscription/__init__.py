from aiogram import types
from aiogram.filters.base import Filter

from core.sp_clients import user_client
from core.sp_clients.sp_user.user_service_client.api.subscription import check_subscription_route_subscription_check_get

class IsSubscribed(Filter):
    async def __call__(self, message: types.Message) -> bool:        
        try:
            return await check_subscription_route_subscription_check_get.asyncio(
                client=user_client,
                x_user_id=message.from_user.id
            )
        except Exception:
            return False
