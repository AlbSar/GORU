"""
Pydantic şemaları.
Kullanıcı ve Sipariş modelleri için Create ve Read şemalarını içerir.
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict, validator
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Kullanıcı adı / User name")
    email: EmailStr = Field(..., description="E-posta adresi / Email address")

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class UserReadWithOrders(UserRead):
    orders: List["OrderRead"] = []

class OrderBase(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=200, description="Ürün adı / Product name")
    amount: float = Field(..., gt=0, description="Tutar / Amount")

class OrderCreate(OrderBase):
    user_id: int = Field(..., description="Kullanıcı ID / User ID")

class OrderRead(OrderBase):
    id: int
    user_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class StockBase(BaseModel):
    product_name: str = Field(..., min_length=1, description="Ürün adı / Product name")
    quantity: int = Field(..., ge=0, description="Stok adedi / Stock quantity")
    location: Optional[str] = Field(None, description="Stok yeri / Stock location")

    @validator("product_name")
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Ürün adı boş olamaz / Product name cannot be empty")
        return v

class StockCreate(StockBase):
    pass

class StockUpdate(BaseModel):
    product_name: Optional[str] = Field(None, min_length=1, description="Ürün adı / Product name")
    quantity: Optional[int] = Field(None, ge=0, description="Stok adedi / Stock quantity")
    location: Optional[str] = Field(None, description="Stok yeri / Stock location")

    @validator("product_name")
    def name_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Ürün adı boş olamaz / Product name cannot be empty")
        return v

class StockRead(StockBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

UserReadWithOrders.model_rebuild() 