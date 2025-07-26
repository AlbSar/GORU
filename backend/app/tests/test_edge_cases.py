"""
Edge case ve hata durumu testleri.
Beklenmedik durumlar ve hata yönetimini test eder.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from ..main import app

# Test client conftest.py'den alınacak


class TestUserEdgeCases:
    """Kullanıcı endpoint'leri için edge case testleri."""

    def test_create_user_invalid_email_format(self):
        """Geçersiz e-posta formatı ile kullanıcı oluşturma testi."""
        invalid_user = {
            "name": "Test User",
            "email": "invalid-email-format",
            "role": "user",
            "is_active": True,
            "password": "test123",
        }
        response = client.post("/api/v1/users/", json=invalid_user)
        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("email" in str(error).lower() for error in error_detail)

    def test_create_user_empty_name(self):
        """Boş isim ile kullanıcı oluşturma testi."""
        invalid_user = {
            "name": "",
            "email": f"empty-name-{uuid.uuid4()}@test.com",
            "role": "user",
            "is_active": True,
            "password": "test123",
        }
        response = client.post("/api/v1/users/", json=invalid_user)
        assert response.status_code == 422

    def test_create_user_missing_required_fields(self):
        """Gerekli alanları eksik kullanıcı oluşturma testi."""
        incomplete_user = {
            "name": "Test User"
            # email, role, password eksik
        }
        response = client.post("/api/v1/users/", json=incomplete_user)
        assert response.status_code == 422

        error_detail = response.json()["detail"]
        required_fields = ["email", "role", "password"]
        for field in required_fields:
            assert any(field in str(error) for error in error_detail)

    def test_get_nonexistent_user(self):
        """Olmayan kullanıcı getirme testi."""
        response = client.get("/api/v1/users/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_nonexistent_user(self):
        """Olmayan kullanıcı güncelleme testi."""
        update_data = {"name": "Updated Name"}
        response = client.put("/api/v1/users/99999", json=update_data)
        assert response.status_code == 404

    def test_delete_nonexistent_user(self):
        """Olmayan kullanıcı silme testi."""
        response = client.delete("/api/v1/users/99999")
        assert response.status_code == 404


class TestStockEdgeCases:
    """Stok endpoint'leri için edge case testleri."""

    def test_create_stock_negative_quantity(self):
        """Negatif miktarda stok oluşturma testi."""
        invalid_stock = {
            "product_name": "Negative Stock Test",
            "quantity": -10,
            "unit_price": 25.99,
            "supplier": "Test Supplier",
        }
        response = client.post("/api/v1/stocks/", json=invalid_stock)
        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("quantity" in str(error).lower() for error in error_detail)

    def test_create_stock_zero_price(self):
        """Sıfır fiyatlı stok oluşturma testi."""
        zero_price_stock = {
            "product_name": "Zero Price Stock",
            "quantity": 100,
            "unit_price": 0.0,
            "supplier": "Test Supplier",
        }
        response = client.post("/api/v1/stocks/", json=zero_price_stock)
        # Bu durum geçerli olabilir (ücretsiz ürünler için)
        assert response.status_code in [201, 422]

    def test_create_stock_empty_product_name(self):
        """Boş ürün adı ile stok oluşturma testi."""
        invalid_stock = {
            "product_name": "",
            "quantity": 10,
            "unit_price": 25.99,
            "supplier": "Test Supplier",
        }
        response = client.post("/api/v1/stocks/", json=invalid_stock)
        assert response.status_code == 422

    def test_create_stock_very_large_quantity(self):
        """Çok büyük miktarda stok oluşturma testi."""
        large_stock = {
            "product_name": "Large Quantity Stock",
            "quantity": 999999999,
            "unit_price": 1.0,
            "supplier": "Test Supplier",
        }
        response = client.post("/api/v1/stocks/", json=large_stock)
        # Bu durum geçerli olmalı, sadece veritabanı sınırları kontrol edilir
        assert response.status_code in [201, 422]


class TestOrderEdgeCases:
    """Sipariş endpoint'leri için edge case testleri."""

    def test_create_order_nonexistent_user(self):
        """Olmayan kullanıcıya sipariş atama testi."""
        invalid_order = {
            "user_id": 99999,
            "total_amount": 150.0,
            "status": "pending",
            "order_items": [
                {
                    "product_id": 1,
                    "quantity": 2,
                    "unit_price": 50.0,
                    "total_price": 100.0,
                }
            ],
        }
        response = client.post("/api/v1/orders/", json=invalid_order)
        assert response.status_code in [400, 404, 422]

    def test_create_order_negative_amount(self):
        """Negatif tutarlı sipariş oluşturma testi."""
        invalid_order = {
            "user_id": 1,
            "total_amount": -150.0,
            "status": "pending",
            "order_items": [],
        }
        response = client.post("/api/v1/orders/", json=invalid_order)
        assert response.status_code == 422
        assert "negative" in response.json()["detail"].lower()

    def test_create_order_empty_items(self):
        """Boş items listesi ile sipariş oluşturma testi."""
        order_without_items = {
            "user_id": 1,
            "total_amount": 0.0,
            "status": "pending",
            "order_items": [],
        }
        response = client.post("/api/v1/orders/", json=order_without_items)
        # Bu durum geçerli olabilir
        assert response.status_code in [201, 422]


class TestAPILimitsAndValidation:
    """API limitleri ve validasyon testleri."""

    def test_very_long_string_fields(self):
        """Çok uzun string alanları testi."""
        very_long_name = "x" * 1000
        long_name_user = {
            "name": very_long_name,
            "email": f"long-name-{uuid.uuid4()}@test.com",
            "role": "user",
            "is_active": True,
            "password": "test123",
        }
        response = client.post("/api/v1/users/", json=long_name_user)
        assert response.status_code in [201, 422]  # Depends on field length limits

    def test_special_characters_in_fields(self):
        """Özel karakterler ile alan testi."""
        special_char_user = {
            "name": "Test User 特殊字符 🚀",
            "email": f"special-{uuid.uuid4()}@test.com",
            "role": "user",
            "is_active": True,
            "password": "test123",
        }
        response = client.post("/api/v1/users/", json=special_char_user)
        assert response.status_code == 201  # Unicode karakterler desteklenmeli
        if response.status_code == 201:
            user = response.json()
            assert "特殊字符" in user["name"]
            assert "🚀" in user["name"]

    def test_sql_injection_attempt(self):
        """SQL injection denemesi testi."""
        malicious_user = {
            "name": "'; DROP TABLE users; --",
            "email": f"malicious-{uuid.uuid4()}@test.com",
            "role": "user",
            "is_active": True,
            "password": "test123",
        }
        response = client.post("/api/v1/users/", json=malicious_user)
        # SQLAlchemy ORM kullandığımız için güvenli olmalı
        assert response.status_code == 201
        if response.status_code == 201:
            # Tablo silinmemiş olmalı, sonraki GET request çalışmalı
            users_response = client.get("/api/v1/users/")
            assert users_response.status_code == 200


@pytest.mark.slow
class TestPerformanceEdgeCases:
    """Performans ve yük testleri."""

    def test_bulk_user_creation(self):
        """Toplu kullanıcı oluşturma testi."""
        users_created = 0
        max_users = 20  # CI ortamı için düşük tutuyoruz

        for i in range(max_users):
            user_data = {
                "name": f"Bulk User {i}",
                "email": f"bulk-user-{i}-{uuid.uuid4()}@test.com",
                "role": "user",
                "is_active": True,
                "password": "test123",
            }
            response = client.post("/api/v1/users/", json=user_data)
            if response.status_code == 201:
                users_created += 1

        # En az %80'i başarılı olmalı
        assert users_created >= max_users * 0.8

    def test_large_paginated_request(self):
        """Büyük sayfalanmış istek testi."""
        # Önce yeterli veri var mı kontrol et
        response = client.get("/api/v1/users/")
        assert response.status_code == 200
        users = response.json()

        # Büyük limit ile test
        large_limit_response = client.get("/api/v1/users/?limit=1000")
        assert large_limit_response.status_code in [
            200,
            422,
        ]  # Limit kısıtlaması olabilir


class TestErrorHandling:
    """Hata yönetimi testleri."""

    def test_malformed_json_request(self):
        """Bozuk JSON ile istek testi."""
        # Bu test HTTP client seviyesinde yapılmalı
        import requests

        try:
            # Malformed JSON
            response = requests.post(
                "http://localhost:8000/api/v1/users/",
                data="{'invalid': json}",  # Bozuk JSON
                headers={"Content-Type": "application/json"},
            )
            assert response.status_code == 422
        except requests.exceptions.ConnectionError:
            # Test ortamında server çalışmıyor olabilir
            pytest.skip("Server is not running")

    def test_unsupported_http_method(self):
        """Desteklenmeyen HTTP metodu testi."""
        response = client.patch("/api/v1/users/1")  # PATCH desteklenmiyorsa
        assert response.status_code in [405, 422]  # Method Not Allowed

    def test_invalid_content_type(self):
        """Geçersiz content type testi."""
        # Bu test client kısıtlamaları nedeniyle basit tutuluyor
        response = client.post("/api/v1/users/", data="not-json")
        assert response.status_code == 422
