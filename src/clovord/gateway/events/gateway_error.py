from __future__ import annotations

from typing import TYPE_CHECKING, Any
from datetime import datetime

from ...models.message import Message
from ...utils.logger import get_logger

logger = get_logger()

import json

if TYPE_CHECKING:
    from ...bot import Bot

GATEWAY_EVENT_NAME = "GATEWAY_ERROR"
INTERNAL_EVENT_NAME = "on_gateway_error"


async def handle(bot: Bot, data_full: dict | None = None, data_part: dict | None = None) -> None:
    payload = data_part if isinstance(data_part, dict) else {}
    request = payload.get("request") if isinstance(payload.get("request"), dict) else {}
    status = payload.get("status") if isinstance(payload.get("status"), dict) else {}

    event = request.get("event", "UNKNOWN_EVENT")
    code = status.get("code", "UNKNOWN_CODE")
    message = status.get("code_message", "UNKNOWN_MESSAGE")


    logger.error(f"The gateway encountered an error for event '{event}' with code '{code}' and message '{message}'")
    logger.error("It is advised to build an handler for this event to log the error details and take appropriate action.")


    await bot.events.dispatch(INTERNAL_EVENT_NAME, payload)
    
