"""
SQLAlchemy veritabanı modelleri.
ERP sistemi için kullanıcı, ürün, sipariş ve stok modellerini içerir.
"""

import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    """
    Kullanıcı modeli.

    Attributes:
        id: Benzersiz kullanıcı kimliği
        name: Kullanıcı adı
        email: Benzersiz e-posta adresi
        password_hash: Şifrelenmiş parola
        role: Kullanıcı rolü (customer, admin, vb.)
        is_active: Kullanıcının aktif olup olmadığı (1: aktif, 0: pasif)
        created_at: Hesap oluşturma tarihi
        updated_at: Son güncelleme tarihi
    """

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="customer", nullable=False)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    addresses = relationship(
        "Address", back_populates="user", cascade="all, delete-orphan"
    )


class Address(Base):
    """
    Adres modeli.

    Attributes:
        id: Benzersiz adres kimliği
        user_id: Adresin ait olduğu kullanıcı
        address_line: Adres satırı
        city: Şehir
        country: Ülke
        postal_code: Posta kodu
        is_default: Varsayılan adres mi (1: evet, 0: hayır)
    """

    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    address_line = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    is_default = Column(Integer, default=0)
    user = relationship("User", back_populates="addresses")


class Category(Base):
    """
    Kategori modeli.

    Attributes:
        id: Benzersiz kategori kimliği
        name: Kategori adı
        parent_id: Üst kategori kimliği (hiyerarşik yapı için)
        description: Kategori açıklaması
    """

    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    description = Column(String)
    parent = relationship("Category", remote_side=[id])


class Product(Base):
    """
    Ürün modeli.

    Attributes:
        id: Benzersiz ürün kimliği
        name: Ürün adı
        sku: Stok tutma birimi (benzersiz)
        category_id: Ürünün ait olduğu kategori
        price: Ürün fiyatı
        stock: Stok miktarı
        description: Ürün açıklaması
        is_active: Ürün aktif mi (1: evet, 0: hayır)
        created_at: Ürün oluşturma tarihi
    """

    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    sku = Column(String, unique=True, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    description = Column(String)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    category = relationship("Category")


class Order(Base):
    """
    Sipariş modeli.

    Attributes:
        id: Benzersiz sipariş kimliği
        user_id: Siparişi veren kullanıcı
        status: Sipariş durumu (pending, confirmed, shipped, delivered)
        total_amount: Toplam sipariş tutarı
        created_at: Sipariş oluşturma tarihi
        shipping_address_id: Teslimat adresi
    """

    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="pending", nullable=False)
    total_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User", back_populates="orders")
    order_items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
    shipping_address_id = Column(Integer, ForeignKey("addresses.id"))
    shipping_address = relationship("Address")


class OrderItem(Base):
    """
    Sipariş kalemi modeli.

    Attributes:
        id: Benzersiz kalem kimliği
        order_id: Ait olduğu sipariş
        product_id: Ürün kimliği
        quantity: Miktar
        unit_price: Birim fiyat
        total_price: Toplam fiyat (quantity * unit_price)
    """

    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product")


class StockMovement(Base):
    """
    Stok hareketi modeli.

    Attributes:
        id: Benzersiz hareket kimliği
        product_id: Ürün kimliği
        quantity: Hareket miktarı (pozitif: giriş, negatif: çıkış)
        source_location: Kaynak konum
        dest_location: Hedef konum
        created_at: Hareket tarihi
    """

    __tablename__ = "stock_movements"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    movement_type = Column(String, nullable=False)  # IN, OUT, TRANSFER
    quantity = Column(Integer, nullable=False)
    source_location = Column(String)
    dest_location = Column(String)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    product = relationship("Product")


class Stock(Base):
    """
    Stok modeli.

    Attributes:
        id: Benzersiz stok kimliği
        product_name: Ürün adı (benzersiz)
        quantity: Stok miktarı
        location: Stok konumu
        created_at: Stok kaydı oluşturma tarihi
    """

    __tablename__ = "stocks"
    __table_args__ = (UniqueConstraint("product_name", name="uq_product_name"),)
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, unique=True, nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=0)
    location = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
