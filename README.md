# Auth MinIO

[![Python](https://img.shields.io/badge/python-3.11.9-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)](https://www.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17.0-blue?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![MinIO](https://img.shields.io/badge/MinIO-latest-blue?logo=minio&logoColor=fff)](https://www.min.io/)
[![Docker](https://img.shields.io/badge/Docker-27.0+-blue?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Auth MinIO** — сервис по загрузке изображений с аутентификацией.

## Возможности

- Регистрация и аутентификация пользователей
- Загрузка изображений в MinIO
- Формирование Presigned URLs

## Архитектура

Проект построен на принципах **CQRS, Clean Architecture и Domain-Driven Design**.

## Технологии

- **Backend:** FastAPI, gRPC, SQLAlchemy и MinIO
- **Базы данных и хранилища:** PostgreSQL, Redis, MinIO
- **Миграции:** Alembic
- **Инфраструктура:** Docker

## Запуск

### Конфигурация

Конфигурация настроена через механизмы слияния конфигурационных файлов.
Примеры конфигурации запуска можно найти в [configs/](configs/example.yaml) и [.env.example](.env.example).

### Запуск через Docker

1. Настроить проект:
   Перед запуском нужно настроить конфигурацию проекта.
   Для запуска всего проекта в среде Docker достаточно скопировать `.env.example` в `.env`.

   ```bash
   cp .env.example .env
   ```

2. Запустить проект:

   ```bash
   docker compose up
   ```

3. API можно запустить локально:

   ```bash
   export PYTHONPATH="src"
   export CONFIG_PATH="configs/example.host.yaml"
   python -m cli.services.api
   ```

После запуска API будет доступно по адресу: [http://localhost:8000](http://localhost:8000)

_\*Поскольку MinIO генерирует Presigned URL на основе заголовка Host (имя домена, для которого предназначен запрос),
API, запущенный в docker будет формировать недоступный из сети хоста (например, браузера) URL,
поэтому имеет смысл запустить API в сети хоста, перед этим внеся соответсвующие изменения в конфигурацию._

## API и документация

- Swagger-документация доступна из коробки (FastAPI) по адресу: [http://localhost:8000/docs](http://localhost:8000/docs).

## Тестирование

- **Unit + Integration:**

  ```bash
  pytest tests/
  ```

- **E2E тесты:**

  ```bash
  docker compose -f docker-compose.test.yaml --env-file .env.test up
  ```

## Лицензия

MIT License
