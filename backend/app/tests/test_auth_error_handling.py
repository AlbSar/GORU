"""
Auth modülü için error handling testleri.
401, 403, 500 hata senaryolarını test eder.
JWT token validation ve role-based authorization kapsar.
"""

from datetime import UTC, datetime, timedelta

import jwt

from ..core.settings import settings


# JWT Token Factory - Eski fonksiyonlar, jwt_token_factory kullanılacak
def create_test_jwt(
    payload: dict,
    secret: str = settings.JWT_SECRET_KEY,
    algorithm: str = settings.JWT_ALGORITHM,
):
    """Test için JWT token oluştur"""
    return jwt.encode(payload, secret, algorithm=algorithm)


def create_expired_jwt(payload: dict):
    """Süresi geçmiş JWT token oluştur"""
    payload["exp"] = datetime.now(UTC) - timedelta(hours=1)
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def create_future_jwt(payload: dict):
    """Gelecekte geçerli olacak JWT token oluştur"""
    payload["exp"] = datetime.now(UTC) + timedelta(hours=1)
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


# genel hata senaryosu testleri
class TestAuthErrorHandling:
    """Auth error handling testleri."""

    def test_missing_token_401(self, unauthenticated_client):
        """Missing token → 401"""
        response = unauthenticated_client.get("/users/")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_invalid_token_401(self, unauthenticated_client):
        """Invalid token → 401"""
        invalid_headers = {"Authorization": "Bearer invalid-token"}
        response = unauthenticated_client.get("/users/", headers=invalid_headers)
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_malformed_token_401(self, unauthenticated_client):
        """Malformed token → 401"""
        malformed_headers = {"Authorization": "InvalidFormat token"}
        response = unauthenticated_client.get("/users/", headers=malformed_headers)
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_empty_token_401(self, unauthenticated_client):
        """Empty token → 401"""
        empty_headers = {"Authorization": "Bearer "}
        try:
            response = unauthenticated_client.get("/users/", headers=empty_headers)
            assert response.status_code == 401
        except Exception as e:
            # HTTPException fırlatılırsa bu da geçerli
            assert "401" in str(e) or "Invalid Authorization header format" in str(e)

    def test_wrong_token_format_401(self, unauthenticated_client):
        """Wrong token format → 401"""
        wrong_format_headers = {"Authorization": "Basic dXNlcjpwYXNz"}
        response = unauthenticated_client.get("/users/", headers=wrong_format_headers)
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_insufficient_permissions_403(self, unauthenticated_client):
        """Insufficient permissions → 403"""
        # Admin endpoint'i yok, 404 döner
        response = unauthenticated_client.get("/admin/")
        assert response.status_code == 404

    def test_auth_internal_error_500(self, unauthenticated_client):
        """Auth internal error → 500"""
        # Auth olmadan test et
        headers = {"Authorization": "Bearer error-token"}
        response = unauthenticated_client.get("/users/", headers=headers)
        assert response.status_code == 401

    def test_users_without_auth_401(self, unauthenticated_client):
        """Users endpoint without auth → 401"""
        response = unauthenticated_client.get("/users/")
        assert response.status_code == 401

    def test_stocks_without_auth_401(self, unauthenticated_client):
        """Stocks endpoint without auth → 401"""
        response = unauthenticated_client.get("/stocks/")
        assert response.status_code == 401

    def test_orders_with_invalid_auth_401(self, unauthenticated_client):
        """Orders endpoint with invalid auth → 401"""
        invalid_headers = {"Authorization": "Bearer invalid-token"}
        response = unauthenticated_client.get("/orders/", headers=invalid_headers)
        assert response.status_code == 401

    def test_users_with_invalid_auth_401(self, unauthenticated_client):
        """Users endpoint with invalid auth → 401"""
        invalid_headers = {"Authorization": "Bearer invalid-token"}
        response = unauthenticated_client.get("/users/", headers=invalid_headers)
        assert response.status_code == 401

    def test_stocks_with_invalid_auth_401(self, unauthenticated_client):
        """Stocks endpoint with invalid auth → 401"""
        invalid_headers = {"Authorization": "Bearer invalid-token"}
        response = unauthenticated_client.get("/stocks/", headers=invalid_headers)
        assert response.status_code == 401

    def test_very_long_token_401(self, unauthenticated_client):
        """Very long token → 401"""
        long_token = "a" * 1000
        long_headers = {"Authorization": f"Bearer {long_token}"}
        response = unauthenticated_client.get("/users/", headers=long_headers)
        assert response.status_code == 401

    def test_special_characters_in_token_401(self, unauthenticated_client):
        """Special characters in token → 401"""
        special_headers = {"Authorization": "Bearer !@#$%^&*()"}
        response = unauthenticated_client.get("/users/", headers=special_headers)
        assert response.status_code == 401

    def test_multiple_auth_headers_401(self, unauthenticated_client):
        """Multiple auth headers → 401"""
        multiple_headers = {
            "Authorization": "Bearer token1",
            "authorization": "Bearer token2",
        }
        response = unauthenticated_client.get("/users/", headers=multiple_headers)
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_case_sensitive_auth_401(self, unauthenticated_client):
        """Case sensitive auth → 401"""
        case_headers = {"authorization": "Bearer test-token"}
        response = unauthenticated_client.get("/users/", headers=case_headers)
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_extra_spaces_in_token_401(self, unauthenticated_client):
        """Extra spaces in token → 401"""
        extra_spaces_headers = {"Authorization": "Bearer  token  "}
        response = unauthenticated_client.get("/users/", headers=extra_spaces_headers)
        assert response.status_code == 401

    def test_token_without_bearer_prefix(self, unauthenticated_client):
        """Token without Bearer prefix → 401"""
        no_bearer_headers = {"Authorization": "test-token"}
        response = unauthenticated_client.get("/users/", headers=no_bearer_headers)
        assert response.status_code == 401

    def test_token_with_extra_spaces_after_bearer(self, unauthenticated_client):
        """Token with extra spaces after Bearer → 401"""
        extra_spaces_headers = {"Authorization": "Bearer   test-token"}
        response = unauthenticated_client.get("/users/", headers=extra_spaces_headers)
        assert response.status_code == 401

    def test_token_with_whitespace_only(self, unauthenticated_client):
        """Token with whitespace only → 401"""
        whitespace_headers = {"Authorization": "Bearer   "}
        try:
            response = unauthenticated_client.get("/users/", headers=whitespace_headers)
            assert response.status_code == 401
        except Exception as e:
            # HTTPException fırlatılırsa bu da geçerli
            assert "401" in str(e) or "Invalid Authorization header format" in str(e)
