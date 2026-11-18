from __future__ import annotations

import pytest

from clovord.commands import CommandTree, Interaction, InteractionResponse


class _RecordingHTTP:
    def __init__(self) -> None:
        self.posts: list[tuple[str, dict]] = []

    async def post(self, path: str, *, json: dict | None = None, **kwargs):
        self.posts.append((path, dict(json or {})))
        return {"ok": True}

    async def patch(self, path: str, *, json: dict | None = None, **kwargs):
        self.posts.append((path, dict(json or {})))
        return {"id": "msg-1", "content": (json or {}).get("content", "")}


@pytest.mark.asyncio
async def test_command_dispatch_defers_before_handler() -> None:
    http = _RecordingHTTP()
    bot = type("Bot", (), {"_logger": None, "http": http})()
    tree = CommandTree(bot)
    order: list[str] = []

    @tree.command(name="dashboard", description="Responds with dashboard link")
    async def dashboard(interaction: Interaction):
        order.append("handler")
        # Simulates slow work that used to run before defer and hit 400097.
        await interaction.response.send_message("https://example.test/dashboard")

    handled = await tree.dispatch(
        {
            "type": 2,
            "id": "ixn-1",
            "token": "tok",
            "application_id": "app",
            "data": {"name": "dashboard"},
        }
    )

    assert handled is True
    assert order == ["handler"]
    assert http.posts[0] == (
        "/interactions/ixn-1/tok/callback",
        {"type": 5},
    )
    assert http.posts[1][0] == "/interactions/ixn-1/tok/messages/@original"
    assert http.posts[1][1]["content"] == "https://example.test/dashboard"


@pytest.mark.asyncio
async def test_defer_is_idempotent_after_auto_defer() -> None:
    http = _RecordingHTTP()
    bot = type("Bot", (), {"http": http})()
    interaction = Interaction(
        bot,
        {"id": "ixn-2", "token": "tok", "type": 2, "application_id": "app", "data": {}},
    )
    response = InteractionResponse(interaction)

    await response.defer()
    await response.defer()

    assert interaction._deferred is True
    assert len(http.posts) == 1
    assert http.posts[0][1]["type"] == 5
