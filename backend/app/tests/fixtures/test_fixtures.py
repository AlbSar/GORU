"""
Pytest fixtures for testing.
Test için kullanılacak fixture'lar ve helper fonksiyonlar.
"""

import json
from pathlib import Path

import pytest
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ... import models
from ...database import Base

fake = Faker("tr_TR")

# Test için in-memory SQLite database
TEST_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session")
def test_db():
    """Test veritabanı session fixture'ı."""
    Base.metadata.create_all(bind=test_engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    """Her test için temiz veritabanı session'ı."""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def sample_data():
    """JSON dosyasından örnek veri yükler."""
    fixtures_dir = Path(__file__).parent
    sample_file = fixtures_dir / "sample_data.json"

    with open(sample_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


@pytest.fixture
def sample_user():
    """Örnek kullanıcı verisi."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "role": "admin",
        "is_active": True,
        "password": "test123",
    }


@pytest.fixture
def sample_order():
    """Örnek sipariş verisi."""
    return {
        "user_id": 1,
        "total_amount": 150.75,
        "status": "pending",
        "order_items": [
            {
                "product_id": 1,
                "quantity": 2,
                "unit_price": 50.25,
                "total_price": 100.50,
            }
        ],
    }


@pytest.fixture
def sample_stock():
    """Örnek stok verisi."""
    return {
        "product_name": "Test Product",
        "quantity": 100,
        "unit_price": 25.99,
        "supplier": "Test Supplier",
    }


@pytest.fixture
def fake_user_data():
    """Faker ile üretilen sahte kullanıcı verisi."""
    return {
        "name": fake.name(),
        "email": fake.unique.email(),
        "role": fake.random_element(elements=["admin", "user", "manager"]),
        "is_active": fake.boolean(),
        "password": fake.password(),
    }


@pytest.fixture
def fake_stock_data():
    """Faker ile üretilen sahte stok verisi."""
    return {
        "product_name": f"{fake.company()} {fake.word()}",
        "quantity": fake.random_int(min=0, max=1000),
        "unit_price": round(fake.random.uniform(1.0, 1000.0), 2),
        "supplier": fake.company(),
    }


@pytest.fixture
def multiple_users(db_session: Session):
    """Veritabanına çoklu kullanıcı ekler."""
    users = []
    for i in range(5):
        user = models.User(
            name=fake.name(),
            email=fake.unique.email(),
            role=fake.random_element(elements=["admin", "user", "manager"]),
            is_active=fake.random_element(elements=[0, 1]),
            password_hash=fake.password(),
        )
        db_session.add(user)
        users.append(user)

    db_session.commit()
    return users


@pytest.fixture
def multiple_stocks(db_session: Session):
    """Veritabanına çoklu stok ekler."""
    stocks = []
    for i in range(10):
        stock = models.Stock(
            product_name=f"{fake.company()} {fake.word()}",
            quantity=fake.random_int(min=0, max=500),
            unit_price=round(fake.random.uniform(10.0, 500.0), 2),
            supplier=fake.company(),
        )
        db_session.add(stock)
        stocks.append(stock)

    db_session.commit()
    return stocks


@pytest.fixture
def edge_case_data():
    """Edge case test verileri."""
    return {
        "invalid_email_user": {
            "name": "Invalid Email User",
            "email": "invalid-email",
            "role": "user",
            "is_active": True,
            "password": "test123",
        },
        "empty_name_user": {
            "name": "",
            "email": "empty@example.com",
            "role": "user",
            "is_active": True,
            "password": "test123",
        },
        "negative_quantity_stock": {
            "product_name": "Negative Stock",
            "quantity": -10,
            "unit_price": 25.99,
            "supplier": "Test Supplier",
        },
        "zero_price_stock": {
            "product_name": "Zero Price Stock",
            "quantity": 100,
            "unit_price": 0.0,
            "supplier": "Test Supplier",
        },
    }


def create_test_user(db: Session, **kwargs) -> models.User:
    """Test kullanıcısı oluşturur."""
    user_data = {
        "name": fake.name(),
        "email": fake.unique.email(),
        "role": "user",
        "is_active": 1,
        "password_hash": fake.password(),
    }
    user_data.update(kwargs)

    user = models.User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_test_stock(db: Session, **kwargs) -> models.Stock:
    """Test stoku oluşturur."""
    stock_data = {
        "product_name": f"{fake.company()} {fake.word()}",
        "quantity": fake.random_int(min=1, max=100),
        "unit_price": round(fake.random.uniform(10.0, 100.0), 2),
        "supplier": fake.company(),
    }
    stock_data.update(kwargs)

    stock = models.Stock(**stock_data)
    db.add(stock)
    db.commit()
    db.refresh(stock)
    return stock
