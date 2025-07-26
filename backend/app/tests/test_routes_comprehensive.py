"""
Routes Comprehensive Test Suite.
Tüm CRUD işlemleri, error handling ve edge case'leri kapsar.
"""

import pytest
import uuid
from unittest.mock import patch


class TestUserRoutesCRUD:
    """User routes CRUD testleri."""

    def test_create_user_success(self, client, auth_headers):
        """Başarılı kullanıcı oluşturma testi."""
        user_data = {
            "name": "Routes Test User",
            "email": f"routes-{uuid.uuid4()}@test.com",
            "role": "user",
            "is_active": True,
            "password": "secure123",
        }
        response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert "password_hash" in data
        assert data["name"] == user_data["name"]
        return data["id"]

    def test_create_user_duplicate_email(self, client, auth_headers):
        """Duplicate email ile kullanıcı oluşturma error testi."""
        email = f"duplicate-{uuid.uuid4()}@test.com"
        user_data = {
            "name": "First User",
            "email": email,
            "role": "user",
            "is_active": True,
            "password": "test123",
        }

        # İlk kullanıcı
        response1 = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
        assert response1.status_code == 201

        # Duplicate attempt
        user_data["name"] = "Second User"
        response2 = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
        assert response2.status_code in [400, 409]  # Constraint error

    def test_create_user_invalid_role(self, client, auth_headers):
        """Geçersiz role ile kullanıcı oluşturma testi."""
        user_data = {
            "name": "Invalid Role User",
            "email": f"invalid-{uuid.uuid4()}@test.com",
            "role": "invalid_role_name",
            "is_active": True,
            "password": "test123",
        }
        response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
        # Role validation varsa 422, yoksa 201 dönebilir
        assert response.status_code in [201, 422]

    def test_get_user_by_id_success(self, client, auth_headers, create_test_user):
        """Başarılı kullanıcı getirme testi."""
        if create_test_user:
            response = client.get(
                f"/api/v1/users/{create_test_user}", headers=auth_headers
            )
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == create_test_user
            assert "password_hash" not in data  # Password hash expose edilmemeli

    def test_get_user_by_id_not_found(self, client, auth_headers):
        """Olmayan kullanıcı getirme 404 testi."""
        response = client.get("/api/v1/users/99999", headers=auth_headers)
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_update_user_success(self, client, auth_headers, create_test_user):
        """Başarılı kullanıcı güncelleme testi."""
        if create_test_user:
            update_data = {"name": "Updated Name", "role": "admin"}
            response = client.put(
                f"/api/v1/users/{create_test_user}",
                json=update_data,
                headers=auth_headers,
            )
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Updated Name"
            assert data["role"] == "admin"

    def test_update_user_not_found(self, client, auth_headers):
        """Olmayan kullanıcı güncelleme 404 testi."""
        update_data = {"name": "Non-existent User"}
        response = client.put(
            "/api/v1/users/99999", json=update_data, headers=auth_headers
        )
        assert response.status_code == 404

    def test_delete_user_success(self, client, auth_headers):
        """Başarılı kullanıcı silme testi."""
        # Önce kullanıcı oluştur
        user_data = {
            "name": "Delete Test User",
            "email": f"delete-{uuid.uuid4()}@test.com",
            "role": "user",
            "is_active": True,
            "password": "test123",
        }
        create_response = client.post(
            "/api/v1/users/", json=user_data, headers=auth_headers
        )
        user_id = create_response.json()["id"]

        # Sil
        response = client.delete(f"/api/v1/users/{user_id}", headers=auth_headers)
        assert response.status_code == 204

        # Silindi kontrolü
        get_response = client.get(f"/api/v1/users/{user_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_user_not_found(self, client, auth_headers):
        """Olmayan kullanıcı silme 404 testi."""
        response = client.delete("/api/v1/users/99999", headers=auth_headers)
        assert response.status_code == 404


class TestStockRoutesCRUD:
    """Stock routes CRUD testleri."""

    def test_create_stock_success(self, client, auth_headers):
        """Başarılı stok oluşturma testi."""
        stock_data = {
            "product_name": f"Routes Test Product {uuid.uuid4()}",
            "quantity": 150,
            "unit_price": 45.99,
            "supplier": "Routes Test Supplier",
        }
        response = client.post("/api/v1/stocks/", json=stock_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["product_name"] == stock_data["product_name"]
        assert data["quantity"] == stock_data["quantity"]

    def test_create_stock_zero_quantity(self, client, auth_headers):
        """Sıfır quantity ile stok oluşturma testi."""
        stock_data = {
            "product_name": "Zero Quantity Stock",
            "quantity": 0,
            "unit_price": 25.99,
            "supplier": "Test Supplier",
        }
        response = client.post("/api/v1/stocks/", json=stock_data, headers=auth_headers)
        # Zero quantity allowed veya validation error
        assert response.status_code in [201, 422]

    def test_create_stock_missing_fields(self, client, auth_headers):
        """Eksik field'lar ile stok oluşturma testi."""
        incomplete_stock = {
            "product_name": "Incomplete Stock"
            # quantity, unit_price, supplier eksik
        }
        response = client.post(
            "/api/v1/stocks/", json=incomplete_stock, headers=auth_headers
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_update_stock_quantity(self, client, auth_headers, create_test_stock):
        """Stok miktarı güncelleme testi."""
        if create_test_stock:
            update_data = {"quantity": 250}
            response = client.put(
                f"/api/v1/stocks/{create_test_stock}",
                json=update_data,
                headers=auth_headers,
            )
            assert response.status_code == 200
            data = response.json()
            assert data["quantity"] == 250

    def test_update_stock_partial_fields(self, client, auth_headers, create_test_stock):
        """Partial field güncelleme testi."""
        if create_test_stock:
            update_data = {"supplier": "Updated Supplier", "unit_price": 99.99}
            response = client.put(
                f"/api/v1/stocks/{create_test_stock}",
                json=update_data,
                headers=auth_headers,
            )
            assert response.status_code == 200
            data = response.json()
            assert data["supplier"] == "Updated Supplier"
            assert data["unit_price"] == 99.99


class TestOrderRoutesCRUD:
    """Order routes CRUD testleri."""

    def test_create_order_basic(self, client, auth_headers):
        """Temel sipariş oluşturma testi."""
        order_data = {
            "user_id": 1,
            "total_amount": 199.99,
            "status": "pending",
            "order_items": [
                {
                    "product_id": 1,
                    "quantity": 2,
                    "unit_price": 99.995,
                    "total_price": 199.99,
                }
            ],
        }
        response = client.post("/api/v1/orders/", json=order_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["total_amount"] == order_data["total_amount"]
        assert data["status"] == "pending"

    def test_create_order_empty_items(self, client, auth_headers):
        """Boş item'lar ile sipariş oluşturma testi."""
        order_data = {
            "user_id": 1,
            "total_amount": 0.0,
            "status": "pending",
            "order_items": [],
        }
        response = client.post("/api/v1/orders/", json=order_data, headers=auth_headers)
        # Empty items allowed veya validation error
        assert response.status_code in [201, 422]

    def test_create_order_invalid_user(self, client, auth_headers):
        """Geçersiz user_id ile sipariş oluşturma testi."""
        order_data = {
            "user_id": 99999,  # Non-existent user
            "total_amount": 100.0,
            "status": "pending",
            "order_items": [],
        }
        response = client.post("/api/v1/orders/", json=order_data, headers=auth_headers)
        # Foreign key constraint veya validation
        assert response.status_code in [201, 400, 422]

    def test_update_order_status(self, client, auth_headers):
        """Sipariş durumu güncelleme testi."""
        # Önce sipariş oluştur
        order_data = {
            "user_id": 1,
            "total_amount": 50.0,
            "status": "pending",
            "order_items": [],
        }
        create_response = client.post(
            "/api/v1/orders/", json=order_data, headers=auth_headers
        )
        if create_response.status_code == 201:
            order_id = create_response.json()["id"]

            # Status güncelle
            update_data = {"status": "completed"}
            response = client.put(
                f"/api/v1/orders/{order_id}", json=update_data, headers=auth_headers
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "completed"

    def test_get_orders_list(self, client, auth_headers):
        """Sipariş listesi getirme testi."""
        response = client.get("/api/v1/orders/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestErrorHandling:
    """Error handling ve HTTP status code testleri."""

    def test_malformed_json(self, client, auth_headers):
        """Malformed JSON testi."""
        response = client.post(
            "/api/v1/users/",
            data="{'invalid': json}",
            headers={**auth_headers, "Content-Type": "application/json"},
        )
        assert response.status_code == 422

    def test_missing_content_type(self, client, auth_headers):
        """Content-Type eksik testi."""
        user_data = {"name": "Test", "email": "test@test.com"}
        headers_no_content = {
            k: v for k, v in auth_headers.items() if k != "Content-Type"
        }
        response = client.post(
            "/api/v1/users/", json=user_data, headers=headers_no_content
        )
        # FastAPI otomatik content-type handle eder
        assert response.status_code in [201, 400, 415]

    def test_oversized_payload(self, client, auth_headers):
        """Büyük payload testi."""
        large_name = "x" * 10000  # 10KB name
        user_data = {
            "name": large_name,
            "email": "large@test.com",
            "role": "user",
            "is_active": True,
            "password": "test123",
        }
        response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
        # Database constraint veya application limit
        assert response.status_code in [201, 400, 413, 422]

    def test_special_characters_injection(self, client, auth_headers):
        """SQL injection attempt testi."""
        malicious_data = {
            "name": "'; DROP TABLE users; --",
            "email": f"injection-{uuid.uuid4()}@test.com",
            "role": "user",
            "is_active": True,
            "password": "test123",
        }
        response = client.post(
            "/api/v1/users/", json=malicious_data, headers=auth_headers
        )
        # SQLAlchemy ORM korumalı olmalı
        assert response.status_code in [201, 400, 422]

    def test_unicode_characters(self, client, auth_headers):
        """Unicode karakter testi."""
        unicode_data = {
            "name": "测试用户 🚀 Ñandú Αλφα",
            "email": f"unicode-{uuid.uuid4()}@测试.com",
            "role": "user",
            "is_active": True,
            "password": "测试密码123",
        }
        response = client.post(
            "/api/v1/users/", json=unicode_data, headers=auth_headers
        )
        # Unicode support test
        assert response.status_code in [201, 400, 422]


class TestAuthenticationScenarios:
    """Authentication senaryoları testleri."""

    def test_missing_auth_header(self, client):
        """Auth header eksik testi."""
        response = client.get("/api/v1/users/")
        assert response.status_code == 403

    def test_invalid_auth_token(self, client):
        """Geçersiz auth token testi."""
        headers = {"Authorization": "Bearer invalid_token_123"}
        response = client.get("/api/v1/users/", headers=headers)
        assert response.status_code == 403

    def test_malformed_auth_header(self, client):
        """Malformed auth header testi."""
        headers = {"Authorization": "InvalidFormat token123"}
        response = client.get("/api/v1/users/", headers=headers)
        assert response.status_code == 403

    def test_empty_auth_token(self, client):
        """Boş auth token testi."""
        headers = {"Authorization": "Bearer "}
        response = client.get("/api/v1/users/", headers=headers)
        assert response.status_code == 403


class TestDatabaseConstraints:
    """Database constraint testleri."""

    @patch("app.routes.SessionLocal")
    def test_database_connection_error(self, mock_session, client, auth_headers):
        """Database connection error testi."""
        mock_session.side_effect = Exception("Database connection failed")

        response = client.get("/api/v1/users/", headers=auth_headers)
        # Internal server error veya handled error
        assert response.status_code in [500, 503]

    def test_concurrent_user_creation(self, client, auth_headers):
        """Eşzamanlı kullanıcı oluşturma race condition testi."""
        email = f"concurrent-{uuid.uuid4()}@test.com"
        user_data = {
            "name": "Concurrent User",
            "email": email,
            "role": "user",
            "is_active": True,
            "password": "test123",
        }

        # Birden fazla request gönder
        import concurrent.futures

        def create_user():
            return client.post("/api/v1/users/", json=user_data, headers=auth_headers)

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(create_user) for _ in range(3)]
            responses = [f.result() for f in futures]

        # Sadece bir tanesi başarılı olmalı
        success_count = sum(1 for r in responses if r.status_code == 201)
        assert success_count == 1
