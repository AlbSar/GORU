"""
Pytest fixtures ve test konfigürasyonu.
Tüm testlerde kullanılacak ortak fixture'lar ve helper fonksiyonlar.
"""

import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

from ..database import Base, get_db
from ..main import app
from ..auth import get_current_user

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


def override_get_current_user():
    """Test için auth override - her zaman geçerli kullanıcı döndür."""
    return {"user": "test_user", "id": 1}


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
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    """Auth token headers fixture."""
    return {"Authorization": "Bearer secret-token"}


@pytest.fixture
def invalid_auth_headers():
    """Geçersiz auth token headers fixture."""
    return {"Authorization": "Bearer invalid-token"}


@pytest.fixture
def no_auth_headers():
    """Auth headers olmadan fixture."""
    return {}


@pytest.fixture
def unique_email():
    """Benzersiz email oluştur."""
    return f"test_{uuid.uuid4()}@example.com"


@pytest.fixture
def unique_product():
    """Benzersiz ürün adı oluştur."""
    return f"Product_{uuid.uuid4()}"


@pytest.fixture
def test_user_data(unique_email):
    """Test kullanıcı verisi."""
    return {
        "name": "Test User",
        "email": unique_email,
        "role": "admin",
        "is_active": True,
        "password": "test123",
    }


@pytest.fixture
def test_stock_data(unique_product):
    """Test stok verisi."""
    return {
        "product_name": unique_product,
        "quantity": 100,
        "price": 25.99,
    }


@pytest.fixture
def test_order_data():
    """Test sipariş verisi."""
    return {
        "user_id": 1,
        "product_name": "Test Product",
        "amount": 150.75,
    }


@pytest.fixture
def authenticated_client(client, auth_headers):
    """Auth token'lı client."""
    client.headers.update(auth_headers)
    return client


@pytest.fixture
def create_test_user(client, auth_headers, unique_email):
    """Test kullanıcısı oluştur ve ID'sini döndür."""
    user_data = {
        "name": "Fixture Test User",
        "email": unique_email,
        "password": "test123",
    }
    response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
    if response.status_code == 201:
        return response.json()["id"]
    return None


@pytest.fixture
def create_test_stock(client, auth_headers, unique_product):
    """Test stoku oluştur ve ID'sini döndür."""
    stock_data = {
        "product_name": unique_product,
        "quantity": 50,
        "price": 15.99,
    }
    response = client.post("/api/v1/stocks/", json=stock_data, headers=auth_headers)
    if response.status_code == 201:
        return response.json()["id"]
    return None


@pytest.fixture
def create_test_order(client, auth_headers, create_test_user, unique_product):
    """Test siparişi oluştur ve ID'sini döndür."""
    user_id = create_test_user
    if user_id:
        order_data = {
            "user_id": user_id,
            "product_name": unique_product,
            "amount": 100.0,
        }
        response = client.post("/api/v1/orders/", json=order_data, headers=auth_headers)
        if response.status_code == 201:
            return response.json()["id"]
    return None


@pytest.fixture
def mock_auth_failure():
    """Auth failure mock fixture."""
    with patch("app.auth.get_current_user", side_effect=Exception("Auth failed")):
        yield


@pytest.fixture
def mock_database_error():
    """Database error mock fixture."""
    with patch("app.routes.SessionLocal", side_effect=Exception("Database error")):
        yield


def pytest_configure(config):
    """Pytest konfigürasyonu."""
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "auth: marks tests that require authentication")
    config.addinivalue_line("markers", "error_handling: marks error handling tests")


def pytest_collection_modifyitems(config, items):
    """Test collection sırasında marker'ları otomatik ekle."""
    for item in items:
        # Error handling testlerini işaretle
        if "error_handling" in item.nodeid or "test_error" in item.nodeid:
            item.add_marker(pytest.mark.error_handling)
        
        # Auth testlerini işaretle
        if "auth" in item.nodeid or "test_auth" in item.nodeid:
            item.add_marker(pytest.mark.auth)
