import pytest
from sqlalchemy import select
from src.models.sellers import Seller
from src.models.books import Book
from fastapi import status
from icecream import ic


@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {
        "first_name": "Oleg",
        "last_name": "Ivanov",
        "email": "ivanov@mail.ru",
        "password": "qwerty123"
    }

    response = await async_client.post("/api/v1/sellers/", json = data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    resp_seller_id = result_data.pop("id", None)
    assert resp_seller_id, "Seller id not returned from endpoint"

    expected_data = data.copy()
    expected_data.pop("password")

    assert result_data == expected_data


@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    seller = Seller(first_name = "Nikita", last_name = "Starkov", email = "starkov@mail.ru", password = "123qwerty")
    seller2 = Seller(first_name = "Igor", last_name = "Starkov", email = "starkov@mail.ru", password = "1234qwerty")
    
    db_session.add_all([seller, seller2])
    await db_session.flush()

    response = await async_client.get("/api/v1/sellers/")

    assert response.status_code == status.HTTP_200_OK

    assert (
        len(response.json()["sellers"]) == 2
    ) 

    assert response.json() == {
        "sellers": [
            {
                "first_name": "Nikita",
                "last_name": "Starkov",
                "email": "starkov@mail.ru",
                "id": seller.id
            },
            {
                "first_name": "Igor",
                "last_name": "Starkov",
                "email": "starkov@mail.ru",
                "id": seller2.id
            },
        ]
    }

@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):
    seller = Seller(first_name = "Nikita", last_name = "Starkov", email = "starkov@mail.ru", password = "123qwerty")
    db_session.add(seller)
    await db_session.flush()

    book = Book(author="Pushkin", title="Eugeny Onegin", year=2001, pages=104, seller_id = seller.id)
    db_session.add(book)
    await db_session.flush()

    response = await async_client.get(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {
        "first_name": "Nikita",
        "last_name": "Starkov",
        "email": "starkov@mail.ru",
        "id": seller.id,
        "books": [
        {
            "title": "Eugeny Onegin",
            "author": "Pushkin",
            "year": 2001,
            "seller_id": seller.id,
            "id": book.id,
            "pages": 104
            }
        ]
    }


@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    seller = Seller(first_name="Nikita", last_name="Starkov", email="starkov@mail.ru", password="123qwerty")
    db_session.add(seller)
    await db_session.flush()

    book = Book(author="Pushkin", title="Eugeny Onegin", year=2001, pages=104, seller_id=seller.id)
    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    await db_session.flush()

    result_sellers = await db_session.execute(select(Seller).where(Seller.id == seller.id))
    seller_exists = result_sellers.scalar_one_or_none()
    assert seller_exists is None  

    result_books = await db_session.execute(select(Book).where(Book.seller_id == seller.id))
    books_remaining = result_books.scalars().all()
    assert len(books_remaining) == 0  


@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    seller = Seller(first_name="Nikita", last_name="Starkov", email="starkov@mail.ru", password="123qwerty")
    db_session.add(seller)
    await db_session.flush()

    data = {
            "first_name": "Kolya",
            "last_name": "Lermontov",
            "email": "lermontov@mail.ru",
            "id": seller.id
        }

    response = await async_client.put(f"/api/v1/sellers/{seller.id}", json=data)

    assert response.status_code == status.HTTP_200_OK

    res = await db_session.get(Seller, seller.id)
    assert res.first_name == "Kolya"
    assert res.last_name == "Lermontov"
    assert res.email == "lermontov@mail.ru"
    assert res.id == seller.id
