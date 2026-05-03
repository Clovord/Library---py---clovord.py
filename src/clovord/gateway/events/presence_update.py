from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...models.message import Message

if TYPE_CHECKING:
    from ...bot import Bot

GATEWAY_EVENT_NAME = "PRESENCE_UPDATE"
INTERNAL_EVENT_NAME = "on_presence_update"

async def handle(bot: Bot, data: Any) -> None:
    if isinstance(data, dict):
        await bot.events.dispatch(INTERNAL_EVENT_NAME, Message.from_dict(data))
        return

    await bot.events.dispatch(INTERNAL_EVENT_NAME, data)
