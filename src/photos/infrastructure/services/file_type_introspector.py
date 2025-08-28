from typing import BinaryIO

import filetype  # pyright: ignore[reportMissingTypeStubs]
from filetype.types import Type  # pyright: ignore[reportMissingTypeStubs]

from photos.application.dtos.dtos import FileType
from photos.application.exceptions import InvalidFileTypeError
from photos.application.interfaces.services.file_type_introspector import (
    IFileTypeIntrospector,
)


class FileTypeIntrospector(IFileTypeIntrospector):
    def extract(self, data: BinaryIO) -> FileType:
        head = data.read(261)
        data.seek(0)
        kind: Type | None = filetype.guess(head)  # type: ignore
        if kind is None:
            raise InvalidFileTypeError

        return FileType(extension=kind.extension, mime=kind.mime)  # type: ignore
