from __future__ import annotations

from typing import TYPE_CHECKING

from ...models.reaction import MessageReactionEvent

if TYPE_CHECKING:
    from ...bot import Bot

GATEWAY_EVENT_NAME = "MESSAGE_REACTION_REMOVE_EMOJI"
INTERNAL_EVENT_NAME = "on_message_reaction_remove_emoji"


async def handle(bot: Bot, data_full: dict | None = None, data_part: dict | None = None) -> None:
    payload = data_part if isinstance(data_part, dict) else data_full if isinstance(data_full, dict) else None
    if isinstance(payload, dict):
        await bot.events.dispatch(INTERNAL_EVENT_NAME, MessageReactionEvent.from_dict(payload))
        return
    await bot.events.dispatch(INTERNAL_EVENT_NAME, payload)
