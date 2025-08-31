import os
from argparse import ArgumentParser
from enum import Enum
from pathlib import Path
from typing import Any, Self

import yaml
from dotenv import load_dotenv
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from common.infrastructure.config.auth_config import AuthConfig
from common.infrastructure.config.database_config import DatabaseConfig
from common.infrastructure.config.grcp_config import GRPCConfig
from common.infrastructure.config.logger_config import LoggerConfig
from common.infrastructure.config.redis_config import RedisConfig
from common.infrastructure.config.s3_config import S3Config


class RunEnvironment(str, Enum):
    LOCAL = "local"
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"
    TEST = "test"


class MergeSettingsSource(PydanticBaseSettingsSource):
    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> tuple[Any, str, bool]:
        # Nothing to do here. Only implement the return statement to make mypy happy
        return None, "", False

    def __call__(self) -> dict[str, Any]:
        return ConfigLoader().load()


class AppConfig(BaseSettings):
    env: RunEnvironment
    auth: AuthConfig
    db: DatabaseConfig
    s3: S3Config
    redis: RedisConfig
    grpc: GRPCConfig
    logger: LoggerConfig

    def masked_dict(self) -> dict[str, Any]:
        return self.model_dump(
            mode="json",
            exclude={
                "db": {"db_password"},
                "auth": {"secret_key", "algorithm"},
                "redis": {"password"},
            },
        )

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    @classmethod
    def load(cls) -> Self:
        return cls()  # pyright: ignore[reportCallIssue]

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # init > env > yaml > dotenv > secrets
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            MergeSettingsSource(settings_cls),
            file_secret_settings,
        )


class ConfigLoader:
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)

    def load(self, config: str | None = None) -> dict[str, Any]:
        data = self.load_yaml(self.config_dir / "base.yaml")

        if config:
            path = self.config_dir / config
            config_data = self.load_yaml(path)
        else:
            path = self.fetch_config_path()
            config_data = self.load_yaml(path)

        self.update(data, config_data)
        self.override(data, os.environ.copy())
        return data

    def update(self, data: dict[str, Any], overrides: dict[str, Any]):
        self.merge(data, overrides)

    def override(self, data: dict[str, Any], overrides: dict[str, Any]):
        # NOTE: overrides values should be plain
        # NOTE: all fields with same name will be overriden
        for key, value in data.items():
            if isinstance(value, dict):
                self.override(value, overrides)  # type: ignore
                continue
            for k, v in overrides.items():
                if k.lower() == key.lower():
                    data[key] = v

    def merge(self, data: dict[str, Any], overrides: dict[str, Any]):
        # NOTE: overrides values should follow data structure
        for key in data.keys():
            for k, v in overrides.items():
                if k == key and isinstance(v, dict):
                    self.override(data[k], v)  # type: ignore
                elif k == key:
                    data[k] = v

    def load_yaml(self, path: str | Path) -> dict[str, Any]:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found at: {path}")
        with path.open("r") as f:
            return yaml.safe_load(f) or {}

    def fetch_config_path(self) -> Path:
        """
        1. --config
        2. ENV CONFIG_PATH
        3. default configs/config.yaml
        """
        default = "configs/config.yaml"

        parser = ArgumentParser(description="Load config path")
        parser.add_argument("--config", type=str, help="Path to config file")
        args, _ = parser.parse_known_args()

        load_dotenv(override=False)
        return Path(args.config or os.getenv("CONFIG_PATH") or default)
