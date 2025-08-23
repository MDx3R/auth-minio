import math
import re

import pytest

from common.infrastructure.services.secrets_token_generator import (
    SecretsTokenGenerator,
)


class TestSecretsTokenGenerator:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.gen = SecretsTokenGenerator()

    @pytest.mark.parametrize("length", [0, 1, 16, 64])
    def test_hex_length_and_type(self, length: int):
        token = self.gen.hex(length)
        assert isinstance(token, str)
        assert len(token) == length  # length is exactly
        assert re.fullmatch(r"[0-9a-f]*", token)

    @pytest.mark.parametrize("length", [0, 1, 6, 20])
    def test_numeric_length_and_digits(self, length: int):
        token = self.gen.numeric(length)
        assert isinstance(token, str)
        assert len(token) == length
        assert re.fullmatch(r"[0-9]*", token)

    @pytest.mark.parametrize("length", [0, 1, 16, 64])
    def test_urlsafe_length_and_type(self, length: int):
        token = self.gen.urlsafe(length)
        assert isinstance(token, str)
        assert len(token) >= length  # length may be different
        assert all(c.isalnum() or c in "-_" for c in token)

    @pytest.mark.parametrize("length", [0, 1, 16, 64])
    def test_secure_length_and_type(self, length: int):
        token = self.gen.secure(length)
        assert isinstance(token, str)
        assert len(token) >= length  # length may be different
        assert all(c.isalnum() or c in "-_" for c in token)

    @pytest.mark.parametrize("length", [-1, -10, -100, -math.inf])
    def test_tokens_length_validation(self, length: int):
        with pytest.raises(ValueError):
            self.gen.hex(length)
        with pytest.raises(ValueError):
            self.gen.numeric(length)
        with pytest.raises(ValueError):
            self.gen.urlsafe(length)
        with pytest.raises(ValueError):
            self.gen.secure(length)

    def test_tokens_unique(self):
        hex1 = self.gen.hex(16)
        hex2 = self.gen.hex(16)
        numeric1 = self.gen.numeric(6)
        numeric2 = self.gen.numeric(6)
        urlsafe1 = self.gen.urlsafe(16)
        urlsafe2 = self.gen.urlsafe(16)

        assert hex1 != hex2
        assert numeric1 != numeric2
        assert urlsafe1 != urlsafe2
