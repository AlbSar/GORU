"""
Stok endpoint'leri için test modülü.
"""

import uuid
from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


class TestStocksWithAuth:
    """Auth token'lı stok testleri."""

    def test_create_stock(self, client, auth_headers):
        """Stok oluşturma testi."""
        stock_data = {
            "product_name": f"Test Product {uuid.uuid4()}",
            "quantity": 100,
            "unit_price": 25.99,
            "supplier": "Test Supplier",
        }
        response = client.post(
            "/api/v1/stocks/", json=stock_data, headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["product_name"] == stock_data["product_name"]
        assert data["quantity"] == stock_data["quantity"]
        assert "id" in data

    def test_get_stocks(self, client, auth_headers):
        """Stok listesi getirme testi."""
        response = client.get("/api/v1/stocks/", headers=auth_headers)
        assert response.status_code == 200
        stocks = response.json()
        assert isinstance(stocks, list)

    def test_get_stock_by_id(self, client, auth_headers, create_test_stock):
        """ID'ye göre stok getirme testi."""
        if create_test_stock:
            response = client.get(
                f"/api/v1/stocks/{create_test_stock}", headers=auth_headers
            )
            assert response.status_code == 200
            stock = response.json()
            assert stock["id"] == create_test_stock

    def test_update_stock(self, client, auth_headers, create_test_stock):
        """Stok güncelleme testi."""
        if create_test_stock:
            update_data = {"quantity": 200}
            response = client.put(
                f"/api/v1/stocks/{create_test_stock}",
                json=update_data,
                headers=auth_headers,
            )
            assert response.status_code == 200
            updated_stock = response.json()
            assert updated_stock["quantity"] == 200

    def test_delete_stock(self, client, auth_headers):
        """Stok silme testi."""
        # Önce bir stok oluştur
        stock_data = {
            "product_name": f"Delete Test Stock {uuid.uuid4()}",
            "quantity": 50,
            "unit_price": 15.99,
            "supplier": "Delete Test Supplier",
        }
        create_response = client.post(
            "/api/v1/stocks/", json=stock_data, headers=auth_headers
        )
        assert create_response.status_code == 201
        stock_id = create_response.json()["id"]

        # Sonra sil
        delete_response = client.delete(
            f"/api/v1/stocks/{stock_id}", headers=auth_headers
        )
        assert delete_response.status_code == 204

        # Silindiğini kontrol et
        get_response = client.get(
            f"/api/v1/stocks/{stock_id}", headers=auth_headers
        )
        assert get_response.status_code == 404


class TestStocksValidation:
    """Stok validasyon testleri."""

    def test_create_stock_negative_quantity(self, client, auth_headers):
        """Negatif miktar ile stok oluşturma testi."""
        stock_data = {
            "product_name": "Negative Stock",
            "quantity": -10,
            "unit_price": 25.99,
            "supplier": "Test Supplier",
        }
        response = client.post(
            "/api/v1/stocks/", json=stock_data, headers=auth_headers
        )
        assert response.status_code == 422

    def test_create_stock_empty_product_name(self, client, auth_headers):
        """Boş ürün adı ile stok oluşturma testi."""
        stock_data = {
            "product_name": "",
            "quantity": 10,
            "unit_price": 25.99,
            "supplier": "Test Supplier",
        }
        response = client.post(
            "/api/v1/stocks/", json=stock_data, headers=auth_headers
        )
        assert response.status_code == 422

    def test_create_stock_missing_fields(self, client, auth_headers):
        """Eksik alan testi."""
        stock_data = {
            "product_name": "Incomplete Stock"
            # quantity, unit_price, supplier eksik
        }
        response = client.post(
            "/api/v1/stocks/", json=stock_data, headers=auth_headers
        )
        assert response.status_code == 422

    def test_get_nonexistent_stock(self, client, auth_headers):
        """Olmayan stok getirme testi."""
        response = client.get("/api/v1/stocks/99999", headers=auth_headers)
        assert response.status_code == 404


class TestStocksUnauthorized:
    """Yetkilendirme testleri."""

    def test_get_stocks_without_auth(self, client):
        """Yetkilendirme olmadan stok listesi."""
        response = client.get("/api/v1/stocks/")
        assert response.status_code == 403

    def test_create_stock_without_auth(self, client):
        """Yetkilendirme olmadan stok oluşturma."""
        stock_data = {
            "product_name": "Test Stock",
            "quantity": 100,
            "unit_price": 25.99,
            "supplier": "Test Supplier",
        }
        response = client.post("/api/v1/stocks/", json=stock_data)
        assert response.status_code == 403
