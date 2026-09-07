"""
Library Catalog API - Точка входа приложения.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1.routers import books, health
from .core.config import settings
from .core.database import dispose_engine
from .core.exceptions import register_exception_handlers
from .core.logging_config import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifecycle manager для FastAPI.

    Выполняется при:
    - startup: настройка логирования
    - shutdown: закрытие подключений к БД
    """
    setup_logging()
    print("🚀 Application started")

    yield

    await dispose_engine()
    print("👋 Application stopped")


app = FastAPI(
    title=settings.app_name,
    description="REST API для управления библиотечным каталогом",
    version="1.0.0",
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(books.router, prefix=settings.api_v1_prefix)
app.include_router(health.router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root() -> dict[str, str]:
    """Корневой эндпоинт."""
    return {
        "message": "Welcome to Library Catalog API",
        "docs": settings.docs_url,
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.library_catalog.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
