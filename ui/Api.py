import httpx

class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def _post(self, path: str, payload: dict, timeout: float):
        async with httpx.AsyncClient() as client:
            return await client.post(f"{self.base_url}{path}", json=payload)

    async def login(self, username: str, password: str):
        return await self._post("/login", {"username": username, "password": password})

    async def aisql(self, username: str, password: str, question: str):
        return await self._post("/aisql", {"username": username, "password": password, "question": question})

    async def add_user(self, payload: dict):
        return await self._post("/add_user", payload)

    async def delete_user(self, payload: dict):
        return await self._post("/delete_user", payload)

    async def database(self, payload: dict):
        return await self._post("/database", payload)
