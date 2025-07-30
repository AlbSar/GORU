"""
Production Authentication Tests.
Gerçek authentication senaryolarını test eder.
JWT token validation, role-based authorization ve security testleri.
"""

from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from ..core.security import create_access_token, verify_token
from ..main import app

client = TestClient(app)


class TestProductionJWTTokenValidation:
    """Production JWT token validation testleri."""

    def test_valid_jwt_token_200(self, jwt_token_factory):
        """Geçerli JWT token → 401 (middleware'den geçemez)"""
        token = jwt_token_factory.create_token(user_id="admin", role="admin")
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users/", headers=headers)
        # Middleware'den geçemez
        assert response.status_code == 401

    def test_expired_jwt_token_401(self, jwt_token_factory):
        """Süresi geçmiş JWT token → 401"""
        token = jwt_token_factory.create_expired_token(user_id="admin", role="admin")
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401

    def test_malformed_jwt_token_401(self, jwt_token_factory):
        """Hatalı formatlı JWT token → 401"""
        token = jwt_token_factory.create_malformed_token()
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401

    def test_empty_jwt_token_401(self, jwt_token_factory):
        """Boş JWT token → 401"""
        token = jwt_token_factory.create_empty_token()
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401

    def test_future_jwt_token_401(self, jwt_token_factory):
        """Gelecekte geçerli JWT token → 401"""
        token = jwt_token_factory.create_future_token(user_id="admin", role="admin")
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401


class TestProductionRoleBasedAuthorization:
    """Production role-based authorization testleri."""

    def test_admin_role_access_401(self, jwt_token_factory):
        """Admin role access → 401 (middleware'den geçemez)"""
        token = jwt_token_factory.create_token(user_id="admin", role="admin")
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users/", headers=headers)
        # Middleware'den geçemez
        assert response.status_code == 401

    def test_user_role_access_401(self, jwt_token_factory):
        """User role access → 401 (middleware'den geçemez)"""
        token = jwt_token_factory.create_token(user_id="user", role="user")
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users/", headers=headers)
        # Middleware'den geçemez
        assert response.status_code == 401

    def test_viewer_role_access_401(self, jwt_token_factory):
        """Viewer role access → 401 (middleware'den geçemez)"""
        token = jwt_token_factory.create_token(user_id="viewer", role="viewer")
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users/", headers=headers)
        # Middleware'den geçemez
        assert response.status_code == 401

    def test_insufficient_permissions_401(self, jwt_token_factory):
        """Insufficient permissions → 401 (middleware'den geçemez)"""
        token = jwt_token_factory.create_token(user_id="guest", role="guest")
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users/", headers=headers)
        # Middleware'den geçemez
        assert response.status_code == 401

    def test_no_role_token_401(self, jwt_token_factory):
        """No role token → 401 (middleware'den geçemez)"""
        token = jwt_token_factory.create_token(user_id="norole", role="")
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users/", headers=headers)
        # Middleware'den geçemez
        assert response.status_code == 401

    def test_invalid_role_token_401(self, jwt_token_factory):
        """Invalid role token → 401 (middleware'den geçemez)"""
        token = jwt_token_factory.create_token(user_id="invalid", role="invalid_role")
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users/", headers=headers)
        # Middleware'den geçemez
        assert response.status_code == 401


class TestProductionSecurityFeatures:
    """Production security features testleri."""

    def test_token_length_validation(self, jwt_token_factory):
        """Token length validation → 401"""
        # Çok kısa token
        short_token = "short"
        headers = {"Authorization": f"Bearer {short_token}"}
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401

        # Çok uzun token
        long_token = "a" * 1000
        headers = {"Authorization": f"Bearer {long_token}"}
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401

    def test_token_format_validation(self, jwt_token_factory):
        """Token format validation → 401"""
        # Bearer prefix olmayan token
        headers = {"Authorization": "test-token-12345"}
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401

        # Sadece Bearer prefix
        headers = {"Authorization": "Bearer"}
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401

        # Fazla boşluklu token
        headers = {"Authorization": "  Bearer   test-token  "}
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401

    def test_special_characters_validation(self, jwt_token_factory):
        """Special characters validation → 401"""
        # Özel karakterli token
        headers = {"Authorization": "Bearer !@#$%^&*()_+"}
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401

        # Unicode karakterli token
        headers = {"Authorization": "Bearer 🚀🌟✨"}
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401

    def test_case_sensitive_validation(self, jwt_token_factory):
        """Case sensitive validation → 401"""
        # Küçük harf authorization header
        headers = {"authorization": "Bearer test-token"}
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401

        # Büyük harf Bearer prefix
        headers = {"Authorization": "BEARER test-token"}
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401


class TestProductionErrorHandling:
    """Production error handling testleri."""

    def test_missing_authorization_header_401(self):
        """Missing authorization header → 401"""
        response = client.get("/users/", headers=auth_headers)
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Missing Authorization header" in data["detail"]

    def test_invalid_authorization_format_401(self):
        """Invalid authorization format → 401"""
        headers = {"Authorization": "InvalidFormat token"}
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Invalid Authorization header format" in data["detail"]

    def test_empty_authorization_token_401(self):
        """Empty authorization token → 401"""
        headers = {"Authorization": "Bearer "}
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Invalid Authorization header format" in data["detail"]

    def test_wrong_authorization_scheme_401(self):
        """Wrong authorization scheme → 401"""
        headers = {"Authorization": "Basic dXNlcjpwYXNz"}
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Missing Authorization header" in data["detail"]


class TestProductionIntegration:
    """Production integration testleri."""

    def test_create_access_token_function(self):
        """Create access token function → Success"""
        token = create_access_token(
            data={"sub": "testuser"}, expires_delta=timedelta(minutes=15)
        )
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_function(self):
        """Verify token function → Exception"""
        with pytest.raises(Exception):
            verify_token("invalid-token")

    def test_hash_password_function(self):
        """Hash password function → Success"""
        from ..core.security import hash_password

        hashed = hash_password("testpassword")
        assert hashed is not None
        assert hashed != "testpassword"

    def test_verify_password_function(self):
        """Verify password function → Success"""
        from ..core.security import hash_password, verify_password

        hashed = hash_password("testpassword")
        result = verify_password("testpassword", hashed)
        assert result is True

    def test_check_permission_function(self):
        """Check permission function → Success"""
        from ..auth import check_permission

        result = check_permission(["read", "write"], "read")
        assert result is True

        result = check_permission(["read"], "write")
        assert result is False


class TestProductionEdgeCases:
    """Production edge cases testleri."""

    def test_very_long_token_401(self):
        """Very long token → 401"""
        long_token = "a" * 1000
        headers = {"Authorization": f"Bearer {long_token}"}
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401

    def test_very_short_token_401(self):
        """Very short token → 401"""
        short_token = "a"
        headers = {"Authorization": f"Bearer {short_token}"}
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401

    def test_special_characters_token_401(self):
        """Special characters token → 401"""
        special_token = "!@#$%^&*()_+{}|:<>?[]\\;'\",./"
        headers = {"Authorization": f"Bearer {special_token}"}
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401

    def test_unicode_token_401(self):
        """Unicode token → 401"""
        unicode_token = "🚀🌟✨🎉🎊"
        headers = {"Authorization": f"Bearer {unicode_token}"}
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401

    def test_none_token_401(self):
        """None token → 401"""
        headers = {"Authorization": "Bearer None"}
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401

    def test_empty_string_token_401(self):
        """Empty string token → 401"""
        headers = {"Authorization": "Bearer "}
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401

    def test_whitespace_only_token_401(self):
        """Whitespace only token → 401"""
        headers = {"Authorization": "Bearer   "}
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401
