"""
Edge case ve hata durumu testleri (Auth Token'lı).
Beklenmedik durumlar ve hata yönetimini auth token ile test eder.
"""

import uuid

import pytest


@pytest.mark.auth
class TestUserEdgeCasesFixed:
    """Kullanıcı endpoint'leri için auth'lu edge case testleri."""

    def test_create_user_invalid_email_format(self, client, auth_headers):
        """Geçersiz e-posta formatı ile kullanıcı oluşturma testi."""
        invalid_user = {
            "name": "Test User",
            "email": "invalid-email-format",
            "role": "user",
            "is_active": True,
            "password": "test123",
        }
        response = client.post("/users/", json=invalid_user, headers=auth_headers)
        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("email" in str(error).lower() for error in error_detail)

    def test_create_user_empty_name(self, client, auth_headers):
        """Boş isim ile kullanıcı oluşturma testi."""
        invalid_user = {
            "name": "",
            "email": f"empty-name-{uuid.uuid4()}@test.com",
            "role": "user",
            "is_active": True,
            "password": "test123",
        }
        response = client.post("/users/", json=invalid_user, headers=auth_headers)
        assert response.status_code == 422

    def test_create_user_missing_required_fields(self, client, auth_headers):
        """Gerekli alanları eksik kullanıcı oluşturma testi."""
        incomplete_user = {
            "name": "Test User"
            # email, role, password eksik
        }
        response = client.post("/users/", json=incomplete_user, headers=auth_headers)
        assert response.status_code == 422

        error_detail = response.json()["detail"]
        required_fields = ["email", "role", "password"]
        for field in required_fields:
            assert any(field in str(error) for error in error_detail)

    def test_get_nonexistent_user(self, client, auth_headers):
        """Olmayan kullanıcı getirme testi."""
        response = client.get("/users/99999", headers=auth_headers)
        assert response.status_code == 404
        # Response format kontrolü - detail alanı olmalı
        response_data = response.json()
        assert "detail" in response_data
        # Türkçe veya İngilizce hata mesajı kontrolü
        detail_text = response_data["detail"].lower()
        assert any(
            keyword in detail_text for keyword in ["not found", "bulunamadı", "user"]
        )

    def test_update_nonexistent_user(self, client, auth_headers):
        """Olmayan kullanıcı güncelleme testi."""
        update_data = {"name": "Updated Name"}
        response = client.put("/users/99999", json=update_data, headers=auth_headers)
        assert response.status_code == 404

    def test_delete_nonexistent_user(self, client, auth_headers):
        """Olmayan kullanıcı silme testi."""
        response = client.delete("/users/99999", headers=auth_headers)
        assert response.status_code == 404


@pytest.mark.auth
class TestStockEdgeCasesFixed:
    """Stok endpoint'leri için auth'lu edge case testleri."""

    def test_create_stock_negative_quantity(self, client, auth_headers):
        """Negatif miktarda stok oluşturma testi."""
        invalid_stock = {
            "product_name": "Negative Stock Test",
            "quantity": -10,
            "unit_price": 25.99,
            "supplier": "Test Supplier",
        }
        response = client.post("/stocks/", json=invalid_stock, headers=auth_headers)
        assert response.status_code == 422

    def test_create_stock_zero_price(self, client, auth_headers):
        """Sıfır fiyatlı stok oluşturma testi."""
        invalid_stock = {
            "product_name": "Zero Price Stock Test",
            "quantity": 50,
            "unit_price": 0,
            "supplier": "Test Supplier",
        }
        response = client.post("/stocks/", json=invalid_stock, headers=auth_headers)
        assert response.status_code == 422

    def test_create_stock_empty_product_name(self, client, auth_headers):
        """Boş ürün adı ile stok oluşturma testi."""
        invalid_stock = {
            "product_name": "",
            "quantity": 50,
            "unit_price": 25.99,
            "supplier": "Test Supplier",
        }
        response = client.post("/stocks/", json=invalid_stock, headers=auth_headers)
        assert response.status_code == 422


@pytest.mark.auth
class TestOrderEdgeCasesFixed:
    """Sipariş endpoint'leri için auth'lu edge case testleri."""

    def test_create_order_negative_amount(self, client, auth_headers):
        """Negatif tutarlı sipariş oluşturma testi."""
        invalid_order = {
            "user_id": 1,
            "status": "pending",
            "total_amount": -100.0,
            "items": [
                {
                    "product_id": 1,
                    "quantity": 2,
                    "unit_price": -50.0,
                    "total_price": -100.0,
                }
            ],
        }
        response = client.post("/orders/", json=invalid_order, headers=auth_headers)
        assert response.status_code == 422


class TestUnauthenticatedAccess:
    """Yetkilendirme olmadan erişim testleri."""

    def test_users_without_auth(self, client):
        """Yetkilendirme olmadan kullanıcı listesi."""
        response = client.get("/users/")
        assert response.status_code == 401

    def test_create_user_without_auth(self, client):
        """Yetkilendirme olmadan kullanıcı oluşturma."""
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "role": "user",
            "is_active": True,
            "password": "test123",
        }
        response = client.post("/users/", json=user_data)
        assert response.status_code == 401

    def test_stocks_without_auth(self, client):
        """Yetkilendirme olmadan stok listesi."""
        response = client.get("/stocks/")
        assert response.status_code == 401

    def test_orders_without_auth(self, client):
        """Yetkilendirme olmadan sipariş listesi."""
        response = client.get("/orders/")
        assert response.status_code == 401


@pytest.mark.integration
class TestIntegrationWithAuth:
    """Auth ile entegrasyon testleri."""

    def test_full_user_crud_with_auth(self, client, auth_headers):
        """Auth ile tam kullanıcı CRUD testi."""
        # Create
        user_data = {
            "name": "Integration Test User",
            "email": f"integration-{uuid.uuid4()}@test.com",
            "role": "user",
            "is_active": True,
            "password": "test123",
        }
        create_response = client.post("/users/", json=user_data, headers=auth_headers)
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        # Read
        get_response = client.get(f"/users/{user_id}", headers=auth_headers)
        assert get_response.status_code == 200
        assert get_response.json()["name"] == user_data["name"]

        # Update
        update_data = {"name": "Updated Integration User"}
        update_response = client.put(
            f"/users/{user_id}", json=update_data, headers=auth_headers
        )
        assert update_response.status_code == 200
        assert update_response.json()["name"] == update_data["name"]

        # Delete
        delete_response = client.delete(f"/users/{user_id}", headers=auth_headers)
        assert delete_response.status_code == 204

        # Verify deletion
        verify_response = client.get(f"/users/{user_id}", headers=auth_headers)
        assert verify_response.status_code == 404

    def test_full_stock_crud_with_auth(self, client, auth_headers):
        """Auth ile tam stok CRUD testi."""
        # Create
        stock_data = {
            "product_name": f"Integration Stock {uuid.uuid4()}",
            "quantity": 100,
            "unit_price": 25.99,
            "supplier": "Integration Supplier",
        }
        create_response = client.post("/stocks/", json=stock_data, headers=auth_headers)
        assert create_response.status_code == 201
        stock_id = create_response.json()["id"]

        # Read
        get_response = client.get(f"/stocks/{stock_id}", headers=auth_headers)
        assert get_response.status_code == 200
        assert get_response.json()["product_name"] == stock_data["product_name"]

        # Update
        update_data = {"quantity": 150}
        update_response = client.put(
            f"/stocks/{stock_id}", json=update_data, headers=auth_headers
        )
        assert update_response.status_code == 200
        assert update_response.json()["quantity"] == update_data["quantity"]

        # Delete
        delete_response = client.delete(f"/stocks/{stock_id}", headers=auth_headers)
        assert delete_response.status_code == 204

        # Verify deletion
        verify_response = client.get(f"/stocks/{stock_id}", headers=auth_headers)
        assert verify_response.status_code == 404
