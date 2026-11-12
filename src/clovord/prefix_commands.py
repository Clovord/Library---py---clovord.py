from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Sequence

if TYPE_CHECKING:
    from .bot import Bot
    from .models.message import Message
    from .models.user import User
    from .models.channel import Channel


PrefixCommandCallback = Callable[..., Awaitable[Any]]


def normalize_prefixes(command_prefix: str | Sequence[str] | None) -> tuple[str, ...]:
    if command_prefix is None:
        return ()
    if isinstance(command_prefix, str):
        value = command_prefix
        return (value,) if value else ()
    prefixes = [str(item) for item in command_prefix if str(item)]
    return tuple(sorted(prefixes, key=len, reverse=True))


class PrefixCommand:
    def __init__(
        self,
        callback: PrefixCommandCallback,
        *,
        name: str,
        aliases: Sequence[str] = (),
    ) -> None:
        if not inspect.iscoroutinefunction(callback):
            raise TypeError("Prefix command callback must be an async function")
        self.callback = callback
        self.name = str(name).lower()
        self.aliases = tuple(str(alias).lower() for alias in aliases if str(alias).strip())

    @property
    def names(self) -> tuple[str, ...]:
        return (self.name, *self.aliases)


class Context:
    def __init__(
        self,
        *,
        bot: Bot,
        message: Message,
        prefix: str,
        command: PrefixCommand,
        invoked_with: str,
        args: list[str],
    ) -> None:
        self.bot = bot
        self.message = message
        self.prefix = prefix
        self.command = command
        self.invoked_with = invoked_with
        self.args = args

    @property
    def channel(self) -> Channel:
        return self.message.channel

    @property
    def author(self) -> User:
        return self.message.author

    async def send(self, content: str = "", **kwargs: Any) -> Any:
        return await self.message.channel.send(content, **kwargs)


class PrefixCommandMap:
    def __init__(self) -> None:
        self._commands: dict[str, PrefixCommand] = {}

    def add(self, command: PrefixCommand) -> PrefixCommand:
        for name in command.names:
            existing = self._commands.get(name)
            if existing is not None and existing is not command:
                raise ValueError(f"Prefix command name already registered: {name}")
            self._commands[name] = command
        return command

    def get(self, name: str) -> PrefixCommand | None:
        return self._commands.get(str(name).lower())

    def clear(self) -> None:
        self._commands.clear()

    @property
    def commands(self) -> tuple[PrefixCommand, ...]:
        seen: dict[int, PrefixCommand] = {}
        for command in self._commands.values():
            seen[id(command)] = command
        return tuple(seen.values())


def match_prefix(content: str, prefixes: Sequence[str]) -> str | None:
    for prefix in prefixes:
        if content.startswith(prefix):
            return prefix
    return None


def parse_invocation(content: str, prefix: str) -> tuple[str, list[str]] | None:
    rest = content[len(prefix) :].lstrip()
    if not rest:
        return None
    parts = rest.split()
    if not parts:
        return None
    return parts[0], parts[1:]
