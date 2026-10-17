from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ._helpers import optional_str, snowflake_str


@dataclass(slots=True)
class MessageReactionEvent:
    """Gateway payload for a single emoji reaction change."""

    message_id: str
    channel_id: str
    guild_id: str | None = None
    user_id: str | None = None
    emoji: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> MessageReactionEvent:
        data = payload if isinstance(payload, dict) else {}
        emoji = data.get("emoji") if isinstance(data.get("emoji"), dict) else {}
        return cls(
            message_id=snowflake_str(data.get("message_id")),
            channel_id=snowflake_str(data.get("channel_id")),
            guild_id=optional_str(data.get("guild_id")),
            user_id=optional_str(data.get("user_id")),
            emoji=dict(emoji),
            raw=dict(data),
        )
