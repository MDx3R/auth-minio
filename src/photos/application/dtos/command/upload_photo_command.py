from dataclasses import dataclass
from typing import BinaryIO


@dataclass(frozen=True)
class UploadPhotoCommand:
    content: BinaryIO
