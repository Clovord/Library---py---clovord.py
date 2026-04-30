from __future__ import annotations

from collections.abc import Awaitable, Callable

from .utils.logger import get_logger

EventHandler = Callable[..., Awaitable[None]]


class EventManager:
    """Registers and dispatches user-defined async event callbacks."""

    def __init__(self) -> None:
        self._handlers: dict[str, EventHandler] = {}
        self._logger = get_logger()

    def register(self, name: str, handler: EventHandler) -> None:
        self._handlers[name] = handler

    def get(self, name: str) -> EventHandler | None:
        return self._handlers.get(name)

    async def dispatch(self, name: str, *args: object, **kwargs: object) -> None:
        handler = self._handlers.get(name)
        if handler is None:
            return

        try:
            await handler(*args, **kwargs)
        except Exception as exc:
            self._logger.exception("Event handler failed for %s: %s", name, exc)
