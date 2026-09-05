from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.library_catalog.api.v1.schemas.book import BookCreate
from src.library_catalog.data.models.book import Book
from src.library_catalog.domain.exceptions import (
    BookAlreadyExistsException,
    BookNotFoundException,
    InvalidPagesException,
    InvalidYearException,
    OpenLibraryException,
)
from src.library_catalog.domain.services.book_service import BookService


def make_book(**overrides) -> Book:
    """Хелпер для создания тестового объекта Book с дефолтными значениями."""
    now = datetime.now(timezone.utc)
    defaults = {
        "book_id": uuid4(),
        "title": "Clean Code",
        "author": "Robert Martin",
        "year": 2008,
        "genre": "Programming",
        "pages": 464,
        "available": True,
        "isbn": "9780132350884",
        "description": "A Handbook of Agile Software Craftsmanship",
        "extra": None,
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(overrides)
    return Book(**defaults)


@pytest.mark.asyncio
async def test_create_book_success(
    book_service: BookService,
    mock_book_repo,
    mock_ol_client,
) -> None:
    """Успешное создание книги: ISBN свободен, Open Library отвечает."""
    mock_book_repo.find_by_isbn.return_value = None
    mock_ol_client.enrich.return_value = {"cover_url": "http://example.com/cover.jpg"}
    mock_book_repo.create.return_value = make_book()

    book_data = BookCreate(
        title="Clean Code",
        author="Robert Martin",
        year=2008,
        genre="Programming",
        pages=464,
        isbn="9780132350884",
    )

    result = await book_service.create_book(book_data)

    assert result.title == "Clean Code"
    assert result.author == "Robert Martin"
    mock_book_repo.find_by_isbn.assert_awaited_once_with("9780132350884")
    mock_ol_client.enrich.assert_awaited_once()
    mock_book_repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_book_invalid_year_future(
    book_service: BookService,
) -> None:
    """Год издания в будущем должен вызывать InvalidYearException."""
    from datetime import datetime

    future_year = datetime.now().year + 1

    book_data = BookCreate(
        title="Some Book",
        author="Some Author",
        year=future_year,
        genre="Fiction",
        pages=100,
    )

    with pytest.raises(InvalidYearException):
        await book_service.create_book(book_data)


@pytest.mark.parametrize("invalid_pages", [0, -42])
def test_validate_pages_raises(
    book_service: BookService,
    invalid_pages: int,
) -> None:
    """Некорректное количество страниц (0 или отрицательное) должно вызывать InvalidPagesException."""
    with pytest.raises(InvalidPagesException):
        book_service._validate_pages(invalid_pages)

@pytest.mark.asyncio
async def test_create_book_isbn_conflict(
    book_service: BookService,
    mock_book_repo,
) -> None:
    """Существующий ISBN должен вызывать BookAlreadyExistsException."""
    mock_book_repo.find_by_isbn.return_value = make_book()

    book_data = BookCreate(
        title="Clean Code",
        author="Robert Martin",
        year=2008,
        genre="Programming",
        pages=464,
        isbn="9780132350884",
    )

    with pytest.raises(BookAlreadyExistsException):
        await book_service.create_book(book_data)


@pytest.mark.asyncio
async def test_create_book_openlibrary_unavailable(
    book_service: BookService,
    mock_book_repo,
    mock_ol_client,
) -> None:
    """Недоступность Open Library не должна прерывать создание книги."""
    mock_book_repo.find_by_isbn.return_value = None
    mock_ol_client.enrich.side_effect = OpenLibraryException("service down")
    mock_book_repo.create.return_value = make_book(extra=None)

    book_data = BookCreate(
        title="Clean Code",
        author="Robert Martin",
        year=2008,
        genre="Programming",
        pages=464,
        isbn="9780132350884",
    )

    result = await book_service.create_book(book_data)

    assert result.extra is None
    mock_book_repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_book_not_found(
    book_service: BookService,
    mock_book_repo,
) -> None:
    """Несуществующий book_id должен вызывать BookNotFoundException."""
    mock_book_repo.get_by_id.return_value = None

    with pytest.raises(BookNotFoundException):
        await book_service.get_book(uuid4())
