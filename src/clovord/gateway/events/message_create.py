from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...models.message import Message

if TYPE_CHECKING:
    from ...bot import Bot


async def handle(bot: Bot, data: Any) -> None:
    if isinstance(data, dict):
        await bot.events.dispatch("on_message_create", Message.from_dict(data))
        return

    await bot.events.dispatch("on_message_create", data)
