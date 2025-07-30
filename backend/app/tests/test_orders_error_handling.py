"""
Orders modülü için error handling testleri.
404, 422, 500 hata senaryolarını test eder.
"""

import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


def generate_unique_product():
    return f"Product_{uuid.uuid4()}"


# genel hata senaryosu testleri
class TestOrdersErrorHandling:
    """Orders modülü için error handling testleri."""

    # === 404 NOT FOUND TESTS ===

    def test_get_nonexistent_order_404(self, client, auth_headers):
        """GET non-existent order → 404"""
        response = client.get("/orders/99999", headers=auth_headers)
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_put_nonexistent_order_404(self, client, auth_headers):
        """PUT non-existent order → 404"""
        update_data = {"user_id": 1, "product_name": "Test", "amount": 100.0}
        response = client.put("/orders/99999", json=update_data, headers=auth_headers)
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_delete_nonexistent_order_404(self, client, auth_headers):
        """DELETE non-existent order → 404"""
        response = client.delete("/orders/99999", headers=auth_headers)
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    # === 422 UNPROCESSABLE ENTITY TESTS ===

    def test_post_missing_required_fields_422(self, client, auth_headers):
        """POST with missing required fields → 422"""
        # Eksik product_name - API bunu 422 döndürür çünkü schema validation
        response = client.post(
            "/orders/",
            json={"user_id": 1, "amount": 100.0},
            headers=auth_headers,
        )
        # API raw dict alıyor ve schema validation yapıyor
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_post_missing_user_id_422(self, client, auth_headers):
        """POST with missing user_id → 422"""
        response = client.post(
            "/orders/",
            json={"product_name": "Test Product", "amount": 100.0},
            headers=auth_headers,
        )
        # API raw dict alıyor, KeyError fırlatır
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_post_missing_amount_422(self, client, auth_headers):
        """POST with missing amount → 422"""
        response = client.post(
            "/orders/",
            json={"user_id": 1, "product_name": "Test Product"},
            headers=auth_headers,
        )
        # API raw dict alıyor ve schema validation yapıyor
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_post_invalid_data_types_422(self, client, auth_headers, create_test_user):
        """POST with wrong data types → 422"""
        user_id = create_test_user["id"]
        response = client.post(
            "/orders/",
            json={
                "user_id": user_id,
                "product_name": generate_unique_product(),
                "amount": "invalid",
            },
            headers=auth_headers,
        )
        # API amount'u float'a çevirmeye çalışır, başarısız olur
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_post_empty_strings_201(self, client, auth_headers, create_test_user):
        """POST with empty strings → 201 (API kabul ediyor)"""
        user_id = create_test_user["id"]
        response = client.post(
            "/orders/",
            json={"user_id": user_id, "product_name": "", "amount": 100.0},
            headers=auth_headers,
        )
        # API boş string'leri kabul ediyor
        assert response.status_code == 201

    def test_put_invalid_data_422(self, client, auth_headers, create_test_user):
        """PUT with invalid data → 422"""
        # Önce geçerli order oluştur
        user_id = create_test_user
        if user_id:
            order_resp = client.post(
                "/orders/",
                json={
                    "user_id": user_id,
                    "product_name": generate_unique_product(),
                    "amount": 10.0,
                },
                headers=auth_headers,
            )
            order_id = order_resp.json()["id"]

            # Negatif amount ile güncelle
            update_data = {"user_id": user_id, "product_name": "Test", "amount": -10.0}
            response = client.put(
                f"/orders/{order_id}", json=update_data, headers=auth_headers
            )
            assert response.status_code == 422
            data = response.json()
            assert "detail" in data

    def test_post_with_invalid_user_id_404(self, client, auth_headers):
        """POST with non-existent user_id → 404"""
        response = client.post(
            "/orders/",
            json={
                "user_id": 99999,
                "product_name": generate_unique_product(),
                "amount": 100.0,
            },
            headers=auth_headers,
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    # === 500 INTERNAL SERVER ERROR TESTS ===

    def test_create_order_internal_error_500(
        self, client, auth_headers, create_test_user
    ):
        """POST with internal exception → 500"""
        user_id = create_test_user["id"]
        with patch("app.models.Order") as mock_order:
            mock_order.side_effect = Exception("Internal server error")
            order_data = {
                "user_id": user_id,
                "product_name": generate_unique_product(),
                "amount": 10.0,
            }
            response = client.post("/orders/", json=order_data, headers=auth_headers)
            assert response.status_code == 500
            data = response.json()
            assert "database error" in data["detail"].lower()

    def test_update_order_internal_error_500(
        self, client, auth_headers, create_test_user
    ):
        """PUT with internal exception → 500"""
        # Önce geçerli order oluştur
        user_id = create_test_user
        if user_id:
            order_resp = client.post(
                "/orders/",
                json={
                    "user_id": user_id,
                    "product_name": generate_unique_product(),
                    "amount": 10.0,
                },
                headers=auth_headers,
            )
            order_id = order_resp.json()["id"]

            # OrderUpdate schema'sı yok, bu yüzden farklı bir mock kullanıyoruz
            with patch("app.models.Order", side_effect=Exception("Test exception")):
                update_data = {
                    "user_id": user_id,
                    "product_name": "Test",
                    "amount": 10.0,
                }
                response = client.put(
                    f"/orders/{order_id}", json=update_data, headers=auth_headers
                )
                assert response.status_code == 500
                data = response.json()
                assert "database error" in data["detail"].lower()

    def test_create_order_database_error_500(
        self, client, auth_headers, create_test_user
    ):
        """POST with database exception → 500"""
        user_id = create_test_user["id"]
        with patch("sqlalchemy.orm.Session.commit") as mock_commit:
            mock_commit.side_effect = Exception("Database connection failed")
            order_data = {
                "user_id": user_id,
                "product_name": generate_unique_product(),
                "amount": 10.0,
            }
            response = client.post("/orders/", json=order_data, headers=auth_headers)
            assert response.status_code == 500
            data = response.json()
            assert "database error" in data["detail"].lower()

    # === EDGE CASES ===

    def test_post_with_very_large_numbers_201(
        self, client, auth_headers, create_test_user
    ):
        """POST with very large numbers → 201 (API kabul ediyor)"""
        user_id = create_test_user["id"]
        response = client.post(
            "/orders/",
            json={
                "user_id": user_id,
                "product_name": generate_unique_product(),
                "amount": 999999999999999.99,
            },
            headers=auth_headers,
        )
        # API büyük sayıları kabul ediyor
        assert response.status_code == 201

    def test_post_with_special_characters_201(
        self, client, auth_headers, create_test_user
    ):
        """POST with special characters → 201 (should work)"""
        user_id = create_test_user["id"]
        special_product = f"Ürün-Çeşit-Özel_123!@#$%^&*() {uuid.uuid4()}"
        response = client.post(
            "/orders/",
            json={"user_id": user_id, "product_name": special_product, "amount": 100.0},
            headers=auth_headers,
        )
        # Özel karakterler kabul edilmeli
        assert response.status_code == 201

    def test_post_with_very_long_strings_201(
        self, client, auth_headers, create_test_user
    ):
        """POST with very long strings → 201 (API kabul ediyor)"""
        user_id = create_test_user["id"]
        long_string = "A" * 1000  # 1000 karakterlik string
        response = client.post(
            "/orders/",
            json={"user_id": user_id, "product_name": long_string, "amount": 100.0},
            headers=auth_headers,
        )
        # API uzun stringleri kabul ediyor
        assert response.status_code == 201
