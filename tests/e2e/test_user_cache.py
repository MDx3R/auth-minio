import json
from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient

from common.infrastructure.database.redis.redis import RedisDatabase


@pytest.mark.asyncio
class TestUserCache:
    @pytest.fixture(autouse=True)
    def setup(self, client: AsyncClient, redis: RedisDatabase):
        self.client = client
        self.redis = redis
        self.redis_client = redis.get_client()
        self.test_user = {"username": "testuser", "password": "password123"}

    async def register_user(self) -> Any:
        response = await self.client.post(
            "/auth/register", json=self.test_user
        )
        assert response.status_code == status.HTTP_200_OK, response.json()
        response = await self.client.post(
            "/auth/login",
            data={
                "username": self.test_user["username"],
                "password": self.test_user["password"],
            },
        )
        assert response.status_code == status.HTTP_200_OK, response.json()
        return response.json()

    def make_auth_headers(self, token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    async def test_cache_user_descriptor_after_me(self):
        # Arrange
        tokens = await self.register_user()
        user_id = tokens["user_id"]
        headers = self.make_auth_headers(tokens["access_token"])
        cache_key = f"user:{user_id}:descriptor"

        # Act: Make auth/me request to trigger descriptor caching
        response = await self.client.get("/auth/me", headers=headers)
        assert response.status_code == status.HTTP_200_OK, response.json()

        # Assert
        cached_data = await self.redis_client.get(cache_key)
        assert (
            cached_data is not None
        ), f"No cache entry found for key {cache_key}"

        deserialized = json.loads(cached_data)
        assert deserialized["user_id"] == user_id
        assert deserialized["username"] == self.test_user["username"]

    async def test_cache_user_read_model_after_me(self):
        # Arrange
        tokens = await self.register_user()
        user_id = tokens["user_id"]
        headers = self.make_auth_headers(tokens["access_token"])
        cache_key = f"user:{user_id}"

        # Act: Make auth/me request to trigger user read-model caching
        response = await self.client.get("/auth/me", headers=headers)
        assert response.status_code == status.HTTP_200_OK, response.json()

        # Assert
        cached_data = await self.redis_client.get(cache_key)
        assert (
            cached_data is not None
        ), f"No cache entry found for key {cache_key}"

        deserialized = json.loads(cached_data)
        assert deserialized["user_id"] == user_id
        assert deserialized["username"] == self.test_user["username"]
