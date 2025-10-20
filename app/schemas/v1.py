from pydantic import BaseModel, EmailStr, Field, condecimal, conint, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    hash_password: Optional[str] = Field(min_length=8, default=None)
    is_active: Optional[bool] = None

class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    price: condecimal(max_digits=12, decimal_places=2)
    stock: conint(ge=0)
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = []

class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[condecimal(max_digits=12, decimal_places=2)] = None
    stock: Optional[conint(ge=0)] = None
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None

class ProductRead(BaseModel):
    id: int
    sku: str
    name: str
    price: Decimal
    stock: int
    description: str
    category_id: Optional[int]
    tag_names: Optional[List[str]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TagRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class ProductReadOrder(BaseModel):
    id: int
    sku: str
    name: str
    price: Decimal
    stock: int
    description: str
    category_id: Optional[int]
    tags: Optional[List[TagRead]] = None
    created_at: datetime

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: conint(gt=0)

class OrderCreate(BaseModel):
    user_id: int
    status: str
    items: List[OrderItemCreate]

class OrderItemRead(BaseModel):
    product: ProductReadOrder
    quantity: int
    unit_price: Decimal

    model_config = ConfigDict(from_attributes=True)

class OrderRead(BaseModel):
    id: int
    user_id: Optional[int]
    status: str
    total_amount: Decimal
    items: List[OrderItemRead]

    model_config = ConfigDict(from_attributes=True)

class OrderItemUpdate(BaseModel):
    product_id: int
    quantity: conint(gt=0)  

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    items: Optional[List[OrderItemUpdate]] = None

class CategoryRead(BaseModel):
    id: int
    name: str
    slug: str

    model_config = ConfigDict(from_attributes=True)

class ReviewRead(BaseModel):
    id: int
    product_id: int
    user_id: Optional[int]
    rating: int
    comment: Optional[str]

    model_config = ConfigDict(from_attributes=True)
