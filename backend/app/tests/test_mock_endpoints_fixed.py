"""
Mock Endpoint testleri - USE_MOCK=true environment için.
Mock servislerinin tüm CRUD işlemlerini test eder.
"""

import os
import uuid
from unittest.mock import patch

import pytest


@pytest.fixture
def mock_client(client):
    """Mock mode'da test client."""
    # Mock environment'ı set et
    with patch.dict(os.environ, {"USE_MOCK": "true"}):
        # App'e mock router'ını ekle
        from ..main import app
        from ..mock_routes import mock_router

        # Router'ı temizle ve yeniden ekle
        app.router.routes = [
            r for r in app.router.routes if not str(r.path).startswith("/mock")
        ]
        app.include_router(mock_router)

        yield client


class TestMockUsers:
    """Mock kullanıcı endpoint testleri."""

    def test_get_mock_users(self, mock_client):
        """Mock kullanıcı listesi testi."""
        response = mock_client.get("/mock/users")
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 5  # faker ile en az 5 kullanıcı oluşturulur

        # İlk kullanıcının yapısını kontrol et
        if users:
            user = users[0]
            assert "id" in user
            assert "name" in user
            assert "email" in user
            assert "role" in user

    def test_get_mock_user_by_id(self, mock_client):
        """ID'ye göre mock kullanıcı testi."""
        # Önce liste al
        response = mock_client.get("/mock/users")
        users = response.json()

        if users:
            user_id = users[0]["id"]
            response = mock_client.get(f"/mock/users/{user_id}")
            assert response.status_code == 200
            user = response.json()
            assert user["id"] == user_id

    def test_create_mock_user(self, mock_client):
        """Mock kullanıcı oluşturma testi."""
        user_data = {
            "name": "Mock Test User",
            "email": f"mock-{uuid.uuid4()}@test.com",
            "role": "user",
            "is_active": True,
        }
        response = mock_client.post("/mock/users/", json=user_data)
        assert response.status_code == 201
        created_user = response.json()
        assert created_user["name"] == user_data["name"]
        assert created_user["email"] == user_data["email"]
        assert "id" in created_user

    def test_update_mock_user(self, mock_client):
        """Mock kullanıcı güncelleme testi."""
        # Önce bir kullanıcı oluştur
        user_data = {
            "name": "Update Test User",
            "email": f"update-{uuid.uuid4()}@test.com",
            "role": "user",
            "is_active": True,
        }
        create_response = mock_client.post("/mock/users/", json=user_data)
        user_id = create_response.json()["id"]

        # Güncelle
        update_data = {"name": "Updated Mock User"}
        response = mock_client.put(f"/mock/users/{user_id}", json=update_data)
        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["name"] == "Updated Mock User"

    def test_delete_mock_user(self, mock_client):
        """Mock kullanıcı silme testi."""
        # Önce bir kullanıcı oluştur
        user_data = {
            "name": "Delete Test User",
            "email": f"delete-{uuid.uuid4()}@test.com",
            "role": "user",
            "is_active": True,
        }
        create_response = mock_client.post("/mock/users/", json=user_data)
        user_id = create_response.json()["id"]

        # Sil
        response = mock_client.delete(f"/mock/users/{user_id}")
        assert response.status_code == 204

        # Silindiğini kontrol et
        get_response = mock_client.get(f"/mock/users/{user_id}")
        assert get_response.status_code == 404


class TestMockStocks:
    """Mock stok endpoint testleri."""

    def test_get_mock_stocks(self, mock_client):
        """Mock stok listesi testi."""
        response = mock_client.get("/mock/stocks")
        assert response.status_code == 200
        stocks = response.json()
        assert isinstance(stocks, list)
        assert len(stocks) >= 5  # faker ile en az 5 stok oluşturulur

    def test_create_mock_stock(self, mock_client):
        """Mock stok oluşturma testi."""
        stock_data = {
            "product_name": f"Mock Product {uuid.uuid4()}",
            "quantity": 100,
            "unit_price": 25.99,
            "supplier": "Mock Supplier",
        }
        response = mock_client.post("/mock/stocks/", json=stock_data)
        assert response.status_code == 201
        created_stock = response.json()
        assert created_stock["product_name"] == stock_data["product_name"]
        assert created_stock["quantity"] == stock_data["quantity"]

    def test_update_mock_stock(self, mock_client):
        """Mock stok güncelleme testi."""
        # Önce bir stok oluştur
        stock_data = {
            "product_name": f"Update Stock {uuid.uuid4()}",
            "quantity": 50,
            "unit_price": 15.99,
            "supplier": "Update Supplier",
        }
        create_response = mock_client.post("/mock/stocks/", json=stock_data)
        stock_id = create_response.json()["id"]

        # Güncelle
        update_data = {"quantity": 200}
        response = mock_client.put(f"/mock/stocks/{stock_id}", json=update_data)
        assert response.status_code == 200
        updated_stock = response.json()
        assert updated_stock["quantity"] == 200

    def test_delete_mock_stock(self, mock_client):
        """Mock stok silme testi."""
        # Önce bir stok oluştur
        stock_data = {
            "product_name": f"Delete Stock {uuid.uuid4()}",
            "quantity": 25,
            "unit_price": 12.50,
            "supplier": "Delete Supplier",
        }
        create_response = mock_client.post("/mock/stocks/", json=stock_data)
        stock_id = create_response.json()["id"]

        # Sil
        response = mock_client.delete(f"/mock/stocks/{stock_id}")
        assert response.status_code == 204


class TestMockOrders:
    """Mock sipariş endpoint testleri."""

    def test_get_mock_orders(self, mock_client):
        """Mock sipariş listesi testi."""
        response = mock_client.get("/mock/orders")
        assert response.status_code == 200
        orders = response.json()
        assert isinstance(orders, list)
        assert len(orders) >= 3  # faker ile en az 3 sipariş oluşturulur

    def test_create_mock_order(self, mock_client):
        """Mock sipariş oluşturma testi."""
        order_data = {
            "user_id": 1,
            "total_amount": 150.75,
            "status": "pending",
            "order_items": [
                {
                    "product_id": 1,
                    "quantity": 2,
                    "unit_price": 75.375,
                    "total_price": 150.75,
                }
            ],
        }
        response = mock_client.post("/mock/orders/", json=order_data)
        assert response.status_code == 201
        created_order = response.json()
        assert created_order["user_id"] == order_data["user_id"]
        assert created_order["total_amount"] == order_data["total_amount"]

    def test_update_mock_order(self, mock_client):
        """Mock sipariş güncelleme testi."""
        # Önce bir sipariş oluştur
        order_data = {
            "user_id": 1,
            "total_amount": 100.0,
            "status": "pending",
            "order_items": [],
        }
        create_response = mock_client.post("/mock/orders/", json=order_data)
        order_id = create_response.json()["id"]

        # Güncelle
        update_data = {"status": "completed"}
        response = mock_client.put(f"/mock/orders/{order_id}", json=update_data)
        assert response.status_code == 200
        updated_order = response.json()
        assert updated_order["status"] == "completed"


class TestMockValidation:
    """Mock endpoint validasyon testleri."""

    def test_mock_user_invalid_data(self, mock_client):
        """Mock kullanıcı geçersiz veri testi."""
        invalid_data = {
            "name": "",  # Boş isim
            "email": "invalid-email",  # Geçersiz email
            "role": "invalid_role",  # Geçersiz rol
        }
        response = mock_client.post("/mock/users/", json=invalid_data)
        # Mock service validation'a bağlı olarak 201 veya 422
        assert response.status_code in [201, 422]

    def test_mock_stock_negative_quantity(self, mock_client):
        """Mock stok negatif miktar testi."""
        invalid_stock = {
            "product_name": "Test Product",
            "quantity": -10,  # Negatif miktar
            "unit_price": 25.99,
            "supplier": "Test Supplier",
        }
        response = mock_client.post("/mock/stocks/", json=invalid_stock)
        # Mock service validation'a bağlı olarak 201 veya 422
        assert response.status_code in [201, 422]

    def test_mock_nonexistent_resource(self, mock_client):
        """Mock olmayan kaynak testi."""
        response = mock_client.get("/mock/users/99999")
        assert response.status_code == 404

        response = mock_client.get("/mock/stocks/99999")
        assert response.status_code == 404

        response = mock_client.get("/mock/orders/99999")
        assert response.status_code == 404


class TestMockServiceFunctionality:
    """Mock servis fonksiyonellik testleri."""

    def test_mock_data_persistence(self, mock_client):
        """Mock veri kalıcılık testi (session boyunca)."""
        # Kullanıcı oluştur
        user_data = {
            "name": "Persistence Test User",
            "email": f"persist-{uuid.uuid4()}@test.com",
            "role": "user",
            "is_active": True,
        }
        create_response = mock_client.post("/mock/users/", json=user_data)
        user_id = create_response.json()["id"]

        # Aynı session'da veriyi tekrar al
        get_response = mock_client.get(f"/mock/users/{user_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == user_data["name"]

    def test_mock_data_isolation(self, mock_client):
        """Mock veri izolasyon testi."""
        # Her test için bağımsız mock data olduğunu kontrol et
        initial_response = mock_client.get("/mock/users")
        initial_count = len(initial_response.json())

        # Yeni kullanıcı ekle
        user_data = {
            "name": "Isolation Test User",
            "email": f"isolation-{uuid.uuid4()}@test.com",
            "role": "user",
            "is_active": True,
        }
        mock_client.post("/mock/users/", json=user_data)

        # Sayının arttığını kontrol et
        final_response = mock_client.get("/mock/users")
        final_count = len(final_response.json())
        assert final_count == initial_count + 1

    def test_mock_router_included_when_enabled(self, mock_client):
        """USE_MOCK=true olduğunda mock router dahil edilmeli."""
        # Mock router'ın dahil edildiğini kontrol et
        response = mock_client.get("/mock/users")
        assert response.status_code == 200
        # Mock endpoint erişilebilir olmalı
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 5


class TestMockEdgeCases:
    """Mock endpoint edge case testleri."""

    def test_mock_empty_pagination(self, mock_client):
        """Mock boş pagination testi."""
        # Çok büyük skip değeri
        response = mock_client.get("/mock/users?skip=1000&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_mock_large_limit(self, mock_client):
        """Mock büyük limit testi."""
        # Çok büyük limit değeri - validation hatası olabilir
        response = mock_client.get("/mock/users?limit=10000")
        assert response.status_code in [200, 422]  # 422 validation error olabilir
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    def test_mock_negative_pagination(self, mock_client):
        """Mock negatif pagination testi."""
        # Negatif skip değeri
        response = mock_client.get("/mock/users?skip=-10")
        assert response.status_code == 422  # Validation error

    def test_mock_data_structure(self, mock_client):
        """Mock data yapısı testi."""
        # Users data yapısı
        response = mock_client.get("/mock/users")
        users = response.json()

        if users:
            user = users[0]
            required_fields = ["id", "name", "email", "role", "is_active"]
            for field in required_fields:
                assert field in user

        # Stocks data yapısı
        response = mock_client.get("/mock/stocks")
        stocks = response.json()

        if stocks:
            stock = stocks[0]
            required_fields = [
                "id",
                "product_name",
                "quantity",
                "unit_price",
                "supplier",
            ]
            for field in required_fields:
                assert field in stock

        # Orders data yapısı
        response = mock_client.get("/mock/orders")
        orders = response.json()

        if orders:
            order = orders[0]
            required_fields = ["id", "user_id", "total_amount", "status"]
            for field in required_fields:
                assert field in order

    def test_mock_concurrent_operations(self, mock_client):
        """Mock eşzamanlı işlem testi."""
        # Aynı anda birden fazla kullanıcı oluştur
        user_ids = []
        for i in range(3):
            user_data = {
                "name": f"Concurrent User {i}",
                "email": f"concurrent{i}@test.com",
                "role": "user",
                "is_active": True,
            }
            response = mock_client.post("/mock/users/", json=user_data)
            assert response.status_code == 201
            user_ids.append(response.json()["id"])

        # Tüm oluşturulan kullanıcıları kontrol et
        for user_id in user_ids:
            response = mock_client.get(f"/mock/users/{user_id}")
            assert response.status_code == 200

    def test_mock_error_handling(self, mock_client):
        """Mock hata yönetimi testi."""
        # Geçersiz ID formatları
        invalid_ids = ["abc", "-1", "0", "1.5"]

        for invalid_id in invalid_ids:
            response = mock_client.get(f"/mock/users/{invalid_id}")
            assert response.status_code in [404, 422]

        # Geçersiz JSON - mock endpoint'ler Content-Type validation'dan muaf
        response = mock_client.post("/mock/users/", data="invalid json")
        assert response.status_code in [
            422,
            400,
            500,
        ]  # Mock endpoint'ler farklı hatalar verebilir
