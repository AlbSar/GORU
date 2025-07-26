"""
Pydantic şemaları.
ERP sistemi için veri doğrulama ve serileştirme şemalarını içerir.
Kullanıcı, ürün, sipariş ve stok modelleri için Create, Read ve Update şemaları.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

# --- User & Address Schemas ---


class AddressBase(BaseModel):
    """
    Adres temel şeması.

    Attributes:
        address_line: Adres satırı
        city: Şehir
        country: Ülke
        postal_code: Posta kodu
        is_default: Varsayılan adres mi
    """

    address_line: str
    city: str
    country: str
    postal_code: str
    is_default: bool = False


class AddressCreate(AddressBase):
    pass


class AddressRead(AddressBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    """
    Kullanıcı temel şeması.

    Attributes:
        name: Kullanıcı adı
        email: E-posta adresi
        role: Kullanıcı rolü (customer, admin, vb.)
        is_active: Kullanıcının aktif olup olmadığı
    """

    name: str
    email: EmailStr
    role: str = "customer"
    is_active: bool = True


class UserCreate(UserBase):
    """
    Kullanıcı oluşturma şeması.

    Attributes:
        password: Şifre (hash'lenecek)
    """

    password: str


class UserRead(UserBase):
    """
    Kullanıcı okuma şeması.

    Attributes:
        id: Kullanıcı kimliği
        created_at: Hesap oluşturma tarihi
        updated_at: Son güncelleme tarihi
        addresses: Kullanıcının adresleri
        orders: Kullanıcının siparişleri
    """

    id: int
    created_at: datetime
    updated_at: datetime
    addresses: List[AddressRead] = []
    orders: List["OrderRead"] = []
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """
    Kullanıcı güncelleme şeması.
    Tüm alanlar opsiyonel, sadece değiştirilecek alanlar gönderilir.

    Attributes:
        name: Kullanıcı adı (opsiyonel)
        email: E-posta adresi (opsiyonel)
        role: Kullanıcı rolü (opsiyonel)
        is_active: Aktiflik durumu (opsiyonel)
        password: Şifre (opsiyonel, hash'lenecek)
    """

    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


# --- Category & Product Schemas ---


class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    name: str
    sku: str
    category_id: Optional[int] = None
    price: float
    stock: int
    description: Optional[str] = None
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int
    created_at: datetime
    category: Optional[CategoryRead] = None
    model_config = ConfigDict(from_attributes=True)


# --- Order & OrderItem Schemas ---


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float
    total_price: float


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemRead(OrderItemBase):
    id: int
    product: Optional[ProductRead] = None
    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    user_id: int
    status: str = "pending"
    total_amount: float
    shipping_address_id: Optional[int] = None


class OrderCreate(OrderBase):
    order_items: List[OrderItemCreate]


class OrderRead(OrderBase):
    id: int
    created_at: datetime
    order_items: List[OrderItemRead] = []
    shipping_address: Optional[AddressRead] = None
    product_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# --- Stock & StockMovement Schemas ---


class StockBase(BaseModel):
    product_name: str
    quantity: int
    location: Optional[str] = None

    @field_validator("product_name")
    @classmethod
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError(
                "Ürün adı boş olamaz / Product name cannot be empty"
            )
        return v


class StockCreate(StockBase):
    @field_validator("quantity")
    @classmethod
    def quantity_non_negative(cls, v):
        if v < 0:
            raise ValueError("Quantity cannot be negative")
        return v


class StockRead(StockBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class StockMovementBase(BaseModel):
    product_id: int
    movement_type: str  # IN, OUT, TRANSFER
    quantity: int
    source_location: Optional[str] = None
    dest_location: Optional[str] = None


class StockMovementCreate(StockMovementBase):
    pass


class StockMovementRead(StockMovementBase):
    id: int
    created_at: datetime
    product: Optional[ProductRead] = None
    model_config = ConfigDict(from_attributes=True)


class StockUpdate(BaseModel):
    product_name: Optional[str] = None
    quantity: Optional[int] = None
    location: Optional[str] = None

    @field_validator("product_name")
    @classmethod
    def name_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError(
                "Ürün adı boş olamaz / Product name cannot be empty"
            )
        return v


UserRead.model_rebuild()
