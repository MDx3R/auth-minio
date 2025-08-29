from pydantic import BaseModel


class DatabaseConfig(BaseModel):
    db_name: str | None = None
    db_user: str | None = None
    db_pass: str | None = None
    db_host: str | None = None
    db_port: int | None = None

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_pass}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
