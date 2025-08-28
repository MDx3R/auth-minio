from unittest.mock import Mock
from uuid import uuid4

import pytest

from common.domain.exceptions import InvariantViolationError
from common.domain.uuid_generator import IUUIDGenerator
from identity.domain.entity.user import User
from identity.domain.factories.user_factory import UserFactory


class TestUserFactory:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_id = uuid4()

        self.uuid_generator = Mock(spec=IUUIDGenerator)
        self.uuid_generator.create.return_value = self.user_id

        self.factory = UserFactory(self.uuid_generator)

    def test_create_success(self):
        result = self.factory.create("testuser", "hash")
        assert result == User(self.user_id, "testuser", "hash")

    def test_create_no_name_no_pass_fails(self):
        with pytest.raises(InvariantViolationError):
            self.factory.create("", "hash")
        with pytest.raises(InvariantViolationError):
            self.factory.create("testuser", "")
        with pytest.raises(InvariantViolationError):
            self.factory.create("", "")
