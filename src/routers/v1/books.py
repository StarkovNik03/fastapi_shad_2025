from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from src.models.books import Book
from src.schemas import IncomingBook, ReturnedAllbooks, ReturnedBook
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession
from src.configurations import get_async_session
from src.models.sellers import Seller

books_router = APIRouter(tags=["books"], prefix="/books")
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


@books_router.post(
    "/", response_model=ReturnedBook, status_code=status.HTTP_201_CREATED
)  
async def create_book(
    book: IncomingBook,
    session: DBSession,
):  
    seller = await session.get(Seller, book.seller_id)

    if not seller:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    new_book = Book(
    **{
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "pages": book.pages,
        "seller_id": book.seller_id 
    }
)

    session.add(new_book)
    await session.flush()

    return new_book


@books_router.get("/", response_model=ReturnedAllbooks)
async def get_all_books(session: DBSession):
    query = select(Book)
    result = await session.execute(query)
    books = result.scalars().all()
    return {"books": books}


@books_router.get("/{book_id}", response_model=ReturnedBook)
async def get_book(book_id: int, session: DBSession):
    if result := await session.get(Book, book_id):
        return result

    return Response(status_code=status.HTTP_404_NOT_FOUND)


@books_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, session: DBSession):
    deleted_book = await session.get(Book, book_id)
    if deleted_book:
        await session.delete(deleted_book)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@books_router.put("/{book_id}", response_model=ReturnedBook)
async def update_book(book_id: int, new_book_data: ReturnedBook, session: DBSession):
    if updated_book := await session.get(Book, book_id):
        updated_book.author = new_book_data.author
        updated_book.title = new_book_data.title
        updated_book.year = new_book_data.year
        updated_book.pages = new_book_data.pages

        await session.flush()

        return updated_book

    return Response(status_code=status.HTTP_404_NOT_FOUND)
