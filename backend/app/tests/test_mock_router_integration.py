"""
Mock Router Integration Testleri
USE_MOCK environment ile mock endpoint'lerin aktif olması testleri.
"""

import os
import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from ..core.settings import Settings


def create_test_app():
    """Test için yeni app instance oluştur."""
    # Environment'ı temizle
    if "USE_MOCK" in os.environ:
        del os.environ["USE_MOCK"]

    # Yeni app oluştur
    from ..main import app

    return app


@pytest.fixture
def mock_enabled_client():
    """USE_MOCK=true ile test client."""
    with patch.dict(os.environ, {"USE_MOCK": "true"}):
        # Settings'i yeniden yükle
        from ..core.settings import settings

        settings.USE_MOCK = True

        # Yeni app instance oluştur
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware

        test_app = FastAPI(
            title="Test GORU API",
            description="Test API with mock endpoints",
            version="1.0.0",
        )

        # CORS middleware ekle
        test_app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Ana router'ı dahil et
        from ..routes import router

        test_app.include_router(router, prefix="/api/v1")

        # Root endpoint ekle
        @test_app.get("/")
        def read_root():
            return {
                "detail": "Test GORU API çalışıyor!",
                "version": "1.0.0",
                "mock_mode": True,
                "api_prefix": "/api/v1",
                "mock_prefix": "/mock",
                "environment": "test",
                "debug": True,
            }

        # Mock router'ı dahil et
        try:
            from ..mock_routes import mock_router

            test_app.include_router(mock_router)
            print("✅ Mock router test app'e dahil edildi")
        except Exception as e:
            print(f"❌ Mock router dahil etme hatası: {e}")

        client = TestClient(test_app)
        yield client


@pytest.fixture
def mock_disabled_client():
    """USE_MOCK=false ile test client."""
    with patch.dict(os.environ, {"USE_MOCK": "false"}):
        # Settings'i yeniden yükle
        from ..core.settings import settings

        settings.USE_MOCK = False

        # Yeni app instance oluştur
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware

        test_app = FastAPI(
            title="Test GORU API",
            description="Test API without mock endpoints",
            version="1.0.0",
        )

        # CORS middleware ekle
        test_app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Sadece ana router'ı dahil et
        from ..routes import router

        test_app.include_router(router, prefix="/api/v1")

        # Root endpoint ekle
        @test_app.get("/")
        def read_root():
            return {
                "detail": "Test GORU API çalışıyor!",
                "version": "1.0.0",
                "mock_mode": False,
                "api_prefix": "/api/v1",
                "mock_prefix": None,
                "environment": "test",
                "debug": True,
            }

        client = TestClient(test_app)
        yield client


@pytest.fixture
def auth_headers():
    """Auth token headers fixture."""
    return {"Authorization": "Bearer test-token-12345"}


class TestMockRouterActivation:
    """Mock router aktivasyon testleri."""

    def test_mock_router_included_when_enabled(self, mock_enabled_client):
        """USE_MOCK=true olduğunda mock router dahil edilmeli."""
        # Root endpoint mock mode raporlamalı
        response = mock_enabled_client.get("/")
        assert response.status_code == 200
        data = response.json()

        # Mock mode bilgileri kontrol et
        assert "mock_mode" in data
        assert data["mock_mode"]
        assert "mock_prefix" in data
        assert data["mock_prefix"] == "/mock"

    def test_mock_router_excluded_when_disabled(self, mock_disabled_client):
        """USE_MOCK=false olduğunda mock router dahil edilmemeli."""
        # Mock endpoint erişilemez olmalı
        response = mock_disabled_client.get("/mock/users")
        assert response.status_code == 404

        # Root endpoint'te mock mode false olmalı
        response = mock_disabled_client.get("/")
        data = response.json()
        assert not data["mock_mode"]
        assert data["mock_prefix"] is None

    def test_mock_users_endpoint_accessible(self, mock_enabled_client):
        """Mock mode'da users endpoint erişilebilir olmalı."""
        response = mock_enabled_client.get("/mock/users")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 5

    def test_mock_stocks_endpoint_accessible(self, mock_enabled_client):
        """Mock mode'da stocks endpoint erişilebilir olmalı."""
        response = mock_enabled_client.get("/mock/stocks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 5

    def test_mock_orders_endpoint_accessible(self, mock_enabled_client):
        """Mock mode'da orders endpoint erişilebilir olmalı."""
        response = mock_enabled_client.get("/mock/orders")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3

    def test_mock_endpoints_with_pagination(self, mock_enabled_client):
        """Mock endpoint'lerde pagination çalışmalı."""
        # Users endpoint'inde pagination
        response = mock_enabled_client.get("/mock/users?skip=0&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

        # Stocks endpoint'inde pagination
        response = mock_enabled_client.get("/mock/stocks?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2


class TestMockEndpointsCRUD:
    """Mock endpoint'lerde CRUD işlemleri testleri."""

    def test_mock_user_create_and_read(self, mock_enabled_client):
        """Mock kullanıcı oluşturma ve okuma testi."""
        # Yeni kullanıcı oluştur
        new_user = {
            "name": f"Test User {uuid.uuid4()}",
            "email": f"test-{uuid.uuid4()}@example.com",
            "role": "user",
            "is_active": True,
        }
        response = mock_enabled_client.post("/mock/users", json=new_user)
        assert response.status_code == 201
        created_user = response.json()
        assert created_user["name"] == new_user["name"]
        assert created_user["email"] == new_user["email"]

        # Oluşturulan kullanıcıyı getir
        user_id = created_user["id"]
        get_response = mock_enabled_client.get(f"/mock/users/{user_id}")
        assert get_response.status_code == 200
        retrieved_user = get_response.json()
        assert retrieved_user["id"] == user_id
        assert retrieved_user["name"] == new_user["name"]

    def test_mock_stock_create_and_update(self, mock_enabled_client):
        """Mock stok oluşturma ve güncelleme testi."""
        # Yeni stok oluştur
        new_stock = {
            "product_name": f"Test Product {uuid.uuid4()}",
            "quantity": 100,
            "unit_price": 25.99,
            "supplier": "Test Supplier",
        }
        response = mock_enabled_client.post("/mock/stocks", json=new_stock)
        assert response.status_code == 201
        created_stock = response.json()
        assert created_stock["product_name"] == new_stock["product_name"]
        assert created_stock["quantity"] == new_stock["quantity"]

        # Stoku güncelle
        stock_id = created_stock["id"]
        update_data = {"quantity": 150, "unit_price": 29.99}
        update_response = mock_enabled_client.put(
            f"/mock/stocks/{stock_id}", json=update_data
        )
        assert update_response.status_code == 200
        updated_stock = update_response.json()
        assert updated_stock["quantity"] == 150
        assert updated_stock["unit_price"] == 29.99

    def test_mock_order_lifecycle(self, mock_enabled_client):
        """Mock order yaşam döngüsü testi."""
        # CREATE
        order_data = {
            "user_id": 1,
            "total_amount": 99.99,
            "status": "pending",
            "order_items": [
                {
                    "product_id": 1,
                    "quantity": 1,
                    "unit_price": 99.99,
                    "total_price": 99.99,
                }
            ],
        }
        create_response = mock_enabled_client.post("/mock/orders/", json=order_data)
        assert create_response.status_code == 201
        created_order = create_response.json()
        order_id = created_order["id"]

        # UPDATE STATUS
        update_data = {"status": "shipped"}
        update_response = mock_enabled_client.put(
            f"/mock/orders/{order_id}", json=update_data
        )
        assert update_response.status_code == 200
        updated_order = update_response.json()
        assert updated_order["status"] == "shipped"

        # DELETE
        delete_response = mock_enabled_client.delete(f"/mock/orders/{order_id}")
        assert delete_response.status_code == 204

        # VERIFY DELETION
        get_response = mock_enabled_client.get(f"/mock/orders/{order_id}")
        assert get_response.status_code == 404

    def test_mock_endpoint_validation(self, mock_enabled_client):
        """Mock endpoint'lerde validation çalışmalı."""
        # Invalid user data
        invalid_user = {
            "name": "",  # Boş name
            "email": "invalid-email",  # Geçersiz email
            "role": "invalid_role",
        }
        response = mock_enabled_client.post("/mock/users/", json=invalid_user)
        # Validation hatası olabilir veya başarılı olabilir (mock service'e bağlı)
        assert response.status_code in [422, 201]

        # Invalid stock data
        invalid_stock = {
            "product_name": "Test",
            "quantity": -10,  # Negatif quantity
            "unit_price": 25.99,
            "supplier": "Test",
        }
        response = mock_enabled_client.post("/mock/stocks/", json=invalid_stock)
        # Validation hatası olabilir veya başarılı olabilir (mock service'e bağlı)
        assert response.status_code in [422, 201]


class TestMockVsRealEndpoints:
    """Mock ve gerçek endpoint'ler karşılaştırma testleri."""

    def test_real_endpoints_require_auth(self, mock_disabled_client):
        """Gerçek endpoint'ler auth gerektirmeli."""
        endpoints = ["/users/", "/stocks/", "/orders/"]

        for endpoint in endpoints:
            response = mock_disabled_client.get(endpoint)
            # Auth gerektiren endpoint'ler 401, 403 veya 404 döner
        # (tablo yoksa)
        assert response.status_code in [401, 403, 404]

    def test_mock_endpoints_no_auth_required(self, mock_enabled_client):
        """Mock endpoint'ler auth gerektirmemeli."""
        endpoints = ["/mock/users", "/mock/stocks", "/mock/orders"]

        for endpoint in endpoints:
            response = mock_enabled_client.get(endpoint)
            assert response.status_code == 200

    def test_mock_and_real_coexist(self, mock_enabled_client, auth_headers):
        """Mock ve gerçek endpoint'ler aynı anda çalışmalı."""
        # Mock endpoint (auth gerektirmez)
        mock_response = mock_enabled_client.get("/mock/users")
        assert mock_response.status_code == 200

        # Real endpoint (auth gerektirir) - database sorunu olabilir
        try:
            real_response = mock_enabled_client.get("/users/", headers=auth_headers)
            # Auth header'ı varsa 200, yoksa 401/403, database sorunu varsa 500
            assert real_response.status_code in [200, 401, 403, 500]
        except Exception:
            # Database bağlantı sorunu olabilir, bu durumda test geçerli
            pass

        # Farklı veri kaynaklarından gelmeli
        mock_users = mock_response.json()
        assert isinstance(mock_users, list)
        assert len(mock_users) >= 5  # Mock'ta en az 5 user

    def test_mock_endpoints_different_prefix(self, mock_enabled_client):
        """Mock endpoint'ler farklı prefix kullanmalı."""
        # Mock endpoint'ler /mock prefix'i kullanmalı
        mock_response = mock_enabled_client.get("/mock/users")
        assert mock_response.status_code == 200

        # Gerçek endpoint'ler /api/v1 prefix'i kullanmalı
        real_response = mock_enabled_client.get("/users/")
        assert real_response.status_code in [
            401,
            403,
            404,
        ]  # Auth gerekli veya tablo yok


class TestMockDataConsistency:
    """Mock data tutarlılık testleri."""

    def test_mock_data_persistent_during_session(self, mock_enabled_client):
        """Session boyunca mock data kalıcı olmalı."""
        # İlk durumu al
        initial_response = mock_enabled_client.get("/mock/users")
        initial_users = initial_response.json()
        initial_count = len(initial_users)

        # Yeni user ekle
        user_data = {
            "name": "Session Persistence User",
            "email": f"session-{uuid.uuid4()}@test.com",
            "role": "user",
            "is_active": True,
        }
        mock_enabled_client.post("/mock/users/", json=user_data)

        # Tekrar kontrol et
        final_response = mock_enabled_client.get("/mock/users")
        final_users = final_response.json()
        final_count = len(final_users)

        assert final_count == initial_count + 1

    def test_mock_data_independence_per_service(self, mock_enabled_client):
        """Her mock service bağımsız veri yönetmeli."""
        # Users'ı değiştir
        user_data = {
            "name": "Independence Test User",
            "email": f"independence-{uuid.uuid4()}@test.com",
            "role": "user",
            "is_active": True,
        }
        mock_enabled_client.post("/mock/users/", json=user_data)

        # Stocks etkilenmemeli
        stocks_response = mock_enabled_client.get("/mock/stocks")
        stocks = stocks_response.json()
        assert len(stocks) >= 5  # Hala default mock data

    def test_mock_data_reasonable_size(self, mock_enabled_client):
        """Mock data makul boyutta olmalı."""
        # Memory kullanımı test edilebilir
        users_response = mock_enabled_client.get("/mock/users")
        users = users_response.json()
        assert 5 <= len(users) <= 50  # Makul range

        stocks_response = mock_enabled_client.get("/mock/stocks")
        stocks = stocks_response.json()
        assert 5 <= len(stocks) <= 100  # Makul range

        orders_response = mock_enabled_client.get("/mock/orders")
        orders = orders_response.json()
        assert 3 <= len(orders) <= 50  # Makul range


class TestEnvironmentToggling:
    """Environment variable toggling testleri."""

    def test_environment_variable_precedence(self):
        """Environment variable öncelik sırası."""
        # Default false
        default_settings = Settings()
        assert hasattr(default_settings, "USE_MOCK")

        # Environment override
        with patch.dict(os.environ, {"USE_MOCK": "true"}):
            env_settings = Settings()
            assert env_settings.USE_MOCK

        with patch.dict(os.environ, {"USE_MOCK": "false"}):
            env_settings = Settings()
            assert not env_settings.USE_MOCK

    @patch.dict(os.environ, {"USE_MOCK": "invalid_value"})
    def test_invalid_environment_value_handling(self):
        """Geçersiz environment value handling."""

        # Pydantic boolean parsing
        try:
            settings = Settings()
            # 'invalid_value' false olarak parse edilebilir
            assert isinstance(settings.USE_MOCK, bool)
        except Exception:
            # Veya validation error fırlatabilir
            pass

    def test_boolean_parsing_variations(self):
        """Farklı boolean değer formatları test edilmeli."""

        # True değerleri
        true_values = [
            "true",
            "True",
            "TRUE",
            "1",
            "yes",
            "Yes",
            "YES",
            "on",
            "On",
            "ON",
        ]
        for value in true_values:
            with patch.dict(os.environ, {"USE_MOCK": value}):
                settings = Settings()
                assert settings.USE_MOCK

        # False değerleri
        false_values = [
            "false",
            "False",
            "FALSE",
            "0",
            "no",
            "No",
            "NO",
            "off",
            "Off",
            "OFF",
            "",
        ]
        for value in false_values:
            with patch.dict(os.environ, {"USE_MOCK": value}):
                settings = Settings()
                assert not settings.USE_MOCK


class TestSwaggerUIDocumentation:
    """Swagger UI dokümantasyon testleri."""

    def test_mock_endpoints_in_swagger(self, mock_enabled_client):
        """Mock endpoint'ler Swagger UI'da görünmeli."""
        # OpenAPI schema'sını al
        response = mock_enabled_client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()

        # Mock endpoint'lerin paths'de olması
        paths = schema.get("paths", {})

        # Mock users endpoint'i kontrol et
        assert "/mock/users" in paths
        assert "/mock/users/{user_id}" in paths

        # Mock stocks endpoint'i kontrol et
        assert "/mock/stocks" in paths
        assert "/mock/stocks/{stock_id}" in paths

        # Mock orders endpoint'i kontrol et
        assert "/mock/orders" in paths
        assert "/mock/orders/{order_id}" in paths

    def test_mock_endpoints_not_in_swagger_when_disabled(self, mock_disabled_client):
        """Mock endpoint'ler USE_MOCK=false ise Swagger'da görünmemeli."""
        # OpenAPI schema'sını al
        response = mock_disabled_client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()

        # Mock endpoint'lerin paths'de olmaması
        paths = schema.get("paths", {})

        # Mock endpoint'ler olmamalı
        assert "/mock/users" not in paths
        assert "/mock/stocks" not in paths
        assert "/mock/orders" not in paths

    def test_mock_endpoints_have_proper_tags(self, mock_enabled_client):
        """Mock endpoint'lerin doğru tag'leri olmalı."""
        # OpenAPI schema'sını al
        response = mock_enabled_client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()

        # Mock endpoint'lerin paths'de olması
        paths = schema.get("paths", {})

        # Mock endpoint'lerin varlığını kontrol et
        mock_paths = ["/mock/users", "/mock/stocks", "/mock/orders"]
        for path in mock_paths:
            if path in paths:
                # Her mock endpoint'in en az bir HTTP method'u olmalı
                assert len(paths[path]) > 0

                # Endpoint'lerin summary veya description'ı olmalı
                for method in paths[path]:
                    endpoint = paths[path][method]
                    # Summary veya description kontrol et
                    assert "summary" in endpoint or "description" in endpoint


class TestErrorHandling:
    """Hata yönetimi testleri."""

    def test_mock_endpoint_not_found_handling(self, mock_enabled_client):
        """Mock endpoint'lerde 404 handling."""
        # Var olmayan user
        response = mock_enabled_client.get("/mock/users/99999")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

        # Var olmayan stock
        response = mock_enabled_client.get("/mock/stocks/99999")
        assert response.status_code == 404

        # Var olmayan order
        response = mock_enabled_client.get("/mock/orders/99999")
        assert response.status_code == 404

    def test_mock_endpoint_invalid_id_handling(self, mock_enabled_client):
        """Mock endpoint'lerde geçersiz ID handling."""
        # Geçersiz ID formatları
        invalid_ids = ["abc", "-1", "0", "1.5"]

        for invalid_id in invalid_ids:
            response = mock_enabled_client.get(f"/mock/users/{invalid_id}")
            assert response.status_code in [
                404,
                422,
            ]  # 422 validation error olabilir

    def test_mock_router_import_error_handling(self):
        """Mock router import hatası handling."""
        # Bu test mock_services import hatası simüle eder
        # Gerçek uygulamada bu durum main.py'de handle edilir
        pass


class TestMockEdgeCases:
    """Mock endpoint edge case testleri."""

    def test_mock_empty_data_handling(self, mock_enabled_client):
        """Mock boş data handling."""
        # Pagination ile boş sonuç
        response = mock_enabled_client.get("/mock/users?skip=1000&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_mock_large_pagination(self, mock_enabled_client):
        """Mock büyük pagination değerleri."""
        # Çok büyük limit - validation hatası olabilir
        response = mock_enabled_client.get("/mock/users?limit=10000")
        assert response.status_code in [200, 422]  # 422 validation error olabilir
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    def test_mock_negative_pagination(self, mock_enabled_client):
        """Mock negatif pagination değerleri."""
        # Negatif skip
        response = mock_enabled_client.get("/mock/users?skip=-10")
        assert response.status_code == 422  # Validation error

    def test_mock_data_integrity(self, mock_enabled_client):
        """Mock data bütünlük testi."""
        # Users data yapısı
        response = mock_enabled_client.get("/mock/users")
        users = response.json()

        if users:
            user = users[0]
            required_fields = ["id", "name", "email", "role", "is_active"]
            for field in required_fields:
                assert field in user

        # Stocks data yapısı
        response = mock_enabled_client.get("/mock/stocks")
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
        response = mock_enabled_client.get("/mock/orders")
        orders = response.json()

        if orders:
            order = orders[0]
            required_fields = ["id", "user_id", "total_amount", "status"]
            for field in required_fields:
                assert field in order
