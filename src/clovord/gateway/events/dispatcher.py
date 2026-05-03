from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

from ...utils.logger import get_logger

if TYPE_CHECKING:
    from ...bot import Bot


_logger = get_logger()


async def dispatch_gateway_event(bot: Bot, event_name: str, data: Any) -> None:
    module_name = event_name.lower()
    target = f"clovord.gateway.events.{module_name}"

    try:
        module = import_module(target)
    except ModuleNotFoundError as exc:
        # Fallback only when the event module itself does not exist.
        if exc.name != target:
            raise
        await bot.events.dispatch(f"on_{module_name}", data)
        return

    handler = getattr(module, "handle", None)
    if handler is None:
        return

    await handler(bot, data)
