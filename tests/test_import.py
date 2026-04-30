from __future__ import annotations


def test_import_bot() -> None:
    from clovord import Bot

    assert Bot is not None
