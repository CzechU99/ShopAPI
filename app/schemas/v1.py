from pydantic import BaseModel, EmailStr, Field, condecimal, conint
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str = Field(min_length=8)

class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    price: condecimal(max_digits=12, decimal_places=2)
    stock: conint(ge=0)
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = []

class ProductRead(BaseModel):
    id: int
    sku: str
    name: str
    price: Decimal
    stock: int
    category_id: Optional[int]

    class Config:
        orm_mode = True

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: conint(gt=0)

class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItemCreate]

class OrderItemRead(BaseModel):
    product_id: int
    quantity: int
    unit_price: Decimal

    class Config:
        orm_mode = True

class OrderRead(BaseModel):
    id: int
    user_id: Optional[int]
    status: str
    total_amount: Decimal
    items: List[OrderItemRead]

    class Config:
        orm_mode = True

class CategoryRead(BaseModel):
    id: int
    name: str
    slug: str

    class Config:
        orm_mode = True

class TagRead(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class ReviewRead(BaseModel):
    id: int
    product_id: int
    user_id: Optional[int]
    rating: int
    comment: Optional[str]

    class Config:
        orm_mode = True
