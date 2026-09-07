from unittest.mock import AsyncMock

import pytest

from src.library_catalog.data.repositories.book_repository import BookRepository
from src.library_catalog.domain.services.book_service import BookService
from src.library_catalog.external.openlibrary.client import OpenLibraryClient


@pytest.fixture
def mock_book_repo() -> AsyncMock:
    """Мок репозитория книг."""
    return AsyncMock(spec=BookRepository)


@pytest.fixture
def mock_ol_client() -> AsyncMock:
    """Мок клиента Open Library."""
    return AsyncMock(spec=OpenLibraryClient)


@pytest.fixture
def book_service(mock_book_repo: AsyncMock, mock_ol_client: AsyncMock) -> BookService:
    """BookService с замоканными зависимостями."""
    return BookService(book_repository=mock_book_repo, openlibrary_client=mock_ol_client)
