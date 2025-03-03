from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
from typing import Optional


__all__ = ["IncomingBook", "ReturnedBook", "ReturnedAllbooks"]

class BaseBook(BaseModel):
    title: str
    author: str
    year: int
    seller_id: int

class IncomingBook(BaseBook):
    pages: int = Field(
        default=150, alias="count_pages"
    ) 

    @field_validator("year") 
    @staticmethod
    def validate_year(val: int):
        if val < 2020:
            raise PydanticCustomError("Validation error", "Year is too old!")

        return val

class ReturnedBook(BaseBook):
    id: int
    pages: int

class ReturnedAllbooks(BaseModel):
    books: list[ReturnedBook]
