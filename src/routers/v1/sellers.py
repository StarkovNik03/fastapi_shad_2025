from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from src.models.sellers import Seller
from src.schemas import IncomingSeller, ReturnedAllSellers, ReturnedSeller, ReturnedSeller_with_books
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession
from src.configurations import get_async_session
from sqlalchemy.orm import selectinload


sellers_router = APIRouter(tags=["sellers"], prefix="/sellers")
DBSession = Annotated[AsyncSession, Depends(get_async_session)]

@sellers_router.post(
    "/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED
)
async def create_seller(seller: IncomingSeller,session: DBSession): 
    new_seller = Seller(
        **{
            "first_name": seller.first_name,
            "last_name": seller.last_name,
            "email": seller.email,
            "password": seller.password,
        }
    )
    session.add(new_seller)
    await session.flush()

    return new_seller
    

@sellers_router.get("/", response_model = ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    query = select(Seller)
    result = await session.execute(query)
    sellers = result.scalars().all()
    return {"sellers": sellers}


@sellers_router.get("/{seller_id}", response_model=ReturnedSeller_with_books)
async def get_seller_with_books(seller_id: int, session: DBSession):
    query = select(Seller).options(selectinload(Seller.books)).where(Seller.id == seller_id)
    result = await session.execute(query)
    seller = result.scalars().first()
    
    if seller:
        return seller
    return Response(status_code=status.HTTP_404_NOT_FOUND)


@sellers_router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(seller_id: int, session: DBSession):
    query = select(Seller).options(selectinload(Seller.books)).where(Seller.id == seller_id)
    result = await session.execute(query)
    deleted_seller = result.scalars().first()

    if deleted_seller:
        for book in deleted_seller.books:
            await session.delete(book)

        await session.delete(deleted_seller)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND) 

@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(
    seller_id: int, new_seller_data: ReturnedSeller, session: DBSession
):
    ic("Looking for seller with ID: {seller_id}")
    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name = new_seller_data.first_name
        updated_seller.last_name = new_seller_data.last_name
        updated_seller.email = new_seller_data.email

        await session.flush()
        return updated_seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)

    
