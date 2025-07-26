"""
Pytest fixtures ve test konfigürasyonu.
Tüm testlerde kullanılacak ortak fixture'lar ve helper fonksiyonlar.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from .. import models
from ..database import Base, get_db
from ..main import app

# Test için in-memory SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Test için database session override."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def test_db():
    """Test veritabanı oluştur."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    """Test client fixture."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    """Auth token headers fixture."""
    return {"Authorization": "Bearer secret-token"}


@pytest.fixture
def test_user_data():
    """Test kullanıcı verisi."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "role": "admin",
        "is_active": True,
        "password": "test123",
    }


@pytest.fixture
def test_stock_data():
    """Test stok verisi."""
    return {
        "product_name": "Test Product",
        "quantity": 100,
        "unit_price": 25.99,
        "supplier": "Test Supplier",
    }


@pytest.fixture
def test_order_data():
    """Test sipariş verisi."""
    return {
        "user_id": 1,
        "total_amount": 150.75,
        "status": "pending",
        "order_items": [
            {"product_id": 1, "quantity": 2, "unit_price": 50.25, "total_price": 100.50}
        ],
    }


@pytest.fixture
def authenticated_client(client, auth_headers):
    """Auth token'lı client."""
    client.headers.update(auth_headers)
    return client


@pytest.fixture
def create_test_user(client, auth_headers):
    """Test kullanıcısı oluştur ve ID'sini döndür."""
    user_data = {
        "name": "Fixture Test User",
        "email": "fixture@test.com",
        "role": "user",
        "is_active": True,
        "password": "test123",
    }
    response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
    if response.status_code == 201:
        return response.json()["id"]
    return None


@pytest.fixture
def create_test_stock(client, auth_headers):
    """Test stoku oluştur ve ID'sini döndür."""
    stock_data = {
        "product_name": "Fixture Test Stock",
        "quantity": 50,
        "unit_price": 15.99,
        "supplier": "Fixture Supplier",
    }
    response = client.post("/api/v1/stocks/", json=stock_data, headers=auth_headers)
    if response.status_code == 201:
        return response.json()["id"]
    return None


def pytest_configure(config):
    """Pytest konfigürasyonu."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "auth: marks tests that require authentication")
