from pydantic import BaseModel


class RedisConfig(BaseModel):
    host: str
    port: int
    db: int = 0
    password: str | None = None

    @property
    def redis_url(self) -> str:
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"
