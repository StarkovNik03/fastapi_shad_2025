from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
from src.schemas import ReturnedBook
from typing import List

__all__ = ["IncomingSeller", "ReturnedSeller", "ReturnedAllSellers", "ReturnedSeller_with_books"]

class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    email: str

class IncomingSeller(BaseSeller):
    password: str

    @field_validator("password")
    @staticmethod
    def validate_password(val : str):
        if len(val) < 6:
            raise PydanticCustomError('Длина пароля не может быть меньше 6 символов') 
        
        return val

class ReturnedSeller(BaseSeller):
    id: int

class ReturnedSeller_with_books(BaseSeller):
    id: int
    books: list[ReturnedBook]

class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]

    