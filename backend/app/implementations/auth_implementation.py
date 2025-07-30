"""
Authentication implementation using the AuthInterface.
"""

from typing import Dict, Optional

from app.core.settings import settings
from app.interfaces.auth_interface import AuthInterface
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from passlib.context import CryptContext

# HTTPBearer'ı auto_error=False ile yapılandır
security = HTTPBearer(auto_error=False)

# Test token from settings
VALID_TOKEN = settings.VALID_TOKEN

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Mock user roles (gerçek uygulamada database'den gelir)
USER_ROLES = {
    "admin": ["read", "write", "delete", "admin"],
    "user": ["read", "write"],
    "viewer": ["read"],
}


class AuthImplementation(AuthInterface):
    """Authentication implementation."""

    def hash_password(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password."""
        return pwd_context.verify(plain_password, hashed_password)

    def verify_token(self, token: str) -> Dict:
        """Verify a JWT token."""
        try:
            import jwt

            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except (jwt.DecodeError, jwt.InvalidTokenError, jwt.InvalidSignatureError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def get_current_user(self, credentials: Optional[str] = None) -> Dict:
        """Get current authenticated user."""
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if credentials != VALID_TOKEN:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "username": "test_user",
            "role": "admin",
            "permissions": USER_ROLES.get("admin", []),
        }

    def check_permission(self, required_permission: str):
        """Check if user has required permission."""

        def permission_checker(current_user: Dict = Depends(self.get_current_user)):
            if required_permission not in current_user.get("permissions", []):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )
            return current_user

        return permission_checker


# Global instance
auth_service = AuthImplementation()
