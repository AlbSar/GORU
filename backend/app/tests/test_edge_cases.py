"""
Edge case ve hata durumu testleri.
Beklenmedik durumlar ve hata yönetimini test eder.
"""

import uuid

import pytest


# Test client conftest.py'den alınacak


class TestUserEdgeCases:
    """Kullanıcı endpoint'leri için edge case testleri."""

    def test_create_user_invalid_email_format(self, client):
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

    def test_create_user_empty_name(self, client):
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

    def test_create_user_missing_required_fields(self, client):
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

    def test_get_nonexistent_user(self, client):
        """Olmayan kullanıcı getirme testi."""
        response = client.get("/api/v1/users/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_nonexistent_user(self, client):
        """Olmayan kullanıcı güncelleme testi."""
        update_data = {"name": "Updated Name"}
        response = client.put("/api/v1/users/99999", json=update_data)
        assert response.status_code == 404

    def test_delete_nonexistent_user(self, client):
        """Olmayan kullanıcı silme testi."""
        response = client.delete("/api/v1/users/99999")
        assert response.status_code == 404


class TestStockEdgeCases:
    """Stok endpoint'leri için edge case testleri."""

    def test_create_stock_negative_quantity(self, client):
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

    def test_create_stock_zero_price(self, client):
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

    def test_create_stock_empty_product_name(self, client):
        """Boş ürün adı ile stok oluşturma testi."""
        invalid_stock = {
            "product_name": "",
            "quantity": 50,
            "unit_price": 15.99,
            "supplier": "Test Supplier",
        }
        response = client.post("/api/v1/stocks/", json=invalid_stock)
        assert response.status_code == 422

    def test_create_stock_very_large_quantity(self, client):
        """Çok büyük miktarda stok oluşturma testi."""
        large_stock = {
            "product_name": "Large Quantity Stock",
            "quantity": 999999999,
            "unit_price": 0.01,
            "supplier": "Test Supplier",
        }
        response = client.post("/api/v1/stocks/", json=large_stock)
        # Bu durum geçerli olmalı, sadece veritabanı sınırları kontrol edilir
        assert response.status_code in [201, 422]


class TestOrderEdgeCases:
    """Sipariş endpoint'leri için edge case testleri."""

    def test_create_order_nonexistent_user(self, client):
        """Olmayan kullanıcı ile sipariş oluşturma testi."""
        invalid_order = {
            "user_id": 99999,
            "order_date": "2024-01-01",
            "total_amount": 100.00,
            "status": "pending",
            "order_items": [
                {
                    "product_name": "Test Product",
                    "quantity": 2,
                    "unit_price": 50.00,
                }
            ],
        }
        response = client.post("/api/v1/orders/", json=invalid_order)
        assert response.status_code in [400, 404, 422]

    def test_create_order_negative_amount(self, client):
        """Negatif tutarlı sipariş oluşturma testi."""
        invalid_order = {
            "user_id": 1,
            "order_date": "2024-01-01",
            "total_amount": -50.00,
            "status": "pending",
            "order_items": [],
        }
        response = client.post("/api/v1/orders/", json=invalid_order)
        assert response.status_code == 422
        assert "negative" in response.json()["detail"].lower()

    def test_create_order_empty_items(self, client):
        """Boş ürün listesi ile sipariş oluşturma testi."""
        order_without_items = {
            "user_id": 1,
            "order_date": "2024-01-01",
            "total_amount": 0.00,
            "status": "pending",
            "order_items": [],
        }
        response = client.post("/api/v1/orders/", json=order_without_items)
        # Bu durum geçerli olabilir
        assert response.status_code in [201, 422]


class TestAPILimitsAndValidation:
    """API limitleri ve validation testleri."""

    def test_very_long_string_fields(self, client):
        """Çok uzun string alanları testi."""
        long_name_user = {
            "name": "A" * 1000,  # Çok uzun isim
            "email": f"long-name-{uuid.uuid4()}@test.com",
            "role": "user",
            "is_active": True,
            "password": "test123",
        }
        response = client.post("/api/v1/users/", json=long_name_user)
        assert response.status_code in [
            201,
            422,
        ]  # Validation veya başarılı olabilir

    def test_special_characters_in_fields(self, client):
        """Özel karakterler içeren alanlar testi."""
        special_char_user = {
            "name": "Test User 🎉",
            "email": f"special-{uuid.uuid4()}@test.com",
            "role": "user",
            "is_active": True,
            "password": "test123",
        }
        response = client.post("/api/v1/users/", json=special_char_user)
        assert response.status_code == 201  # Unicode karakterler desteklenmeli
        if response.status_code == 201:
            user_data = response.json()
            assert "🎉" in user_data["name"]

    def test_sql_injection_attempt(self, client):
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
    """Performans edge case testleri."""

    def test_bulk_user_creation(self, client):
        """Toplu kullanıcı oluşturma testi."""
        users_created = 0
        for i in range(10):  # 10 kullanıcı oluştur
            user_data = {
                "name": f"Bulk User {i}",
                "email": f"bulk-{i}-{uuid.uuid4()}@test.com",
                "role": "user",
                "is_active": True,
                "password": "test123",
            }
            response = client.post("/api/v1/users/", json=user_data)
            if response.status_code == 201:
                users_created += 1

        # En az bir kullanıcı oluşturulmuş olmalı
        assert users_created > 0

    def test_large_paginated_request(self, client):
        """Büyük sayfalanmış istek testi."""
        # Önce yeterli veri var mı kontrol et
        response = client.get("/api/v1/users/")
        assert response.status_code == 200

        # Büyük limit ile test
        large_limit_response = client.get("/api/v1/users/?limit=1000")
        assert large_limit_response.status_code in [
            200,
            422,
        ]  # Limit aşımı veya başarılı


class TestErrorHandling:
    """Hata yönetimi testleri."""

    def test_malformed_json_request(self, client):
        """Hatalı JSON formatı testi."""
        # Bu test client kısıtlamaları nedeniyle basit tutuluyor
        response = client.post("/api/v1/users/", data="not-json")
        assert response.status_code == 422

    def test_unsupported_http_method(self, client):
        """Desteklenmeyen HTTP metodu testi."""
        response = client.patch("/api/v1/users/1")  # PATCH desteklenmiyorsa
        assert response.status_code in [405, 422]  # Method Not Allowed

    def test_invalid_content_type(self, client):
        """Geçersiz content type testi."""
        # Bu test client kısıtlamaları nedeniyle basit tutuluyor
        response = client.post("/api/v1/users/", data="not-json")
        assert response.status_code == 422
