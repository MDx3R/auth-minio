import pytest

from photos.domain.policies.extenstion_policy import ExtensionWhitelistPolicy


class TestExtensionPolicy:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.ext = ["ext", "ext2", "ext3"]
        self.ext_policy = ExtensionWhitelistPolicy(self.ext)

    def test_is_allowed_true(self):
        for i in self.ext:
            assert self.ext_policy.is_allowed(i) is True

    def test_is_allowed_false(self):
        assert self.ext_policy.is_allowed("some-ext") is False
