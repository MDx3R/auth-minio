import pytest

from auth.infrastructure.services.bcrypt.password_hasher import (
    BcryptPasswordHasher,
)


class TestBcryptPasswordHasher:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.hasher = BcryptPasswordHasher()

    def test_hash_and_verify_success(self):
        password = "s3cret!"
        hashed = self.hasher.hash(password)

        assert isinstance(hashed, str)
        assert self.hasher.verify(password, hashed)

    def test_verify_wrong_password(self):
        password = "s3cret!"
        hashed = self.hasher.hash(password)

        assert not self.hasher.verify("wrong", hashed)

    def test_hash_is_different_each_time(self):
        password = "s3cret!"
        hash1 = self.hasher.hash(password)
        hash2 = self.hasher.hash(password)
        assert hash1 != hash2
