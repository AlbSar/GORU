"""
Test fixtures for authentication and authorization tests.
"""

from datetime import UTC, datetime, timedelta
from typing import Dict, List

import jwt
import pytest

from ...core.settings import settings


class JWTTokenFactory:
    """JWT token oluşturmak için factory class."""

    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM

    def create_token(
        self,
        user_id: str = "testuser",
        role: str = "user",
        permissions: List[str] = None,
        expires_in: int = 15,  # dakika
        **extra_claims,
    ) -> str:
        """JWT token oluştur."""
        if permissions is None:
            permissions = self._get_default_permissions(role)

        payload = {
            "sub": user_id,
            "role": role,
            "permissions": permissions,
            "exp": datetime.now(UTC) + timedelta(minutes=expires_in),
            "iat": datetime.now(UTC),
            **extra_claims,
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_expired_token(
        self,
        user_id: str = "testuser",
        role: str = "user",
        permissions: List[str] = None,
        **extra_claims,
    ) -> str:
        """Süresi geçmiş JWT token oluştur."""
        if permissions is None:
            permissions = self._get_default_permissions(role)

        payload = {
            "sub": user_id,
            "role": role,
            "permissions": permissions,
            "exp": datetime.now(UTC) - timedelta(hours=1),
            "iat": datetime.now(UTC) - timedelta(hours=2),
            **extra_claims,
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_future_token(
        self,
        user_id: str = "testuser",
        role: str = "user",
        permissions: List[str] = None,
        **extra_claims,
    ) -> str:
        """Gelecekte geçerli olacak JWT token oluştur."""
        if permissions is None:
            permissions = self._get_default_permissions(role)

        payload = {
            "sub": user_id,
            "role": role,
            "permissions": permissions,
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC) + timedelta(minutes=1),
            **extra_claims,
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_malformed_token(self) -> str:
        """Hatalı formatlı JWT token oluştur."""
        return "invalid.jwt.token"

    def create_empty_token(self) -> str:
        """Boş JWT token oluştur."""
        return ""

    def _get_default_permissions(self, role: str) -> List[str]:
        """Role'e göre varsayılan yetkileri döndür."""
        role_permissions = {
            "admin": ["read", "write", "delete", "admin"],
            "user": ["read", "write"],
            "viewer": ["read"],
            "guest": [],
        }
        return role_permissions.get(role, [])


class RoleBasedFixtures:
    """Role bazlı test fixture'ları."""

    def __init__(self, token_factory: JWTTokenFactory):
        self.token_factory = token_factory

    def admin_user(self) -> Dict[str, str]:
        """Admin kullanıcı fixture'ı."""
        token = self.token_factory.create_token(
            user_id="admin_user",
            role="admin",
            permissions=["read", "write", "delete", "admin"],
        )
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def regular_user(self) -> Dict[str, str]:
        """Normal kullanıcı fixture'ı."""
        token = self.token_factory.create_token(
            user_id="regular_user", role="user", permissions=["read", "write"]
        )
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def viewer_user(self) -> Dict[str, str]:
        """Viewer kullanıcı fixture'ı."""
        token = self.token_factory.create_token(
            user_id="viewer_user", role="viewer", permissions=["read"]
        )
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def guest_user(self) -> Dict[str, str]:
        """Misafir kullanıcı fixture'ı."""
        token = self.token_factory.create_token(
            user_id="guest_user", role="guest", permissions=[]
        )
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def expired_admin_user(self) -> Dict[str, str]:
        """Süresi geçmiş admin kullanıcı fixture'ı."""
        token = self.token_factory.create_expired_token(
            user_id="expired_admin", role="admin"
        )
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def future_admin_user(self) -> Dict[str, str]:
        """Gelecekte geçerli admin kullanıcı fixture'ı."""
        token = self.token_factory.create_future_token(
            user_id="future_admin", role="admin"
        )
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


class PermissionFixtures:
    """Permission bazlı test fixture'ları."""

    def __init__(self, token_factory: JWTTokenFactory):
        self.token_factory = token_factory

    def read_permission_user(self) -> Dict[str, str]:
        """Sadece okuma yetkisi olan kullanıcı."""
        token = self.token_factory.create_token(
            user_id="read_user", role="viewer", permissions=["read"]
        )
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def write_permission_user(self) -> Dict[str, str]:
        """Yazma yetkisi olan kullanıcı."""
        token = self.token_factory.create_token(
            user_id="write_user", role="user", permissions=["read", "write"]
        )
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def delete_permission_user(self) -> Dict[str, str]:
        """Silme yetkisi olan kullanıcı."""
        token = self.token_factory.create_token(
            user_id="delete_user", role="admin", permissions=["read", "write", "delete"]
        )
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def admin_permission_user(self) -> Dict[str, str]:
        """Admin yetkisi olan kullanıcı."""
        token = self.token_factory.create_token(
            user_id="admin_user",
            role="admin",
            permissions=["read", "write", "delete", "admin"],
        )
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def no_permission_user(self) -> Dict[str, str]:
        """Hiç yetkisi olmayan kullanıcı."""
        token = self.token_factory.create_token(
            user_id="no_permission_user", role="guest", permissions=[]
        )
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


# Global fixture instances
jwt_factory = JWTTokenFactory()
role_fixtures = RoleBasedFixtures(jwt_factory)
permission_fixtures = PermissionFixtures(jwt_factory)


# Pytest fixtures
@pytest.fixture
def jwt_token_factory():
    """JWT token factory fixture."""
    return jwt_factory


@pytest.fixture
def role_based_fixtures():
    """Role bazlı fixture'lar."""
    return role_fixtures


@pytest.fixture
def permission_based_fixtures():
    """Permission bazlı fixture'lar."""
    return permission_fixtures


@pytest.fixture
def admin_headers():
    """Admin kullanıcı headers."""
    return role_fixtures.admin_user()


@pytest.fixture
def user_headers():
    """Normal kullanıcı headers."""
    return role_fixtures.regular_user()


@pytest.fixture
def viewer_headers():
    """Viewer kullanıcı headers."""
    return role_fixtures.viewer_user()


@pytest.fixture
def guest_headers():
    """Misafir kullanıcı headers."""
    return role_fixtures.guest_user()


@pytest.fixture
def expired_headers():
    """Süresi geçmiş token headers."""
    return role_fixtures.expired_admin_user()


@pytest.fixture
def future_headers():
    """Gelecekte geçerli token headers."""
    return role_fixtures.future_admin_user()


@pytest.fixture
def read_headers():
    """Sadece okuma yetkisi headers."""
    return permission_fixtures.read_permission_user()


@pytest.fixture
def write_headers():
    """Yazma yetkisi headers."""
    return permission_fixtures.write_permission_user()


@pytest.fixture
def delete_headers():
    """Silme yetkisi headers."""
    return permission_fixtures.delete_permission_user()


@pytest.fixture
def admin_permission_headers():
    """Admin yetkisi headers."""
    return permission_fixtures.admin_permission_user()


@pytest.fixture
def no_permission_headers():
    """Hiç yetkisi olmayan headers."""
    return permission_fixtures.no_permission_user()


@pytest.fixture
def malformed_token_headers():
    """Hatalı formatlı token headers."""
    return {
        "Authorization": f"Bearer {jwt_factory.create_malformed_token()}",
        "Content-Type": "application/json",
    }


@pytest.fixture
def empty_token_headers():
    """Boş token headers."""
    return {
        "Authorization": f"Bearer {jwt_factory.create_empty_token()}",
        "Content-Type": "application/json",
    }


@pytest.fixture
def no_auth_headers():
    """Authentication olmayan headers."""
    return {"Content-Type": "application/json"}


@pytest.fixture
def invalid_auth_headers():
    """Geçersiz authentication headers."""
    return {"Authorization": "Bearer invalid-token", "Content-Type": "application/json"}
