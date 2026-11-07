from __future__ import annotations

import json
import os
import socket
import struct
import tempfile
from typing import Any, BinaryIO


class RichPresenceError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


def encode_frame(payload: dict[str, Any]) -> bytes:
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    if len(body) > 65536:
        raise RichPresenceError("CLOVORD_RICH_PRESENCE_FRAME", "activity frame is too large")
    return struct.pack("<I", len(body)) + body


def decode_frame(buffer: bytes) -> tuple[dict[str, Any] | None, bytes]:
    if len(buffer) < 4:
        return None, buffer
    length = struct.unpack("<I", buffer[:4])[0]
    if length < 1 or length > 65536:
        raise RichPresenceError("CLOVORD_RICH_PRESENCE_FRAME", "desktop app sent an invalid frame")
    if len(buffer) < 4 + length:
        return None, buffer
    raw = buffer[4 : 4 + length]
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise RichPresenceError("CLOVORD_RICH_PRESENCE_FRAME", "desktop app sent invalid JSON") from exc
    if not isinstance(payload, dict):
        raise RichPresenceError("CLOVORD_RICH_PRESENCE_FRAME", "desktop app sent an invalid frame")
    return payload, buffer[4 + length :]


class _Transport:
    def __init__(self, stream: BinaryIO | socket.socket) -> None:
        self._stream = stream
        self._pending = b""

    def write(self, payload: dict[str, Any]) -> None:
        data = encode_frame(payload)
        stream = self._stream
        if isinstance(stream, socket.socket):
            stream.sendall(data)
            return
        stream.write(data)
        stream.flush()

    def read(self) -> dict[str, Any]:
        while True:
            payload, self._pending = decode_frame(self._pending)
            if payload is not None:
                return payload
            chunk = self._read_some()
            if not chunk:
                raise RichPresenceError("CLOVORD_RICH_PRESENCE_CLOSED", "desktop app closed the connection")
            self._pending += chunk

    def close(self) -> None:
        try:
            self._stream.close()
        except OSError:
            return

    def _read_some(self) -> bytes:
        stream = self._stream
        if isinstance(stream, socket.socket):
            return stream.recv(65536)
        return stream.read(65536)


def _open_ipc(index: int) -> _Transport:
    if os.name == "nt":
        path = "\\\\.\\pipe\\clovord-ipc-" + str(index)
        stream = open(path, "r+b", buffering=0)
        return _Transport(stream)
    path = os.path.join(tempfile.gettempdir(), "clovord-ipc-" + str(index) + ".sock")
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect(path)
    return _Transport(sock)


class RichPresence:
    def __init__(self, client_id: str) -> None:
        text = str(client_id or "").strip()
        if not text.isdigit() or not 1 <= len(text) <= 32:
            raise RichPresenceError("CLOVORD_RICH_PRESENCE_CLIENT", "client_id must be an application id")
        self.client_id = text
        self._transport: _Transport | None = None

    def connect(self) -> None:
        if self._transport is not None:
            return
        last: OSError | None = None
        for index in range(10):
            try:
                transport = _open_ipc(index)
            except OSError as exc:
                last = exc
                continue
            self._transport = transport
            try:
                self._write({"op": "handshake", "client_id": self.client_id})
                ready = self._read()
            except Exception:
                self.close()
                raise
            if ready.get("op") != "ready":
                self.close()
                raise RichPresenceError("CLOVORD_RICH_PRESENCE_HANDSHAKE", "desktop app rejected the handshake")
            return
        raise RichPresenceError(
            "CLOVORD_RICH_PRESENCE_OFFLINE",
            "Clovord desktop app is not running",
        ) from last

    def set_activity(self, activity: dict[str, Any]) -> None:
        if not isinstance(activity, dict):
            raise RichPresenceError("CLOVORD_RICH_PRESENCE_ACTIVITY", "activity must be an object")
        name = activity.get("name")
        if not isinstance(name, str) or not name.strip():
            raise RichPresenceError("CLOVORD_RICH_PRESENCE_ACTIVITY", "activity name is required")
        self.connect()
        self._write({"op": "set_activity", "activity": activity})
        reply = self._read()
        if reply.get("op") == "error":
            raise RichPresenceError("CLOVORD_RICH_PRESENCE_ACTIVITY", str(reply.get("message") or "rejected"))
        if reply.get("op") != "ack":
            raise RichPresenceError("CLOVORD_RICH_PRESENCE_ACTIVITY", "desktop app did not accept the activity")

    def clear(self) -> None:
        if self._transport is None:
            return
        self._write({"op": "clear_activity"})

    def close(self) -> None:
        transport = self._transport
        self._transport = None
        if transport is not None:
            transport.close()

    def __enter__(self) -> "RichPresence":
        self.connect()
        return self

    def __exit__(self, *_exc: object) -> None:
        try:
            self.clear()
        finally:
            self.close()

    def _write(self, payload: dict[str, Any]) -> None:
        if self._transport is None:
            raise RichPresenceError("CLOVORD_RICH_PRESENCE_OFFLINE", "not connected")
        self._transport.write(payload)

    def _read(self) -> dict[str, Any]:
        if self._transport is None:
            raise RichPresenceError("CLOVORD_RICH_PRESENCE_OFFLINE", "not connected")
        return self._transport.read()
