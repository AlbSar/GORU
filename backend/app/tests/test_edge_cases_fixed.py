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
        response = client.post(
            "/api/v1/users/", json=invalid_user, headers=auth_headers
        )
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
        response = client.post(
            "/api/v1/users/", json=invalid_user, headers=auth_headers
        )
        assert response.status_code == 422

    def test_create_user_missing_required_fields(self, client, auth_headers):
        """Gerekli alanları eksik kullanıcı oluşturma testi."""
        incomplete_user = {
            "name": "Test User"
            # email, role, password eksik
        }
        response = client.post(
            "/api/v1/users/", json=incomplete_user, headers=auth_headers
        )
        assert response.status_code == 422

        error_detail = response.json()["detail"]
        required_fields = ["email", "role", "password"]
        for field in required_fields:
            assert any(field in str(error) for error in error_detail)

    def test_get_nonexistent_user(self, client, auth_headers):
        """Olmayan kullanıcı getirme testi."""
        response = client.get("/api/v1/users/99999", headers=auth_headers)
        assert response.status_code == 404
        # Response format kontrolü - detail alanı olmalı
        response_data = response.json()
        assert "detail" in response_data
        # Türkçe veya İngilizce hata mesajı kontrolü
        detail_text = response_data["detail"].lower()
        assert any(keyword in detail_text for keyword in ["not found", "bulunamadı", "user"])

    def test_update_nonexistent_user(self, client, auth_headers):
        """Olmayan kullanıcı güncelleme testi."""
        update_data = {"name": "Updated Name"}
        response = client.put(
            "/api/v1/users/99999", json=update_data, headers=auth_headers
        )
        assert response.status_code == 404

    def test_delete_nonexistent_user(self, client, auth_headers):
        """Olmayan kullanıcı silme testi."""
        response = client.delete("/api/v1/users/99999", headers=auth_headers)
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
        response = client.post(
            "/api/v1/stocks/", json=invalid_stock, headers=auth_headers
        )
        assert response.status_code == 422
        # Response format kontrolü
        response_data = response.json()
        assert "detail" in response_data
        # Validation error kontrolü
        detail_text = str(response_data["detail"]).lower()
        assert any(keyword in detail_text for keyword in ["quantity", "negative", "greater"])

    def test_create_stock_zero_price(self, client, auth_headers):
        """Sıfır fiyatlı stok oluşturma testi."""
        zero_price_stock = {
            "product_name": "Zero Price Stock",
            "quantity": 100,
            "unit_price": 0.0,
            "supplier": "Test Supplier",
        }
        response = client.post(
            "/api/v1/stocks/", json=zero_price_stock, headers=auth_headers
        )
        # Bu durum geçerli olabilir (ücretsiz ürünler için)
        assert response.status_code in [201, 422]

    def test_create_stock_empty_product_name(self, client, auth_headers):
        """Boş ürün adı ile stok oluşturma testi."""
        invalid_stock = {
            "product_name": "",
            "quantity": 10,
            "unit_price": 25.99,
            "supplier": "Test Supplier",
        }
        response = client.post(
            "/api/v1/stocks/", json=invalid_stock, headers=auth_headers
        )
        assert response.status_code == 422


@pytest.mark.auth
class TestOrderEdgeCasesFixed:
    """Sipariş endpoint'leri için auth'lu edge case testleri."""

    def test_create_order_negative_amount(self, client, auth_headers):
        """Negatif tutarlı sipariş oluşturma testi."""
        invalid_order = {
            "user_id": 1,
            "total_amount": -150.0,
            "status": "pending",
            "order_items": [],
        }
        response = client.post(
            "/api/v1/orders/", json=invalid_order, headers=auth_headers
        )
        assert response.status_code == 422
        # Response format kontrolü
        response_data = response.json()
        assert "detail" in response_data
        # Validation error kontrolü
        detail_text = response_data["detail"].lower()
        assert any(keyword in detail_text for keyword in ["negative", "amount", "greater"])


class TestUnauthenticatedAccess:
    """Auth olmadan endpoint erişim testleri."""

    def test_users_without_auth(self, client):
        """Token olmadan kullanıcı listesi erişimi."""
        response = client.get("/api/v1/users/")
        assert response.status_code == 403

    def test_create_user_without_auth(self, client):
        """Token olmadan kullanıcı oluşturma."""
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "role": "user",
            "is_active": True,
            "password": "test123",
        }
        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 403

    def test_stocks_without_auth(self, client):
        """Token olmadan stok listesi erişimi."""
        response = client.get("/api/v1/stocks/")
        assert response.status_code == 403

    def test_orders_without_auth(self, client):
        """Token olmadan sipariş listesi erişimi."""
        response = client.get("/api/v1/orders/")
        assert response.status_code == 403


@pytest.mark.integration
class TestIntegrationWithAuth:
    """Auth token'lı entegrasyon testleri."""

    def test_full_user_crud_with_auth(self, client, auth_headers):
        """Auth ile tam kullanıcı CRUD testi."""
        # CREATE
        user_data = {
            "name": "Integration Test User",
            "email": f"integration-{uuid.uuid4()}@test.com",
            "role": "user",
            "is_active": True,
            "password": "test123",
        }
        create_response = client.post(
            "/api/v1/users/", json=user_data, headers=auth_headers
        )
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        # READ
        read_response = client.get(f"/api/v1/users/{user_id}", headers=auth_headers)
        assert read_response.status_code == 200
        assert read_response.json()["name"] == user_data["name"]

        # UPDATE
        update_data = {"name": "Updated Integration User"}
        update_response = client.put(
            f"/api/v1/users/{user_id}", json=update_data, headers=auth_headers
        )
        assert update_response.status_code == 200
        assert update_response.json()["name"] == "Updated Integration User"

        # DELETE
        delete_response = client.delete(
            f"/api/v1/users/{user_id}", headers=auth_headers
        )
        assert delete_response.status_code == 204

        # Verify deletion
        get_deleted_response = client.get(
            f"/api/v1/users/{user_id}", headers=auth_headers
        )
        assert get_deleted_response.status_code == 404

    def test_full_stock_crud_with_auth(self, client, auth_headers):
        """Auth ile tam stok CRUD testi."""
        # CREATE
        stock_data = {
            "product_name": "Integration Test Stock",
            "quantity": 100,
            "unit_price": 25.99,
            "supplier": "Integration Supplier",
        }
        create_response = client.post(
            "/api/v1/stocks/", json=stock_data, headers=auth_headers
        )
        assert create_response.status_code == 201
        stock_id = create_response.json()["id"]

        # READ
        read_response = client.get(f"/api/v1/stocks/{stock_id}", headers=auth_headers)
        assert read_response.status_code == 200
        assert read_response.json()["product_name"] == stock_data["product_name"]

        # UPDATE
        update_data = {"quantity": 150}
        update_response = client.put(
            f"/api/v1/stocks/{stock_id}",
            json=update_data,
            headers=auth_headers,
        )
        assert update_response.status_code == 200
        assert update_response.json()["quantity"] == 150

        # DELETE
        delete_response = client.delete(
            f"/api/v1/stocks/{stock_id}", headers=auth_headers
        )
        assert delete_response.status_code == 204
