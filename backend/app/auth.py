"""
Authentication and authorization utilities.
JWT token handling, user authentication, and permission checking.
"""

from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext

from .core.settings import settings

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


def hash_password(password: str) -> str:
    """Şifreyi hash'le"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Şifreyi doğrula"""
    return pwd_context.verify(plain_password, hashed_password)


def verify_token(token: str) -> dict:
    """JWT token'ı doğrula"""
    try:
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


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
):
    """
    Mevcut kullanıcıyı doğrula.
    401: Geçersiz/eksik token
    403: Yetkisiz erişim (role-based)
    500: Internal server error
    """
    try:
        # Eksik token kontrolü
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = credentials.credentials

        # Boş token kontrolü
        if not token or token.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Empty authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Geçersiz token kontrolü
        if token != VALID_TOKEN:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Geçerli token için kullanıcı bilgilerini döndür
        return {
            "user": "authorized",
            "role": "admin",
            "permissions": ["read", "write", "delete"],
        }

    except HTTPException:
        # HTTPException'ları tekrar fırlat
        raise
    except Exception:
        # Diğer tüm hatalar için 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error",
            headers={"WWW-Authenticate": "Bearer"},
        )


def check_permission(required_permission: str):
    """Permission kontrolü için decorator"""

    def permission_checker(current_user: dict = Depends(get_current_user)):
        user_permissions = current_user.get("permissions", []) or []
        if required_permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: " f"{required_permission}",
            )
        return current_user

    return permission_checker
