"""
Security Headers Middleware.
Production ortamında güvenlik header'larını ekler.
"""

from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Güvenlik header'larını ekleyen middleware.

    Eklenen header'lar:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Strict-Transport-Security: max-age=31536000; includeSubDomains
    - Content-Security-Policy: default-src 'self'
    - Referrer-Policy: strict-origin-when-cross-origin
    - Permissions-Policy: geolocation=(), microphone=(), camera=()
    """

    def __init__(
        self,
        app: ASGIApp,
        hsts_max_age: int = 31536000,
        hsts_include_subdomains: bool = True,
        hsts_preload: bool = False,
        csp_policy: str = (
            "default-src 'self'; script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; "
            "font-src 'self' data:; connect-src 'self'; frame-ancestors 'none';"
        ),
        referrer_policy: str = "strict-origin-when-cross-origin",
        permissions_policy: str = (
            "geolocation=(), microphone=(), camera=(), payment=(), usb=(), "
            "magnetometer=(), gyroscope=(), accelerometer=()"
        ),
    ):
        super().__init__(app)
        self.hsts_max_age = hsts_max_age
        self.hsts_include_subdomains = hsts_include_subdomains
        self.hsts_preload = hsts_preload
        self.csp_policy = csp_policy
        self.referrer_policy = referrer_policy
        self.permissions_policy = permissions_policy

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Request'i işler ve güvenlik header'larını ekler."""
        response = await call_next(request)

        # HSTS header'ını oluştur
        hsts_parts = [f"max-age={self.hsts_max_age}"]
        if self.hsts_include_subdomains:
            hsts_parts.append("includeSubDomains")
        if self.hsts_preload:
            hsts_parts.append("preload")

        # Güvenlik header'larını ekle
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "; ".join(hsts_parts)
        response.headers["Content-Security-Policy"] = self.csp_policy
        response.headers["Referrer-Policy"] = self.referrer_policy
        response.headers["Permissions-Policy"] = self.permissions_policy

        # Cache control header'ları (güvenlik için)
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = (
                "no-store, no-cache, must-revalidate, max-age=0"
            )
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

        return response
