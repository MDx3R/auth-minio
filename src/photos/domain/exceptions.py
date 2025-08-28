from common.domain.exceptions import DomainError


class InvalidExtensionTypeError(DomainError):
    def __init__(self, ext: str) -> None:
        super().__init__(f"Invalid file extension type: {ext}")
