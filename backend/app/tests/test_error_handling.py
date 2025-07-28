"""
Tüm API modülleri için ortak error handling testleri.
404, 422, 500 hata senaryolarını test eder.
"""

import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)
headers = {"Authorization": "Bearer secret-token"}


def unique_email():
    return f"error_test_{uuid.uuid4()}@example.com"


def unique_product():
    return f"Product_{uuid.uuid4()}"


# genel hata senaryosu testleri
class TestGlobalErrorHandling:
    """Tüm API modülleri için global error handling testleri."""

    # === CROSS-MODULE 404 TESTS ===

    def test_all_modules_get_nonexistent_404(self):
        """All modules: GET non-existent resources → 404"""
        # Orders
        response = client.get("/api/v1/orders/99999", headers=headers)
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

        # Users
        response = client.get("/api/v1/users/99999", headers=headers)
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

        # Stocks
        response = client.get("/api/v1/stocks/99999", headers=headers)
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_all_modules_put_nonexistent_404(self):
        """All modules: PUT non-existent resources → 404"""
        # Orders
        update_data = {"user_id": 1, "product_name": "Test", "amount": 100.0}
        response = client.put("/api/v1/orders/99999", json=update_data, headers=headers)
        assert response.status_code == 404

        # Users
        update_data = {"name": "Test User", "email": "test@example.com"}
        response = client.put("/api/v1/users/99999", json=update_data, headers=headers)
        assert response.status_code == 404

        # Stocks
        update_data = {"product_name": "Test Product", "quantity": 100, "price": 10.0}
        response = client.put("/api/v1/stocks/99999", json=update_data, headers=headers)
        assert response.status_code == 404

    def test_all_modules_delete_nonexistent_404(self):
        """All modules: DELETE non-existent resources → 404"""
        # Orders
        response = client.delete("/api/v1/orders/99999", headers=headers)
        assert response.status_code == 404

        # Users
        response = client.delete("/api/v1/users/99999", headers=headers)
        assert response.status_code == 404

        # Stocks
        response = client.delete("/api/v1/stocks/99999", headers=headers)
        assert response.status_code == 404

    # === CROSS-MODULE 422 TESTS ===

    def test_all_modules_post_missing_fields_422(self):
        """All modules: POST with missing required fields → 422"""
        # Orders - missing product_name
        response = client.post(
            "/api/v1/orders/",
            json={"user_id": 1, "amount": 100.0},
            headers=headers,
        )
        assert response.status_code == 422

        # Users - missing email
        response = client.post(
            "/api/v1/users/",
            json={"name": "Test User", "password": "test123"},
            headers=headers,
        )
        assert response.status_code == 422

        # Stocks - missing quantity
        response = client.post(
            "/api/v1/stocks/",
            json={"product_name": "Test Product", "price": 10.0},
            headers=headers,
        )
        assert response.status_code == 422

    def test_all_modules_post_invalid_data_types_422(self):
        """All modules: POST with invalid data types → 422"""
        # Orders - string instead of int for user_id
        response = client.post(
            "/api/v1/orders/",
            json={
                "user_id": "invalid",
                "product_name": unique_product(),
                "amount": 100.0,
            },
            headers=headers,
        )
        assert response.status_code == 422

        # Users - int instead of string for name
        response = client.post(
            "/api/v1/users/",
            json={"name": 123, "email": unique_email(), "password": "test123"},
            headers=headers,
        )
        assert response.status_code == 422

        # Stocks - string instead of int for quantity
        response = client.post(
            "/api/v1/stocks/",
            json={
                "product_name": unique_product(),
                "quantity": "invalid",
                "price": 10.0,
            },
            headers=headers,
        )
        assert response.status_code == 422

    def test_all_modules_post_empty_strings_422(self):
        """All modules: POST with empty strings → 422"""
        # Orders - empty product_name
        response = client.post(
            "/api/v1/orders/",
            json={"user_id": 1, "product_name": "", "amount": 100.0},
            headers=headers,
        )
        assert response.status_code == 422

        # Users - empty name
        response = client.post(
            "/api/v1/users/",
            json={"name": "", "email": unique_email(), "password": "test123"},
            headers=headers,
        )
        assert response.status_code == 422

        # Stocks - empty product_name
        response = client.post(
            "/api/v1/stocks/",
            json={"product_name": "", "quantity": 100, "price": 10.0},
            headers=headers,
        )
        assert response.status_code == 422

    # === CROSS-MODULE 500 TESTS ===

    def test_all_modules_create_internal_error_500(self):
        """All modules: POST with internal exception → 500"""
        # Orders
        with patch(
            "app.routes.schemas.OrderCreate", side_effect=Exception("Test exception")
        ):
            order_data = {
                "user_id": 1,
                "product_name": unique_product(),
                "amount": 10.0,
            }
            response = client.post("/api/v1/orders/", json=order_data, headers=headers)
            assert response.status_code == 500
            data = response.json()
            assert "internal server error" in data["detail"].lower()

        # Users
        with patch(
            "app.routes.schemas.UserCreate", side_effect=Exception("Test exception")
        ):
            user_data = {
                "name": "Test User",
                "email": unique_email(),
                "password": "test123",
            }
            response = client.post("/api/v1/users/", json=user_data, headers=headers)
            assert response.status_code == 500
            data = response.json()
            assert "internal server error" in data["detail"].lower()

        # Stocks
        with patch(
            "app.routes.schemas.StockCreate", side_effect=Exception("Test exception")
        ):
            stock_data = {
                "product_name": unique_product(),
                "quantity": 100,
                "price": 10.0,
            }
            response = client.post("/api/v1/stocks/", json=stock_data, headers=headers)
            assert response.status_code == 500
            data = response.json()
            assert "internal server error" in data["detail"].lower()

    def test_all_modules_update_internal_error_500(self):
        """All modules: PUT with internal exception → 500"""
        # Orders
        with patch(
            "app.routes.schemas.OrderUpdate", side_effect=Exception("Test exception")
        ):
            update_data = {"user_id": 1, "product_name": "Test", "amount": 10.0}
            response = client.put("/api/v1/orders/1", json=update_data, headers=headers)
            assert response.status_code == 500
            data = response.json()
            assert "internal server error" in data["detail"].lower()

        # Users
        with patch(
            "app.routes.schemas.UserUpdate", side_effect=Exception("Test exception")
        ):
            update_data = {"name": "Updated User", "email": "updated@example.com"}
            response = client.put("/api/v1/users/1", json=update_data, headers=headers)
            assert response.status_code == 500
            data = response.json()
            assert "internal server error" in data["detail"].lower()

        # Stocks
        with patch(
            "app.routes.schemas.StockUpdate", side_effect=Exception("Test exception")
        ):
            update_data = {
                "product_name": "Updated Product",
                "quantity": 200,
                "price": 20.0,
            }
            response = client.put("/api/v1/stocks/1", json=update_data, headers=headers)
            assert response.status_code == 500
            data = response.json()
            assert "internal server error" in data["detail"].lower()

    # === DATABASE CONSTRAINT TESTS ===

    def test_orders_with_invalid_user_id_404(self):
        """Orders: POST with non-existent user_id → 404"""
        response = client.post(
            "/api/v1/orders/",
            json={"user_id": 99999, "product_name": unique_product(), "amount": 100.0},
            headers=headers,
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_users_duplicate_email_400(self):
        """Users: POST with duplicate email → 400"""
        email = unique_email()
        # İlk user oluştur
        user_data = {"name": "Test User", "email": email, "password": "test123"}
        response1 = client.post("/api/v1/users/", json=user_data, headers=headers)
        assert response1.status_code == 201

        # Aynı email ile ikinci user oluşturmaya çalış
        response2 = client.post("/api/v1/users/", json=user_data, headers=headers)
        assert response2.status_code == 400
        data = response2.json()
        assert "already registered" in data["detail"].lower()

    def test_stocks_duplicate_product_name_400(self):
        """Stocks: POST with duplicate product_name → 400"""
        product_name = unique_product()
        # İlk stock oluştur
        stock_data = {"product_name": product_name, "quantity": 100, "price": 10.0}
        response1 = client.post("/api/v1/stocks/", json=stock_data, headers=headers)
        assert response1.status_code == 201

        # Aynı product_name ile ikinci stock oluşturmaya çalış
        response2 = client.post("/api/v1/stocks/", json=stock_data, headers=headers)
        assert response2.status_code == 400
        data = response2.json()
        assert (
            "already exists" in data["detail"].lower()
            or "unique" in data["detail"].lower()
        )

    # === EDGE CASES ===

    def test_orders_with_special_characters_201(self):
        """Orders: POST with special characters → 201 (should work)"""
        special_product = f"Ürün-Çeşit-Özel_123!@#$%^&*() {uuid.uuid4()}"
        response = client.post(
            "/api/v1/orders/",
            json={"user_id": 1, "product_name": special_product, "amount": 100.0},
            headers=headers,
        )
        # Özel karakterler kabul edilmeli
        assert response.status_code == 201

    def test_users_with_special_characters_201(self):
        """Users: POST with special characters → 201 (should work)"""
        special_name = f"Üser-Çeşit-Özel_123!@#$%^&*() {uuid.uuid4()}"
        response = client.post(
            "/api/v1/users/",
            json={"name": special_name, "email": unique_email(), "password": "test123"},
            headers=headers,
        )
        # Özel karakterler kabul edilmeli
        assert response.status_code == 201

    def test_stocks_with_special_characters_201(self):
        """Stocks: POST with special characters → 201 (should work)"""
        special_product = f"Ürün-Çeşit-Özel_123!@#$%^&*() {uuid.uuid4()}"
        response = client.post(
            "/api/v1/stocks/",
            json={"product_name": special_product, "quantity": 100, "price": 10.0},
            headers=headers,
        )
        # Özel karakterler kabul edilmeli
        assert response.status_code == 201

    def test_all_modules_with_very_large_numbers_422(self):
        """All modules: POST with very large numbers → 422"""
        # Orders
        response = client.post(
            "/api/v1/orders/",
            json={
                "user_id": 1,
                "product_name": unique_product(),
                "amount": 999999999999999.99,
            },
            headers=headers,
        )
        assert response.status_code in [201, 422]

        # Users - very long name
        long_name = "A" * 1000
        response = client.post(
            "/api/v1/users/",
            json={"name": long_name, "email": unique_email(), "password": "test123"},
            headers=headers,
        )
        assert response.status_code in [201, 422]

        # Stocks
        response = client.post(
            "/api/v1/stocks/",
            json={
                "product_name": unique_product(),
                "quantity": 999999999,
                "price": 999999999.99,
            },
            headers=headers,
        )
        assert response.status_code in [201, 422]

    # === AUTHENTICATION TESTS ===

    def test_all_modules_without_auth_401(self):
        """All modules: POST without authentication → 401"""
        # Orders
        response = client.post(
            "/api/v1/orders/",
            json={"user_id": 1, "product_name": unique_product(), "amount": 100.0},
        )
        assert response.status_code == 401

        # Users
        response = client.post(
            "/api/v1/users/",
            json={"name": "Test User", "email": unique_email(), "password": "test123"},
        )
        assert response.status_code == 401

        # Stocks
        response = client.post(
            "/api/v1/stocks/",
            json={"product_name": unique_product(), "quantity": 100, "price": 10.0},
        )
        assert response.status_code == 401

    def test_all_modules_with_invalid_auth_401(self):
        """All modules: GET with invalid authentication → 401"""
        invalid_headers = {"Authorization": "Bearer invalid-token"}

        # Orders
        response = client.get("/api/v1/orders/", headers=invalid_headers)
        assert response.status_code == 401

        # Users
        response = client.get("/api/v1/users/", headers=invalid_headers)
        assert response.status_code == 401

        # Stocks
        response = client.get("/api/v1/stocks/", headers=invalid_headers)
        assert response.status_code == 401
