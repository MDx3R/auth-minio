from datetime import timedelta

from pydantic import BaseModel


class AuthConfig(BaseModel):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ISSUER: str
    ACCESS_TOKEN_TTL: timedelta = timedelta(minutes=15)
    REFRESH_TOKEN_TTL: timedelta = timedelta(days=7)
