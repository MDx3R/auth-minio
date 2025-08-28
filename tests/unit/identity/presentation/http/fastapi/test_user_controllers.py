from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from auth.application.interfaces.services.token_service import (
    ITokenIntrospector,
)
from identity.application.dtos.queries.get_user_be_id_query import (
    GetUserByIdQuery,
)
from identity.application.dtos.responses.user_dto import UserDTO
from identity.application.interfaces.usecases.query.get_self_use_case import (
    IGetSelfUseCase,
)
from identity.domain.value_objects.descriptor import UserDescriptor
from identity.presentation.http.fastapi.controllers import query_router


@pytest.mark.asyncio
class TestUserController:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.app = FastAPI()
        self.app.include_router(query_router)
        self.client: TestClient = TestClient(self.app)

        self.get_self_use_case = AsyncMock(spec=IGetSelfUseCase)
        self.token_introspector = AsyncMock(spec=ITokenIntrospector)

        self.app.dependency_overrides[IGetSelfUseCase] = (
            lambda: self.get_self_use_case
        )
        self.app.dependency_overrides[ITokenIntrospector] = (
            lambda: self.token_introspector
        )

    async def test_me_success(self):
        # Arrange
        user_id = uuid4()
        mock_response = UserDTO(user_id, username="testuser")
        self.get_self_use_case.execute.return_value = mock_response
        self.token_introspector.extract_user.return_value = UserDescriptor(
            user_id, mock_response.username
        )

        # Act
        response = self.client.get(
            "/me",
            headers={"Authorization": "Bearer authenticated_token"},  # Token
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "user_id": str(user_id),
            "username": "testuser",
        }
        self.get_self_use_case.execute.assert_awaited_once_with(
            GetUserByIdQuery(user_id)
        )
