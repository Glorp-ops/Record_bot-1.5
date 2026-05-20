from typing import Callable, Any, Dict, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
import httpx


class HttpxClientMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[TelegramObject,Dict[str, Any]],Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]) -> Any:

        async with httpx.AsyncClient() as client:
            data['client'] = client
            return await handler(event, data)