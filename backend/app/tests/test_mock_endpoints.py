"""
Mock endpoint'lerin testleri.
USE_MOCK=true durumunda mock API endpoint'lerini test eder.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from ..core.settings import settings
from ..main import app


@pytest.fixture
def mock_enabled_client():
    """Mock modunda client oluşturur."""
    with patch.object(settings, "USE_MOCK", True):
        with TestClient(app) as client:
            yield client


@pytest.fixture
def mock_disabled_client():
    """Mock modu devre dışı client oluşturur."""
    with patch.object(settings, "USE_MOCK", False):
        with TestClient(app) as client:
            yield client


class TestMockEndpoints:
    """Mock endpoint testleri."""

    def test_mock_users_get_all(self, mock_enabled_client):
        """Mock kullanıcı listesi endpoint'ini test eder."""
        response = mock_enabled_client.get("/mock/users")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # İlk kullanıcının gerekli alanları kontrol et
        first_user = data[0]
        assert "id" in first_user
        assert "name" in first_user
        assert "email" in first_user
        assert "role" in first_user

    def test_mock_user_get_by_id(self, mock_enabled_client):
        """Mock kullanıcı ID'ye göre getirme endpoint'ini test eder."""
        # İlk kullanıcıyı al
        response = mock_enabled_client.get("/mock/users/1")
        assert response.status_code == 200
        user = response.json()
        assert user["id"] == 1
        assert "name" in user
        assert "email" in user

    def test_mock_user_not_found(self, mock_enabled_client):
        """Olmayan mock kullanıcı için 404 testi."""
        response = mock_enabled_client.get("/mock/users/9999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_mock_user_create(self, mock_enabled_client):
        """Mock kullanıcı oluşturma endpoint'ini test eder."""
        new_user = {
            "name": "Test Mock User",
            "email": "mock@test.com",
            "role": "user",
            "is_active": True,
        }
        response = mock_enabled_client.post("/mock/users", json=new_user)
        assert response.status_code == 201
        created_user = response.json()
        assert created_user["name"] == new_user["name"]
        assert created_user["email"] == new_user["email"]
        assert "id" in created_user

    def test_mock_orders_get_all(self, mock_enabled_client):
        """Mock sipariş listesi endpoint'ini test eder."""
        response = mock_enabled_client.get("/mock/orders")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # İlk siparişin gerekli alanları
        first_order = data[0]
        assert "id" in first_order
        assert "user_id" in first_order
        assert "total_amount" in first_order
        assert "status" in first_order

    def test_mock_stocks_get_all(self, mock_enabled_client):
        """Mock stok listesi endpoint'ini test eder."""
        response = mock_enabled_client.get("/mock/stocks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # İlk stokun gerekli alanları
        first_stock = data[0]
        assert "id" in first_stock
        assert "product_name" in first_stock
        assert "quantity" in first_stock
        assert "unit_price" in first_stock

    def test_mock_mode_disabled(self, mock_disabled_client):
        """Mock modu devre dışıyken mock endpoint'lerin çalışmadığını test eder."""
        response = mock_disabled_client.get("/mock/users")
        assert response.status_code == 404  # Route not found

    def test_root_endpoint_shows_mock_status(self, mock_enabled_client):
        """Root endpoint'in mock durumunu gösterdiğini test eder."""
        response = mock_enabled_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "mock_mode" in data
        assert data["mock_mode"] == True


class TestMockDataConsistency:
    """Mock veri tutarlılığı testleri."""

    def test_mock_order_references_valid_user(self, mock_enabled_client):
        """Mock siparişlerin geçerli kullanıcı ID'lerine sahip olduğunu test eder."""
        # Kullanıcıları al
        users_response = mock_enabled_client.get("/mock/users")
        users = users_response.json()
        user_ids = [user["id"] for user in users]

        # Siparişleri al
        orders_response = mock_enabled_client.get("/mock/orders")
        orders = orders_response.json()

        # Her siparişin user_id'si geçerli olmalı
        for order in orders:
            assert order["user_id"] in user_ids

    def test_mock_data_persistence_during_session(self, mock_enabled_client):
        """Aynı session boyunca mock verinin korunduğunu test eder."""
        # İlk request
        response1 = mock_enabled_client.get("/mock/users")
        users1 = response1.json()

        # İkinci request
        response2 = mock_enabled_client.get("/mock/users")
        users2 = response2.json()

        # Aynı data döndürülmeli
        assert len(users1) == len(users2)
        assert users1[0]["id"] == users2[0]["id"]


@pytest.mark.integration
class TestMockIntegration:
    """Mock sistemi entegrasyon testleri."""

    def test_mock_crud_operations(self, mock_enabled_client):
        """Mock CRUD işlemlerinin tam döngüsünü test eder."""
        # CREATE
        new_user = {"name": "CRUD Test User", "email": "crud@test.com", "role": "user"}
        create_response = mock_enabled_client.post("/mock/users", json=new_user)
        assert create_response.status_code == 201
        created_user = create_response.json()
        user_id = created_user["id"]

        # READ
        read_response = mock_enabled_client.get(f"/mock/users/{user_id}")
        assert read_response.status_code == 200
        read_user = read_response.json()
        assert read_user["name"] == new_user["name"]

        # UPDATE
        update_data = {"name": "Updated CRUD User"}
        update_response = mock_enabled_client.put(
            f"/mock/users/{user_id}", json=update_data
        )
        assert update_response.status_code == 200
        updated_user = update_response.json()
        assert updated_user["name"] == "Updated CRUD User"

        # DELETE
        delete_response = mock_enabled_client.delete(f"/mock/users/{user_id}")
        assert delete_response.status_code == 204

        # Deleted user artık bulunamaz
        get_deleted_response = mock_enabled_client.get(f"/mock/users/{user_id}")
        assert get_deleted_response.status_code == 404
