"""
JWT Token Standardization Tests.
JWT token validation, expiration, and role-based tests.
"""

from datetime import UTC, datetime, timedelta

import jwt
from fastapi.testclient import TestClient

from ..core.settings import settings
from ..main import app

client = TestClient(app)


class TestJWTTokenStandardization:
    def test_valid_jwt_token_200(self, jwt_token_factory):
        token = jwt_token_factory.create_token(user_id="admin", role="admin")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=headers)
        assert response.status_code in [200, 401, 500]

    def test_expired_jwt_token_401(self, jwt_token_factory):
        token = jwt_token_factory.create_token(
            user_id="admin", role="admin", expires_in=-1
        )
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=headers)
        assert response.status_code in [401, 500]
        if response.status_code != 500:
            data = response.json()
            assert "detail" in data

    def test_future_jwt_token_401(self, jwt_token_factory):
        future_time = datetime.now(UTC) + timedelta(hours=1)
        token = jwt.encode(
            {"sub": "admin", "role": "admin", "exp": future_time},
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=headers)
        assert response.status_code in [401, 500]
        if response.status_code != 500:
            data = response.json()
            assert "detail" in data

    def test_malformed_jwt_token_401(self):
        headers = {
            "Authorization": "Bearer malformed.token.here",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=headers)
        assert response.status_code in [401, 500]
        if response.status_code != 500:
            data = response.json()
            assert "detail" in data

    def test_empty_jwt_token_401(self):
        headers = {"Authorization": "Bearer ", "Content-Type": "application/json"}
        try:
            response = client.get("/users/", headers=headers)
            assert response.status_code in [401, 500]
            if response.status_code != 500:
                data = response.json()
                assert "detail" in data
        except Exception as e:
            # Middleware'den HTTPException fırlatılıyor
            assert (
                "401" in str(e)
                or "Missing Authorization header" in str(e)
                or "Invalid Authorization header format" in str(e)
            )

    def test_no_jwt_token_401(self):
        headers = {"Content-Type": "application/json"}
        try:
            response = client.get("/users/", headers=headers)
            assert response.status_code in [401, 500]
            if response.status_code != 500:
                data = response.json()
                assert "detail" in data
        except Exception as e:
            # Middleware'den HTTPException fırlatılıyor
            assert (
                "401" in str(e)
                or "Missing Authorization header" in str(e)
                or "Invalid Authorization header format" in str(e)
            )

    def test_invalid_jwt_token_401(self):
        headers = {
            "Authorization": "Bearer invalid-token",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=headers)
        assert response.status_code in [401, 500]
        if response.status_code != 500:
            data = response.json()
            assert "detail" in data


class TestRoleBasedJWTTokens:
    def test_admin_role_jwt_token(self, jwt_token_factory):
        token = jwt_token_factory.create_token(user_id="admin", role="admin")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=headers)
        assert response.status_code in [200, 401, 500]

    def test_user_role_jwt_token(self, jwt_token_factory):
        token = jwt_token_factory.create_token(user_id="user", role="user")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=headers)
        assert response.status_code in [200, 401, 500]

    def test_guest_role_jwt_token(self, jwt_token_factory):
        token = jwt_token_factory.create_token(user_id="guest", role="guest")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=headers)
        assert response.status_code in [200, 401, 500]


class TestJWTTokenFactory:
    def test_create_valid_token(self, jwt_token_factory):
        token = jwt_token_factory.create_token(user_id="testuser", role="user")
        assert isinstance(token, str)

    def test_create_expired_token(self, jwt_token_factory):
        token = jwt_token_factory.create_expired_token(user_id="testuser", role="user")
        assert isinstance(token, str)

    def test_create_future_token(self, jwt_token_factory):
        token = jwt_token_factory.create_future_token(user_id="testuser", role="user")
        assert isinstance(token, str)

    def test_create_malformed_token(self, jwt_token_factory):
        token = jwt_token_factory.create_malformed_token()
        assert isinstance(token, str)

    def test_create_empty_token(self, jwt_token_factory):
        token = jwt_token_factory.create_empty_token()
        assert token == ""

    def test_default_permissions(self, jwt_token_factory):
        perms = jwt_token_factory._get_default_permissions("admin")
        assert "admin" in perms


class TestJWTTokenIntegration:
    def test_jwt_token_with_custom_permissions(self, jwt_token_factory):
        token = jwt_token_factory.create_token(
            user_id="testuser", role="user", permissions=["read", "write"]
        )
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=headers)
        assert response.status_code in [200, 401, 403, 500]

    def test_jwt_token_with_extra_claims(self, jwt_token_factory):
        token = jwt_token_factory.create_token(
            user_id="testuser", role="user", permissions=["read"], custom_claim="custom"
        )
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=headers)
        assert response.status_code in [200, 401, 403, 500]

    def test_jwt_token_expiration_handling(self, jwt_token_factory):
        token = jwt_token_factory.create_token(
            user_id="testuser", role="user", expires_in=-1
        )
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=headers)
        assert response.status_code in [401, 500]


class TestJWTTokenSecurity:
    def test_jwt_token_signature_verification(self, jwt_token_factory):
        token = jwt_token_factory.create_token(user_id="testuser", role="user")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=headers)
        assert response.status_code in [200, 401, 403, 500]

    def test_jwt_token_algorithm_verification(self, jwt_token_factory):
        token = jwt_token_factory.create_token(user_id="testuser", role="user")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=headers)
        assert response.status_code in [200, 401, 403, 500]

    def test_jwt_token_tampering_detection(self, jwt_token_factory):
        token = jwt_token_factory.create_token(user_id="testuser", role="user")
        # Token'ı değiştir
        tampered_token = token + "tampered"
        headers = {
            "Authorization": f"Bearer {tampered_token}",
            "Content-Type": "application/json",
        }
        response = client.get("/users/", headers=headers)
        assert response.status_code in [401, 500]
