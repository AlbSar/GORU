from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
import datetime

Base = declarative_base()

class User(Base):
    """
    TR: Kullanıcı tablosu modeli.
    EN: User table model.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")

class Order(Base):
    """
    TR: Sipariş tablosu modeli.
    EN: Order table model.
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="orders")

class Stock(Base):
    """
    TR: Stok tablosu modeli.
    EN: Stock table model.
    """
    __tablename__ = "stocks"
    __table_args__ = (UniqueConstraint("product_name", name="uq_product_name"),)

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, unique=True, nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=0)
    location = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False) 