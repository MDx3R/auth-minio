from pydantic import BaseModel, field_validator


class RedisConfig(BaseModel):
    host: str
    port: int
    db: int = 0
    password: str | None = None

    @field_validator("password", mode="after")
    @classmethod
    def password_to_none(cls, v: str | None):
        if not v:
            return None
        return v
