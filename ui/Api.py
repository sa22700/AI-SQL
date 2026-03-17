# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import httpx

class ApiClient:
    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def _post(self, path: str, payload: dict, timeout: float | None = None) -> httpx.Response:
        t = self.timeout if timeout is None else timeout
        async with httpx.AsyncClient(timeout=t) as client:
            return await client.post(f"{self.base_url}{path}", json=payload)

    async def _put(self, path: str, payload: dict, timeout: float | None = None) -> httpx.Response:
        t = self.timeout if timeout is None else timeout
        async with httpx.AsyncClient(timeout=t) as client:
            return await client.put(f"{self.base_url}{path}", json=payload)

    async def login(self, username: str, password: str) -> httpx.Response:
        return await self._post("/login", {"username": username, "password": password})

    async def aisql(self, username: str, password: str, question: str) -> httpx.Response:
        return await self._post("/aisql", {"username": username, "password": password, "question": question})

    async def add_user(self, payload: dict) -> httpx.Response:
        return await self._post("/add_user", payload)

    async def delete_user(self, payload: dict) -> httpx.Response:
        return await self._post("/delete_user", payload)

    async def database(self, payload: dict) -> httpx.Response:
        return await self._post("/database", payload)

    async def delete_part(self, payload: dict) -> httpx.Response:
        return await self._post("/delete_part", payload)

    async def update_part(self, payload: dict) -> httpx.Response:
        return await self._put("/update_part", payload)

    async def delete_table(self, payload: dict) -> httpx.Response:
        return await self._post("/delete_table", payload)