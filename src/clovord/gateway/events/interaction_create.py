from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...bot import Bot


async def handle(bot: Bot, data_full: Any, data_part: Any) -> None:
    payload = data_part if isinstance(data_part, dict) else data_full
    if isinstance(payload, dict) and hasattr(bot, "tree"):
        try:
            handled = await bot.tree.dispatch(payload)
            if handled:
                return
        except Exception:
            pass
    event_payload = data_part if isinstance(data_part, dict) else data_full
    logger = getattr(bot, "_logger", None)
    if logger is not None and isinstance(event_payload, dict):
        try:
            logger.debug(
                "INTERACTION_CREATE type=%s custom_id=%s name=%s",
                event_payload.get("type"),
                (event_payload.get("data") or {}).get("custom_id")
                if isinstance(event_payload.get("data"), dict)
                else None,
                (event_payload.get("data") or {}).get("name")
                if isinstance(event_payload.get("data"), dict)
                else None,
            )
        except Exception:
            pass
    await bot.events.dispatch("on_interaction_create", data_full, data_part)
