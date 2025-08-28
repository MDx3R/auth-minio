from pydantic import BaseModel


class S3Config(BaseModel):
    endpoint: str
    access_key: str
    secret_key: str
    secure: bool = False  # True for HTTPS
    bucket_name: str
