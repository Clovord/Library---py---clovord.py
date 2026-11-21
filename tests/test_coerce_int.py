from clovord.models._helpers import coerce_int, optional_int
from clovord.ui.components import Container, TextDisplay, _coerce_int


def test_optional_int_accepts_hex_and_hash():
    assert optional_int("0x0050FF") == 0x0050FF
    assert optional_int("#0050FF") == 0x0050FF
    assert optional_int(0x0050FF) == 0x0050FF
    assert optional_int("20735") == 20735
    assert optional_int(None) is None
    assert optional_int("nope") is None


def test_coerce_int_raises_on_invalid():
    try:
        coerce_int("nope")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")


def test_ui_coerce_int_hex():
    assert _coerce_int("0x0050FF") == 0x0050FF
    assert _coerce_int("#0050FF") == 0x0050FF


def test_container_accent_color_hex_string():
    payload = Container(TextDisplay("hi"), accent_color="0x0050FF").to_dict()
    assert payload["accent_color"] == 0x0050FF
    payload_hash = Container(TextDisplay("hi"), accent_color="#0050FF").to_dict()
    assert payload_hash["accent_color"] == 0x0050FF
