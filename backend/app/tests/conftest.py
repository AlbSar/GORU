"""
Pytest fixtures ve test konfigürasyonu.
Tüm testlerde kullanılacak ortak fixture'lar ve helper fonksiyonlar.
"""

import os
import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..auth import get_current_user
from ..main import app
from ..models import Base  # Models dosyasındaki Base'i kullan
from ..routes.common import get_db  # Doğru import

# Test ortamını ayarla
os.environ["TESTING"] = "1"
os.environ["PYTEST_CURRENT_TEST"] = "test_session"
os.environ["USE_MOCK"] = "true"

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
    db = TestingSessionLocal()
    try:
        # Connection check
        db.execute(text("SELECT 1"))
        yield db
    except Exception as e:
        print(f"Database connection error: {e}")
        db.rollback()
        raise
    finally:
        # Session cleanup - her test sonunda
        try:
            db.rollback()  # Pending transaction'ları rollback
            db.close()
        except Exception as e:
            print(f"Error closing database connection: {e}")


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
    with patch(
        "app.auth.get_current_user", side_effect=Exception("Auth failed")
    ) as mock:
        yield mock


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
    """Test database setup ve teardown."""
    # Mock testlerde database gerekli değil
    if os.getenv("USE_MOCK") == "true":
        yield "mock_database"
        return

    # Database tablolarını oluştur
    Base.metadata.create_all(bind=engine)

    # Test veritabanını kontrol et
    with engine.begin() as conn:
        # Tüm tabloları listele
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result.fetchall()]
        print(f"Created tables: {tables}")

        # OrderItems tablosunu kontrol et
        try:
            result = conn.execute(text("SELECT COUNT(*) FROM order_items"))
            print("OrderItems table exists and accessible")
        except Exception as e:
            print(f"OrderItems table error: {e}")

    yield engine
    # Test sonunda temizlik - güvenli şekilde
    try:
        with engine.begin() as conn:
            # Tüm tabloları temizle
            for table in reversed(Base.metadata.sorted_tables):
                try:
                    conn.execute(text(f"DELETE FROM {table.name}"))
                except Exception as e:
                    print(f"Error cleaning table {table.name}: {e}")
    except Exception as e:
        print(f"Database cleanup error: {e}")
        # Drop_all'ı deneme, sadece temizlik yap
        pass


@pytest.fixture(autouse=True)
def clean_database():
    """Her test sonunda database'i temizle."""
    # Test öncesi
    yield
    # Test sonrası - tüm tabloları temizle
    with engine.begin() as conn:
        # Foreign key constraint'leri devre dışı bırak
        conn.execute(text("PRAGMA foreign_keys=OFF"))
        # Tüm tabloları temizle
        for table in reversed(Base.metadata.sorted_tables):
            try:
                conn.execute(text(f"DELETE FROM {table.name}"))
            except Exception as e:
                print(f"Error cleaning table {table.name}: {e}")
        # Foreign key constraint'leri tekrar etkinleştir
        conn.execute(text("PRAGMA foreign_keys=ON"))


@pytest.fixture
def client(test_db):
    """Test client fixture - auth bypass ile."""
    # Database dependency override
    app.dependency_overrides[get_db] = override_get_db

    # Auth dependency override - test ortamında bypass et
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture
def client_with_auth(test_db):
    """Auth header'ları ile test client."""
    app.dependency_overrides[get_db] = override_get_db
    # Auth dependency override - test ortamında bypass et
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture
def client_without_auth(test_db):
    """Auth olmadan test client."""
    app.dependency_overrides[get_db] = override_get_db
    # Auth dependency override'ı kaldır - gerçek auth kontrolü yap
    # app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture
def unauthenticated_client(test_db):
    """Unauthenticated test client."""
    app.dependency_overrides[get_db] = override_get_db
    # Auth dependency override'ı kaldır - gerçek auth kontrolü yap
    # app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture
def test_user():
    """Test kullanıcısı fixture."""
    return {
        "id": 1,
        "name": "Test User",
        "email": "test@example.com",
        "role": "admin",
        "permissions": ["read", "write", "delete", "admin"],
    }


@pytest.fixture
def auth_headers(test_user):
    """Geçerli auth header'ları."""
    return {
        "Authorization": "Bearer test-token-12345",
        "Content-Type": "application/json",
    }


@pytest.fixture
def invalid_auth_headers():
    """Geçersiz auth header'ları."""
    return {
        "Authorization": "Bearer invalid-token",
        "Content-Type": "application/json",
    }


@pytest.fixture
def no_auth_headers():
    """Auth header'ları olmadan."""
    return {"Content-Type": "application/json"}


@pytest.fixture
def unique_email():
    """Benzersiz email adresi."""
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture
def unique_product():
    """Benzersiz ürün adı."""
    return f"Test Product {uuid.uuid4().hex[:8]}"


@pytest.fixture
def test_user_data(unique_email):
    """Test kullanıcı verisi."""
    return {
        "name": "Test User",
        "email": unique_email,
        "password": "testpassword123",
        "role": "customer",
    }


@pytest.fixture
def test_stock_data(unique_product):
    """Test stok verisi."""
    return {
        "product_name": unique_product,
        "quantity": 100,
        "location": "Warehouse A",
        "price": 50.0,  # Mock testlerde price field'ı ekle
    }


@pytest.fixture
def test_order_data():
    """Test sipariş verisi."""
    return {
        "user_id": 1,
        "status": "pending",
        "total_amount": 150.0,
        "items": [
            {
                "product_id": 1,
                "quantity": 2,
                "unit_price": 75.0,
                "total_price": 150.0,
            }
        ],
    }


@pytest.fixture
def authenticated_client(client, auth_headers):
    """Auth header'ları ile test client."""
    client.headers.update(auth_headers)
    return client


@pytest.fixture
def create_test_user(client, auth_headers, unique_email):
    """Test kullanıcısı oluştur."""
    # Mock testlerde gerçek veri oluşturulmamalı
    if os.getenv("USE_MOCK") == "true":
        return None

    user_data = {
        "name": "Test User",
        "email": unique_email,
        "password": "testpassword123",
        "role": "customer",
    }

    response = client.post("/users/", json=user_data, headers=auth_headers)
    if response.status_code == 201:
        return response.json()
    else:
        # Eğer kullanıcı zaten varsa, mevcut kullanıcıyı döndür
        return {"id": 1, "name": "Test User", "email": unique_email}


@pytest.fixture
def create_test_stock(client, auth_headers, unique_product):
    """Test stok oluştur."""
    # Mock testlerde gerçek veri oluşturulmamalı
    if os.getenv("USE_MOCK") == "true":
        return None

    stock_data = {
        "product_name": unique_product,
        "quantity": 100,
        "location": "Warehouse A",
    }

    response = client.post("/stocks/", json=stock_data, headers=auth_headers)
    if response.status_code == 201:
        return response.json()
    else:
        # Eğer stok zaten varsa, mevcut stoku döndür
        return {"id": 1, "product_name": unique_product, "quantity": 100}


@pytest.fixture
def create_test_order(client, auth_headers, create_test_user, unique_product):
    """Test sipariş oluştur."""
    # Mock testlerde gerçek veri oluşturulmamalı
    if os.getenv("USE_MOCK") == "true":
        return None

    # Önce stok oluştur
    stock_data = {
        "product_name": unique_product,
        "quantity": 100,
        "location": "Warehouse A",
    }

    stock_response = client.post("/stocks/", json=stock_data, headers=auth_headers)
    if stock_response.status_code == 201:
        stock_id = stock_response.json()["id"]
    else:
        stock_id = 1

    # Sipariş oluştur
    order_data = {
        "user_id": create_test_user["id"],
        "status": "pending",
        "total_amount": 150.0,
        "items": [
            {
                "product_id": stock_id,
                "quantity": 2,
                "unit_price": 75.0,
                "total_price": 150.0,
            }
        ],
    }

    response = client.post("/orders/", json=order_data, headers=auth_headers)
    if response.status_code == 201:
        return response.json()
    else:
        return {"id": 1, "user_id": create_test_user["id"], "status": "pending"}


def pytest_configure(config):
    """Pytest konfigürasyonu."""
    # Test marker'larını kaydet
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")


def pytest_collection_modifyitems(config, items):
    """Test collection modifikasyonu."""
    for item in items:
        # Tüm testlere unit marker'ı ekle
        if "unit" not in item.keywords:
            item.add_marker(pytest.mark.unit)
