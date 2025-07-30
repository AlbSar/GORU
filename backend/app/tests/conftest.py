"""
Pytest fixtures ve test konfigürasyonu.
Tüm testlerde kullanılacak ortak fixture'lar ve helper fonksiyonlar.
"""

import os
import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..auth import get_current_user
from ..main import app
from ..models import Base  # Models dosyasındaki Base'i kullan
from ..routes.common import get_db  # Doğru import

# Test ortamını ayarla
os.environ["TESTING"] = "1"
os.environ["PYTEST_CURRENT_TEST"] = "test_session"

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
    return {
        "user": "test_user",
        "id": 1,
        "role": "admin",
        "permissions": ["read", "write", "delete", "admin"],
    }


@pytest.fixture
def mock_auth_bypass():
    """Auth bypass için mock fixture."""
    with patch("app.auth.get_current_user") as mock_auth:
        mock_auth.return_value = {
            "user": "test_user",
            "id": 1,
            "role": "admin",
            "permissions": ["read", "write", "delete", "admin"],
        }
        yield mock_auth


@pytest.fixture
def mock_auth_failure():
    """Auth failure mock fixture."""
    with patch("app.auth.get_current_user", side_effect=Exception("Auth failed")):
        yield


@pytest.fixture
def mock_auth_unauthorized():
    """Auth unauthorized mock fixture."""
    with patch("app.auth.get_current_user") as mock_auth:
        from fastapi import HTTPException, status

        mock_auth.side_effect = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
        yield mock_auth


@pytest.fixture
def mock_auth_forbidden():
    """Auth forbidden mock fixture."""
    with patch("app.auth.get_current_user") as mock_auth:
        from fastapi import HTTPException, status

        mock_auth.side_effect = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )
        yield mock_auth


@pytest.fixture(scope="session")
def test_db():
    """Test veritabanı oluştur."""
    # Test ortamında tabloları oluştur
    try:
        Base.metadata.create_all(bind=engine)
        print("Test veritabanı tabloları oluşturuldu")
    except Exception as e:
        print(f"Test veritabanı tabloları oluşturulurken hata: {e}")
    yield
    # Test sonunda tabloları temizle
    try:
        Base.metadata.drop_all(bind=engine)
        print("Test veritabanı tabloları temizlendi")
    except Exception as e:
        print(f"Test veritabanı tabloları temizlenirken hata: {e}")


@pytest.fixture
def client(test_db):
    """Test client fixture with auth bypass."""
    # Routes dosyasındaki get_db'yi override et
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def client_with_auth(test_db):
    """Test client fixture with proper auth headers."""
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as c:
        c.headers.update({"Authorization": "Bearer test-token-12345"})
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def client_without_auth(test_db):
    """Test client fixture without auth bypass."""
    # Sadece DB override yap, auth override yapma
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def unauthenticated_client(test_db):
    """Test client fixture without auth bypass."""
    # Sadece DB override yap, auth override yapma
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    """Auth token headers fixture."""
    return {"Authorization": "Bearer test-token-12345"}


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
    """Test kullanıcısı oluştur ve user dict'ini döndür."""
    user_data = {
        "name": "Fixture Test User",
        "email": unique_email,
        "password": "test123",
    }
    response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
    if response.status_code == 201:
        return response.json()  # Tüm user dict'ini döndür
    return None


@pytest.fixture
def create_test_stock(client, auth_headers, unique_product):
    """Test stoku oluştur ve stock dict'ini döndür."""
    stock_data = {
        "product_name": unique_product,
        "quantity": 50,
        "location": "Test Location",
    }
    response = client.post("/api/v1/stocks/", json=stock_data, headers=auth_headers)
    if response.status_code == 201:
        return response.json()  # Tüm stock dict'ini döndür
    return None


@pytest.fixture
def create_test_order(client, auth_headers, create_test_user, unique_product):
    """Test siparişi oluştur ve order dict'ini döndür."""
    if create_test_user:
        user_id = create_test_user["id"]  # dict'ten ID'yi al
        order_data = {
            "user_id": user_id,  # user ID'yi kullan
            "product_name": unique_product,
            "amount": 100.0,
        }
        response = client.post("/api/v1/orders/", json=order_data, headers=auth_headers)
        if response.status_code == 201:
            return response.json()  # Tüm order dict'ini döndür
    return None


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
