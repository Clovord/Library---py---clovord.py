from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...bot import Bot

GATEWAY_EVENT_NAME = "ACTIVITY_JOIN"
INTERNAL_EVENT_NAME = "on_activity_join"


async def handle(bot: Bot, data_full: dict[str, Any] | None = None, data_part: dict[str, Any] | None = None) -> None:
    if not isinstance(data_part, dict):
        raise TypeError("ACTIVITY_JOIN payload must be a dict")
    await bot.events.dispatch(INTERNAL_EVENT_NAME, data_part)
