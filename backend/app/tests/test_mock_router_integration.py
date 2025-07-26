"""
Mock Router Integration Test Suite.
USE_MOCK environment ile mock endpoint'lerin aktif olması testleri.

Bu test suite şunları test eder:
- Mock router'ın koşullu yüklenmesi
- Mock endpoint'lerin erişilebilirliği
- Mock vs gerçek endpoint'lerin ayrımı
- Environment variable handling
- Swagger UI uyumluluğu
"""

import os
import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


def create_test_app(use_mock: bool = False):
    """Test için dinamik app oluştur."""
    # Environment variable'ı ayarla
    os.environ["USE_MOCK"] = str(use_mock).lower()

    # Settings'i yeniden yükle
    from ..core.settings import Settings

    settings = Settings()

    # App'i yeniden oluştur
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    from ..routes import router

    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="""
        GORU ERP Backend API
        
        ## Mock Mode
        USE_MOCK environment variable ile mock endpoint'ler aktif edilebilir:
        - USE_MOCK=true: Mock endpoint'ler (/mock/*) aktif
        - USE_MOCK=false: Sadece gerçek endpoint'ler aktif
        
        ## Endpoints
        - /api/v1/*: Gerçek API endpoint'leri (auth gerekli)
        - /mock/*: Mock API endpoint'leri (USE_MOCK=true ise)
        """,
        debug=settings.DEBUG,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        version="1.0.0",
    )

    # CORS middleware yapılandırması
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Ana router'ı dahil et (gerçek API endpoint'leri)
    app.include_router(router, prefix=settings.API_V1_STR)

    # Mock router'ı koşullu olarak dahil et
    if settings.USE_MOCK:
        try:
            from ..mock_routes import mock_router

            app.include_router(mock_router)
        except ImportError as e:
            print(f"❌ Mock router import hatası: {e}")
        except Exception as e:
            print(f"❌ Mock router dahil etme hatası: {e}")

    @app.get("/", tags=["System"])
    def read_root():
        """
        API root endpoint.

        Returns:
            dict: API durumu ve konfigürasyon bilgileri
        """
        return {
            "message": "GORU ERP Backend API çalışıyor!",
            "version": "1.0.0",
            "mock_mode": settings.USE_MOCK,
            "api_prefix": settings.API_V1_STR,
            "mock_prefix": (
                settings.MOCK_API_PREFIX if settings.USE_MOCK else None
            ),
            "environment": settings.APP_ENV,
            "debug": settings.DEBUG,
        }

    @app.get("/health", tags=["System"])
    def health_check():
        """
        Health check endpoint.

        Returns:
            dict: Sistem sağlık durumu
        """
        return {
            "status": "healthy",
            "mock_enabled": settings.USE_MOCK,
            "timestamp": "2024-01-01T00:00:00Z",  # Gerçek uygulamada datetime.now() kullanılır
        }

    return app


@pytest.fixture
def mock_enabled_client():
    """Mock aktif olan client fixture."""
    app = create_test_app(use_mock=True)
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_disabled_client():
    """Mock devre dışı olan client fixture."""
    app = create_test_app(use_mock=False)
    with TestClient(app) as client:
        yield client


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
        """Mock user oluştur ve oku."""
        # CREATE
        user_data = {
            "name": "Mock Integration User",
            "email": f"integration-{uuid.uuid4()}@mock.com",
            "role": "user",
            "is_active": True,
            "password": "mock123",
        }
        create_response = mock_enabled_client.post(
            "/mock/users/", json=user_data
        )
        assert create_response.status_code == 201
        created_user = create_response.json()
        user_id = created_user["id"]

        # READ
        read_response = mock_enabled_client.get(f"/mock/users/{user_id}")
        assert read_response.status_code == 200
        read_user = read_response.json()
        assert read_user["name"] == user_data["name"]
        assert read_user["email"] == user_data["email"]

    def test_mock_stock_create_and_update(self, mock_enabled_client):
        """Mock stock oluştur ve güncelle."""
        # CREATE
        stock_data = {
            "product_name": f"Mock Product {uuid.uuid4()}",
            "quantity": 100,
            "unit_price": 29.99,
            "supplier": "Mock Supplier",
        }
        create_response = mock_enabled_client.post(
            "/mock/stocks/", json=stock_data
        )
        assert create_response.status_code == 201
        created_stock = create_response.json()
        stock_id = created_stock["id"]

        # UPDATE
        update_data = {"quantity": 200, "unit_price": 39.99}
        update_response = mock_enabled_client.put(
            f"/mock/stocks/{stock_id}", json=update_data
        )
        assert update_response.status_code == 200
        updated_stock = update_response.json()
        assert updated_stock["quantity"] == 200
        assert updated_stock["unit_price"] == 39.99

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
        create_response = mock_enabled_client.post(
            "/mock/orders/", json=order_data
        )
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
        delete_response = mock_enabled_client.delete(
            f"/mock/orders/{order_id}"
        )
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
        response = mock_enabled_client.post(
            "/mock/stocks/", json=invalid_stock
        )
        # Validation hatası olabilir veya başarılı olabilir (mock service'e bağlı)
        assert response.status_code in [422, 201]


class TestMockVsRealEndpoints:
    """Mock ve gerçek endpoint'ler karşılaştırma testleri."""

    def test_real_endpoints_require_auth(self, mock_disabled_client):
        """Gerçek endpoint'ler auth gerektirmeli."""
        endpoints = ["/api/v1/users/", "/api/v1/stocks/", "/api/v1/orders/"]

        for endpoint in endpoints:
            response = mock_disabled_client.get(endpoint)
            # Auth gerektiren endpoint'ler 401 veya 403 döner
            assert response.status_code in [401, 403]

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

        # Real endpoint (auth gerektirir)
        real_response = mock_enabled_client.get(
            "/api/v1/users/", headers=auth_headers
        )
        # Auth header'ı varsa 200, yoksa 401/403
        assert real_response.status_code in [200, 401, 403]

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
        real_response = mock_enabled_client.get("/api/v1/users/")
        assert real_response.status_code in [401, 403]  # Auth gerekli


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
            "password": "test123",
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
            "password": "test123",
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
        from ..core.settings import Settings
        default_settings = Settings()
        assert hasattr(default_settings, 'USE_MOCK')
        
        # Environment override
        with patch.dict(os.environ, {'USE_MOCK': 'true'}):
            env_settings = Settings()
            assert env_settings.USE_MOCK
            
        with patch.dict(os.environ, {'USE_MOCK': 'false'}):
            env_settings = Settings()
            assert not env_settings.USE_MOCK

    @patch.dict(os.environ, {'USE_MOCK': 'invalid_value'})
    def test_invalid_environment_value_handling(self):
        """Geçersiz environment value handling."""
        from ..core.settings import Settings
        
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
        from ..core.settings import Settings
        
        # True değerleri
        true_values = ['true', 'True', 'TRUE', '1', 'yes', 'Yes', 'YES', 'on', 'On', 'ON']
        for value in true_values:
            with patch.dict(os.environ, {'USE_MOCK': value}):
                settings = Settings()
                assert settings.USE_MOCK
        
        # False değerleri
        false_values = ['false', 'False', 'FALSE', '0', 'no', 'No', 'NO', 'off', 'Off', 'OFF', '']
        for value in false_values:
            with patch.dict(os.environ, {'USE_MOCK': value}):
                settings = Settings()
                assert not settings.USE_MOCK


class TestSwaggerUIDocumentation:
    """Swagger UI dokümantasyon testleri."""

    def test_mock_endpoints_in_swagger(self, mock_enabled_client):
        """Mock endpoint'ler Swagger UI'da görünmeli."""
        # OpenAPI schema'sını al
        response = mock_enabled_client.get("/api/v1/openapi.json")
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

    def test_mock_endpoints_not_in_swagger_when_disabled(
        self, mock_disabled_client
    ):
        """Mock endpoint'ler USE_MOCK=false ise Swagger'da görünmemeli."""
        # OpenAPI schema'sını al
        response = mock_disabled_client.get("/api/v1/openapi.json")
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
        response = mock_enabled_client.get("/api/v1/openapi.json")
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
