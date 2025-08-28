from collections.abc import Sequence

from photos.domain.interfaces.extenstion_policy import IExtensionPolicy


class ExtensionWhitelistPolicy(IExtensionPolicy):
    def __init__(self, allowed: Sequence[str]) -> None:
        self._allowed = {ext.lower() for ext in allowed}

    def is_allowed(self, extension: str) -> bool:
        return extension.lower() in self._allowed
