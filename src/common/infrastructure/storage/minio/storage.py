from typing import Self

from minio import Minio  # type: ignore

from common.infrastructure.config.s3_config import S3Config


class MinioStorage:
    def __init__(self, client: Minio, bucket_name: str):
        self._client = client
        self._bucket_name = bucket_name

    @classmethod
    def create(cls, config: S3Config) -> Self:
        client = cls.create_client(config)
        return cls(client=client, bucket_name=config.bucket_name)

    @staticmethod
    def create_client(config: S3Config) -> Minio:
        return Minio(
            endpoint=config.endpoint,
            access_key=config.access_key,
            secret_key=config.secret_key,
            secure=config.secure,
        )

    def get_client(self) -> Minio:
        return self._client

    def get_bucket_name(self) -> str:
        return self._bucket_name

    def ensure_bucket(self) -> None:
        if not self._client.bucket_exists(self._bucket_name):
            self._client.make_bucket(self._bucket_name)

    def shutdown(self) -> None:
        """MinIO does not maintain a persistent connection"""
        pass
