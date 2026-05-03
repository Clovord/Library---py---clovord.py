from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...models.message import Message
from ...utils.logger import get_logger

logger = get_logger()

import json

if TYPE_CHECKING:
    from ...bot import Bot

GATEWAY_EVENT_NAME = "GATEWAY_ERROR"
INTERNAL_EVENT_NAME = "on_gateway_error"


async def handle(bot: Bot, data: Any) -> None:
    if isinstance(data, dict):
        payload = data(Message.from_dict(data))

    payload = data

    event = payload.get("d",).get("request").get("event", "UNKNOWN_EVENT")

    code = payload.get("d",).get("request").get("code", "UNKNOWN_CODE")
    message = payload.get("d",).get("request").get("message", "UNKNOWN_MESSAGE")


    logger.error(f"The gateway encountered an error for event '{event}' with code '{code}' and message '{message}'")
    logger.error("It is advised to build an handler for this event to log the error details and take appropriate action.")

    await bot.events.dispatch(INTERNAL_EVENT_NAME, payload)
    
