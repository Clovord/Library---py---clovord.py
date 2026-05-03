from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...bot import Bot

GATEWAY_EVENT_NAME = "PRESENCE_UPDATE"
INTERNAL_EVENT_NAME = "on_presence_update"


def _normalize_user(user_data: Any) -> dict[str, Any] | None:
    if not isinstance(user_data, dict):
        return None

    normalized = dict(user_data)
    if "name" not in normalized and "username" in normalized:
        normalized["name"] = normalized.get("username")
    return normalized


def _to_object(value: Any) -> Any:
    if isinstance(value, dict):
        return SimpleNamespace(**{k: _to_object(v) for k, v in value.items()})
    if isinstance(value, list):
        return [_to_object(v) for v in value]
    return value


def _build_presence_states(data: dict[str, Any]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    user_data = _normalize_user(data.get("user"))
    presence_data = data.get("presence") if isinstance(data.get("presence"), dict) else {}

    before = presence_data.get("before") if isinstance(presence_data.get("before"), dict) else None
    after = presence_data.get("after") if isinstance(presence_data.get("after"), dict) else None

    # Backward compatibility: older payloads may only provide presence status directly.
    if after is None and presence_data:
        if "status" in presence_data or "custom_status" in presence_data:
            after = {
                "status": presence_data.get("status"),
                "custom_status": presence_data.get("custom_status"),
            }

    if user_data is not None:
        if isinstance(before, dict) and "user" not in before:
            before = {**before, "user": user_data}
        if isinstance(after, dict) and "user" not in after:
            after = {**after, "user": user_data}

    return before, after

async def handle(bot: Bot, data_full: dict = None, data_part: dict = None) -> None:

    before_state, after_state = _build_presence_states(data_full)
    await bot.events.dispatch(
        INTERNAL_EVENT_NAME,
        before=_to_object(before_state),
        after=_to_object(after_state),
    )
