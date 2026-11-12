from __future__ import annotations

import pytest

from clovord.bot import Bot
from clovord.gateway.events.message_create import handle as message_create_handle
from clovord.models.message import Message
from clovord.models.user import User
from clovord.prefix_commands import match_prefix, normalize_prefixes, parse_invocation


def test_normalize_prefixes_longest_first() -> None:
    assert normalize_prefixes(None) == ()
    assert normalize_prefixes("!") == ("!",)
    assert normalize_prefixes(["!", "!!", "?"]) == ("!!", "!", "?")


def test_match_prefix_and_parse_invocation() -> None:
    prefixes = normalize_prefixes(["!", "!!"])
    assert match_prefix("!!help now", prefixes) == "!!"
    assert match_prefix("!help", prefixes) == "!"
    assert match_prefix("hello", prefixes) is None
    assert parse_invocation("!help one two", "!") == ("help", ["one", "two"])
    assert parse_invocation("!", "!") is None


@pytest.mark.asyncio
async def test_process_commands_invokes_handler_with_args() -> None:
    bot = Bot(command_prefix="!")
    bot._user = User.from_dict({"id": "bot", "username": "Bot"})
    seen: dict[str, object] = {}

    @bot.command(name="help", aliases=("h",))
    async def help_command(ctx):
        seen["invoked_with"] = ctx.invoked_with
        seen["args"] = list(ctx.args)
        seen["prefix"] = ctx.prefix
        seen["author"] = ctx.author.id

    message = Message.from_dict(
        {
            "id": "1",
            "content": "!h alpha beta",
            "author": {"id": "user", "username": "User"},
            "channel_id": "10",
        },
        bot=bot,
    )
    assert await bot.process_commands(message) is True
    assert seen == {
        "invoked_with": "h",
        "args": ["alpha", "beta"],
        "prefix": "!",
        "author": "user",
    }


@pytest.mark.asyncio
async def test_process_commands_ignores_self_and_unknown() -> None:
    bot = Bot(command_prefix="!")
    bot._user = User.from_dict({"id": "bot", "username": "Bot"})
    called = False

    @bot.command()
    async def ping(ctx):
        nonlocal called
        called = True

    self_message = Message.from_dict(
        {
            "id": "1",
            "content": "!ping",
            "author": {"id": "bot", "username": "Bot"},
            "channel_id": "10",
        },
        bot=bot,
    )
    assert await bot.process_commands(self_message) is False
    assert called is False

    unknown = Message.from_dict(
        {
            "id": "2",
            "content": "!unknown",
            "author": {"id": "user", "username": "User"},
            "channel_id": "10",
        },
        bot=bot,
    )
    assert await bot.process_commands(unknown) is False


@pytest.mark.asyncio
async def test_message_create_runs_prefix_before_event() -> None:
    bot = Bot(command_prefix="!")
    bot._user = User.from_dict({"id": "bot", "username": "Bot"})
    order: list[str] = []

    @bot.command()
    async def ping(ctx):
        order.append("command")

    @bot.event
    async def on_message_create(message):
        order.append("event")

    await message_create_handle(
        bot,
        data_part={
            "id": "1",
            "content": "!ping",
            "author": {"id": "user", "username": "User"},
            "channel_id": "10",
        },
    )
    assert order == ["command", "event"]
