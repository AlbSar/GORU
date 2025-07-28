from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# HTTPBearer'ı auto_error=False ile yapılandır
security = HTTPBearer(auto_error=False)

# JWT Secret key (production'da environment variable'dan alınmalı)
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Sabit bir token (örnek için - production'da kullanılmamalı)
VALID_TOKEN = "secret-token"

# Mock user roles (gerçek uygulamada database'den gelir)
USER_ROLES = {
    "admin": ["read", "write", "delete", "admin"],
    "user": ["read", "write"],
    "viewer": ["read"],
}


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """JWT token oluştur"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Token'ı doğrula ve payload'ı döndür"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
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

        # Önce sabit token kontrolü (test için)
        if token == VALID_TOKEN:
            return {
                "user": "authorized",
                "role": "admin",
                "permissions": ["read", "write", "delete"],
            }

        # JWT token kontrolü
        payload = verify_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Kullanıcı bilgilerini döndür
        return {
            "user": username,
            "role": payload.get("role", "user"),
            "permissions": USER_ROLES.get(payload.get("role", "user"), ["read"]),
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
        user_permissions = current_user.get("permissions", [])
        if required_permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {required_permission}",
            )
        return current_user

    return permission_checker


# Şifreyi hashle
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


# Şifreyi doğrula
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )
