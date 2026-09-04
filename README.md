# Library Catalog API

Учебный REST API для управления библиотечным каталогом на FastAPI.
Реализует слоистую архитектуру (API → Domain → Data/External), с интеграцией внешнего Open Library API для обогащения данных о книгах.

## Стек

- Python 3.12, FastAPI
- PostgreSQL + SQLAlchemy 2.0 (async) + Alembic
- Pydantic / pydantic-settings
- Poetry, ruff, mypy
- Docker Compose (PostgreSQL)

## Запуск

1. Клонировать репозиторий и установить зависимости:
```bash
   poetry install
```

2. Скопировать `.env.example` в `.env` и при необходимости поправить значения:
```bash
   cp .env.example .env
```

3. Поднять PostgreSQL:
```bash
   docker-compose up -d postgres
```

4. Применить миграции:
```bash
   poetry run alembic upgrade head
```

5. Запустить приложение:
```bash
   poetry run uvicorn src.library_catalog.main:app --reload
```

6. Открыть документацию API:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Проверка качества кода

```bash
poetry run ruff check .
poetry run ruff format .
poetry run mypy src
```

## Архитектура

- `api/` — HTTP-слой: роутеры, схемы, DI-контейнер
- `domain/` — бизнес-логика: сервисы, доменные исключения, мапперы
- `data/` — работа с БД: ORM-модели, репозитории
- `external/` — интеграция с внешними API (Open Library)
- `core/` — конфигурация, подключение к БД, логирование