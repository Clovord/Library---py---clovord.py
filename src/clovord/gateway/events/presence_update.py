from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...bot import Bot

GATEWAY_EVENT_NAME = "PRESENCE_UPDATE"
INTERNAL_EVENT_NAME = "on_presence_update"


def _normalize_user(user_data: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(user_data)
    username = normalized.get("username") or normalized.get("name") or "unknown"
    normalized["username"] = username
    if "name" not in normalized and "username" in normalized:
        normalized["name"] = normalized.get("username")
    return normalized


def _to_object(value: Any) -> Any:
    if isinstance(value, dict):
        return SimpleNamespace(**{k: _to_object(v) for k, v in value.items()})
    if isinstance(value, list):
        return [_to_object(v) for v in value]
    return value


def _build_presence_states(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    user_data = _normalize_user(data.get("user") or {})
    presence_data = data.get("presence") or {}

    before = dict(presence_data.get("before") or {})
    after = dict(presence_data.get("after") or {})

    # Backward compatibility: older payloads may only provide presence status directly.
    if not after and presence_data:
        if "status" in presence_data or "custom_status" in presence_data:
            after = {
                "status": presence_data.get("status"),
                "custom_status": presence_data.get("custom_status"),
            }

    if "user" not in before:
        before["user"] = user_data
    if "user" not in after:
        after["user"] = user_data

    return before, after

async def handle(bot: Bot, data_full: dict[str, Any] | None = None, data_part: dict[str, Any] | None = None) -> None:
    if not isinstance(data_part, dict):
        raise TypeError("PRESENCE_UPDATE payload must be a dict")

    before_state, after_state = _build_presence_states(data_part)
    await bot.events.dispatch(
        INTERNAL_EVENT_NAME,
        _to_object(before_state),
        _to_object(after_state),
    )
