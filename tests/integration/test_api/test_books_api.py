import pytest


@pytest.mark.asyncio
async def test_book_crud_cycle(client) -> None:
    """Полный цикл: создать → получить → обновить → удалить → проверить отсутствие."""
    create_response = await client.post(
        "/api/v1/books/",
        json={
            "title": "Integration Test Book",
            "author": "Test Author",
            "year": 2020,
            "genre": "Testing",
            "pages": 100,
        },
    )
    assert create_response.status_code == 201
    book_id = create_response.json()["book_id"]

    get_response = await client.get(f"/api/v1/books/{book_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Integration Test Book"

    update_response = await client.patch(
        f"/api/v1/books/{book_id}",
        json={"available": False},
    )
    assert update_response.status_code == 200
    assert update_response.json()["available"] is False

    delete_response = await client.delete(f"/api/v1/books/{book_id}")
    assert delete_response.status_code == 204

    final_get = await client.get(f"/api/v1/books/{book_id}")
    assert final_get.status_code == 404
