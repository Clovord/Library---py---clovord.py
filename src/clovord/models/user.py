from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class User:
    id: str
    username: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "User":
        return cls(
            id=str(payload.get("id", "")),
            username=str(payload.get("username", "")),
        )
