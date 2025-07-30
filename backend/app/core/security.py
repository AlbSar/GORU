"""
Security configuration and utilities.
JWT, password hashing, and security-related functions.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from fastapi import HTTPException, status

from .settings import settings


def generate_secret_key(length: int = 32) -> str:
    """
    Güvenli bir secret key oluşturur.

    Args:
        length: Secret key uzunluğu (default: 32)

    Returns:
        str: Güvenli secret key
    """
    return secrets.token_urlsafe(length)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT access token oluşturur.

    Args:
        data: Token payload'ı
        expires_delta: Token geçerlilik süresi

    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT refresh token oluşturur.

    Args:
        data: Token payload'ı
        expires_delta: Token geçerlilik süresi

    Returns:
        str: Encoded JWT refresh token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    JWT token'ı doğrular ve payload'ı döndürür.

    Args:
        token: JWT token string

    Returns:
        dict: Token payload

    Raises:
        HTTPException: Token geçersiz veya süresi dolmuş
    """
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
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def hash_password(password: str) -> str:
    """
    Şifreyi bcrypt ile hashler.

    Args:
        password: Plain text şifre

    Returns:
        str: Hashed şifre
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Şifreyi doğrular.

    Args:
        plain_password: Plain text şifre
        hashed_password: Hashed şifre

    Returns:
        bool: Şifre doğru ise True
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    """
    Şifre hash'i oluşturur (hash_password ile aynı).

    Args:
        password: Plain text şifre

    Returns:
        str: Hashed şifre
    """
    return hash_password(password)


def verify_password_hash(plain_password: str, hashed_password: str) -> bool:
    """
    Şifre hash'ini doğrular (verify_password ile aynı).

    Args:
        plain_password: Plain text şifre
        hashed_password: Hashed şifre

    Returns:
        bool: Şifre doğru ise True
    """
    return verify_password(plain_password, hashed_password)
