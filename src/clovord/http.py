from __future__ import annotations

from typing import Any

import aiohttp

from .errors import ClovordHTTPError, ClovordInvalidTokenError


class HTTPClient:
    """Minimal async REST client for Clovord API."""

    BASE_URL = "https://clovord.com/api/v1"

    def __init__(self) -> None:
        self._session: aiohttp.ClientSession | None = None
        self._token: str | None = None

    async def start(self, token: str) -> None:
        self._token = token
        if self._session is None or self._session.closed:
            headers = {
                "Authorization": f"Bot {token}",
                "Content-Type": "application/json",
            }
            self._session = aiohttp.ClientSession(headers=headers)

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()

    async def get(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return await self._request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return await self._request("POST", path, **kwargs)

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        if self._session is None or self._session.closed:
            raise ClovordHTTPError("HTTP client is not started")

        normalized_path = path if path.startswith("/") else f"/{path}"
        url = f"{self.BASE_URL}{normalized_path}"

        try:
            async with self._session.request(method, url, **kwargs) as response:
                if response.status in {401, 403}:
                    text = await response.text()
                    raise ClovordInvalidTokenError(f"Authentication failed: {text or response.reason}")

                if response.status >= 400:
                    text = await response.text()
                    raise ClovordHTTPError(f"{response.status} {response.reason}: {text}")

                if response.content_type == "application/json":
                    return await response.json()

                text = await response.text()
                return {"raw": text}
        except aiohttp.ClientError as exc:
            raise ClovordHTTPError(str(exc)) from exc
