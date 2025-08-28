import pytest
from minio import Minio  # type: ignore
from testcontainers.minio import MinioContainer  # type: ignore


@pytest.fixture(scope="session")
def minio_container():
    with MinioContainer(
        access_key="minioadmin",
        secret_key="minioadmin",
        image="minio/minio:latest",
    ) as minio:
        minio.with_command("server /data --console-address ':9001'")
        yield minio


@pytest.fixture(scope="session")
def minio(minio_container: MinioContainer):
    host = minio_container.get_container_host_ip()
    port = minio_container.get_exposed_port("9000")
    client = Minio(
        endpoint=f"{host}:{port}",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False,
    )
    return client
