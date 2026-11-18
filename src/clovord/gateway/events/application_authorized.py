from __future__ import annotations

from typing import TYPE_CHECKING

from ...models.guild import Guild

if TYPE_CHECKING:
    from ...bot import Bot

GATEWAY_EVENT_NAME = "APPLICATION_AUTHORIZED"
INTERNAL_EVENT_NAME = "on_application_authorized"


async def handle(bot: Bot, data_full: dict | None = None, data_part: dict | None = None) -> None:
    if isinstance(data_part, dict):
        guild_payload = data_part.get("guild")
        if isinstance(guild_payload, dict):
            guild = Guild.from_dict(guild_payload, bot=bot)
            bot._cache_guild(guild)
            await bot.events.dispatch(INTERNAL_EVENT_NAME, guild)
            return

    await bot.events.dispatch(INTERNAL_EVENT_NAME, data_part)
