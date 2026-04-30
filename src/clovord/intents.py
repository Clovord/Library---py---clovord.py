from __future__ import annotations


class Intents:
    """Gateway intent bitmask helper.

    Example:
        intents = Intents.default()
        intents.members = True
    """

    __slots__ = ("_value",)

    PRESENCE = 1 << 1
    GUILD_MEMBERS = 1 << 3
    MESSAGE_CONTENT = 1 << 5
    REFERRALS = 1 << 7
    DOMAINLIST = 1 << 9

    _ALL_MASK = PRESENCE | GUILD_MEMBERS | MESSAGE_CONTENT | REFERRALS | DOMAINLIST

    _GATEWAY_INTENTS = {
        PRESENCE: "INTENT_PRESENCE",
        GUILD_MEMBERS: "INTENT_GUILD_MEMBERS",
        MESSAGE_CONTENT: "INTENT_MESSAGE_CONTENT",
        REFERRALS: "INTENT_REFERRALS",
        DOMAINLIST: "INTENT_DOMAINLIST",
    }

    def __init__(self, value: int = 0) -> None:
        self._value = 0
        self.value = value

    @classmethod
    def none(cls) -> "Intents":
        return cls(0)

    @classmethod
    def default(cls) -> "Intents":
        # Default should stay conservative; users opt-in by enabling flags.
        return cls.none()

    @classmethod
    def all(cls) -> "Intents":
        return cls(cls._ALL_MASK)

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("intents value must be an integer")
        if value < 0:
            raise ValueError("intents value must be >= 0")
        self._value = value

    def _get_flag(self, flag: int) -> bool:
        return bool(self._value & flag)

    def _set_flag(self, flag: int, enabled: bool) -> None:
        if not isinstance(enabled, bool):
            raise TypeError("intent flags must be set to bool")
        if enabled:
            self._value |= flag
        else:
            self._value &= ~flag

    @property
    def guilds(self) -> bool:
        return self._get_flag(self.GUILD_MEMBERS)

    @guilds.setter
    def guilds(self, enabled: bool) -> None:
        self._set_flag(self.GUILD_MEMBERS, enabled)

    @property
    def members(self) -> bool:
        return self._get_flag(self.GUILD_MEMBERS)

    @members.setter
    def members(self, enabled: bool) -> None:
        self._set_flag(self.GUILD_MEMBERS, enabled)

    @property
    def messages(self) -> bool:
        return self._get_flag(self.MESSAGE_CONTENT)

    @messages.setter
    def messages(self, enabled: bool) -> None:
        self._set_flag(self.MESSAGE_CONTENT, enabled)

    @property
    def message_content(self) -> bool:
        return self._get_flag(self.MESSAGE_CONTENT)

    @message_content.setter
    def message_content(self, enabled: bool) -> None:
        self._set_flag(self.MESSAGE_CONTENT, enabled)

    @property
    def presence(self) -> bool:
        return self._get_flag(self.PRESENCE)

    @presence.setter
    def presence(self, enabled: bool) -> None:
        self._set_flag(self.PRESENCE, enabled)

    @property
    def referrals(self) -> bool:
        return self._get_flag(self.REFERRALS)

    @referrals.setter
    def referrals(self, enabled: bool) -> None:
        self._set_flag(self.REFERRALS, enabled)

    @property
    def domainlist(self) -> bool:
        return self._get_flag(self.DOMAINLIST)

    @domainlist.setter
    def domainlist(self, enabled: bool) -> None:
        self._set_flag(self.DOMAINLIST, enabled)

    def to_gateway_list(self) -> list[str]:
        intents: list[str] = []
        for bit, name in self._GATEWAY_INTENTS.items():
            if self._value & bit:
                intents.append(name)
        return intents

    def __int__(self) -> int:
        return self._value

    def __repr__(self) -> str:
        return f"Intents(value={self._value})"
