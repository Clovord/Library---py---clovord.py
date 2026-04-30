from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .user import User


@dataclass(slots=True)
class Message:
    id: str
    content: str
    author: User

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Message":
        author_payload = payload.get("author") if isinstance(payload.get("author"), dict) else {}
        return cls(
            id=str(payload.get("id", "")),
            content=str(payload.get("content", "")),
            author=User.from_dict(author_payload),
        )
