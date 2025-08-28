from common.infrastructure.config.config import AppConfig


def main():
    config = AppConfig.load()
    print(config)


main()
