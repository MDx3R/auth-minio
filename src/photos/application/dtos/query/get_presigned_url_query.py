from dataclasses import dataclass


@dataclass(frozen=True)
class GetPresignedUrlQuery:
    name: str
