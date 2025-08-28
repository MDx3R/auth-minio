from pydantic import BaseModel

from common.infrastructure.config.auth_config import AuthConfig
from common.infrastructure.config.database_config import DatabaseConfig
from common.infrastructure.config.s3_config import S3Config


class AppConfig(BaseModel):
    auth: AuthConfig
    db: DatabaseConfig
    s3: S3Config
