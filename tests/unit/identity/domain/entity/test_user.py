from uuid import uuid4

import pytest

from identity.domain.entity.user import User


class TestUserFactory:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user = User(uuid4(), "testuser", "hash")

    def test_descriptor(self):
        desc = self.user.descriptor()
        assert desc.user_id == self.user.user_id
        assert desc.username == self.user.username
