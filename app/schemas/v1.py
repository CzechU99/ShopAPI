from pydantic import BaseModel, EmailStr, Field, condecimal, conint
from typing import Optional, List

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str = Field(min_length=8)

class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_active: bool

    class Config:
        orm_mode = True

class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str]
    price: condecimal(max_digits=12, decimal_places=2)
    stock: conint(ge=0)

class ProductRead(BaseModel):
    id: int
    sku: str
    name: str
    price: condecimal(max_digits=12, decimal_places=2)
    stock: int

    class Config:
        orm_mode = True
