import logging

from common.infrastructure.config.config import AppConfig


def log_config(logger: logging.Logger, cfg: AppConfig) -> None:
    logger.info(
        "Configuration loaded",
        extra={
            "extra": {
                "env": cfg.env,
                "config": cfg.masked_dict(),
            }
        },
    )
