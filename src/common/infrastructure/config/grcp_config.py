from pydantic import BaseModel


class GRPCConfig(BaseModel):
    host: str
    port: int
    grace: int = 1

    @property
    def address(self) -> str:
        return f"{self.host}:{self.port}"
