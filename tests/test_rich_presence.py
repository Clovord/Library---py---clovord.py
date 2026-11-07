from __future__ import annotations

import pytest

from clovord.rich_presence import RichPresence, RichPresenceError, decode_frame, encode_frame


def test_frame_round_trip() -> None:
    encoded = encode_frame({"op": "handshake", "client_id": "42"})
    payload, rest = decode_frame(encoded)
    assert rest == b""
    assert payload == {"op": "handshake", "client_id": "42"}


def test_frame_waits_for_body() -> None:
    encoded = encode_frame({"op": "ack"})
    partial, rest = decode_frame(encoded[:3])
    assert partial is None
    assert rest == encoded[:3]


def test_client_id_must_be_an_application_id() -> None:
    with pytest.raises(RichPresenceError):
        RichPresence("app")


def test_activity_requires_a_name() -> None:
    presence = RichPresence("123")
    with pytest.raises(RichPresenceError):
        presence.set_activity({"type": 0})
