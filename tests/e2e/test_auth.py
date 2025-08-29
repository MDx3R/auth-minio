from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuth:
    @pytest.fixture(autouse=True)
    def setup(self, client: AsyncClient):
        self.test_user = {"username": "testuser", "password": "password123"}
        self.client = client

    async def register_user(
        self, user_data: dict[str, str] | None = None
    ) -> Any:
        user_data = user_data or self.test_user

        response = await self.client.post("/auth/register", json=user_data)
        assert response.status_code == status.HTTP_200_OK, response.json()
        response = await self.client.post(
            "/auth/login",
            data={
                "username": user_data["username"],
                "password": user_data["password"],
            },
        )
        assert response.status_code == status.HTTP_200_OK, response.json()
        return response.json()

    def make_auth_headers(self, token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    async def test_register(self):
        # Act
        response = await self.client.post(
            "/auth/register", json=self.test_user
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK, response.json()
        data = response.json()
        assert "id" in data

    async def test_login_user(self):
        # Arrange
        await self.register_user()

        # Act
        response = await self.client.post(
            "/auth/login",
            data={
                "username": self.test_user["username"],
                "password": self.test_user["password"],
            },
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK, response.json()
        data = response.json()
        assert "user_id" in data
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_logout_user(self):
        # Arrange
        tokens = await self.register_user()
        headers = self.make_auth_headers(tokens["refresh_token"])

        # Act
        response = await self.client.post("/auth/logout", headers=headers)

        # Assert
        assert (
            response.status_code == status.HTTP_204_NO_CONTENT
        ), response.json()

    async def test_refresh_token(self):
        # Arrange
        tokens = await self.register_user()
        headers = self.make_auth_headers(tokens["refresh_token"])

        # Act
        response = await self.client.post("/auth/refresh", headers=headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK, response.json()
        data = response.json()
        assert "user_id" in data
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_me(self):
        # Arrange
        tokens = await self.register_user()
        headers = self.make_auth_headers(tokens["access_token"])

        # Act
        response = await self.client.get("/auth/me", headers=headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK, response.json()
        data = response.json()
        assert data["user_id"] == tokens["user_id"]
        assert data["username"] == self.test_user["username"]

    async def test_subsequent_logout(self):
        # Arrange
        tokens = await self.register_user()
        headers = self.make_auth_headers(tokens["refresh_token"])

        # First logout
        await self.client.post("/auth/logout", headers=headers)

        # Act
        response = await self.client.post("/auth/logout", headers=headers)

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_subsequent_refresh_fails(self):
        # Arrange
        tokens = await self.register_user()
        headers = self.make_auth_headers(tokens["refresh_token"])

        # First logout
        await self.client.post("/auth/refresh", headers=headers)

        # Act
        response = await self.client.post("/auth/refresh", headers=headers)

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_login_register_not_allowed_with_token(self):
        # Arrange
        tokens = await self.register_user()
        headers = self.make_auth_headers(tokens["access_token"])

        # Act
        response = await self.client.post(
            "/auth/register", json=self.test_user, headers=headers
        )
        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Act
        response = await self.client.post(
            "/auth/login",
            data={
                "username": self.test_user["username"],
                "password": self.test_user["password"],
            },
            headers=headers,
        )
        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_logout_not_allowed_without_token(self):
        # Act
        response = await self.client.post("/auth/logout")

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_refresh_not_allowed_without_token(self):
        # Act
        response = await self.client.post("/auth/refresh")

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
