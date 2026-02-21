from __future__ import annotations

import httpx


class BalatroError(Exception):
    """Error returned by the BalatroBot JSON-RPC API."""

    def __init__(self, code: int, message: str, data: dict | None = None):
        self.code = code
        self.message = message
        self.data = data or {}
        super().__init__(f"[{code}] {message}")


class BalatroClient:
    """Async JSON-RPC 2.0 client for BalatroBot."""

    def __init__(self, host: str = "127.0.0.1", port: int = 12346):
        self._url = f"http://{host}:{port}"
        self._client = httpx.AsyncClient(timeout=30.0)
        self._id = 0

    async def call(self, method: str, params: dict | None = None) -> dict:
        self._id += 1
        payload: dict = {"jsonrpc": "2.0", "method": method, "id": self._id}
        if params:
            payload["params"] = params
        resp = await self._client.post(self._url, json=payload)
        data = resp.json()
        if "error" in data:
            err = data["error"]
            raise BalatroError(err["code"], err["message"], err.get("data"))
        return data["result"]

    async def close(self):
        await self._client.aclose()
