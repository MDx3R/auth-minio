from pydantic import BaseModel


class S3Config(BaseModel):
    ENDPOINT: str
    ACCESS_KEY: str
    SECRET_KEY: str
    SECURE: bool = False  # True for HTTPS
    BUCKET_NAME: str
