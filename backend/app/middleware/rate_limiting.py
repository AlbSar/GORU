"""
Rate Limiting Middleware.
API endpoint'leri için rate limiting sağlar.
"""

import time
from collections import defaultdict
from typing import Callable, Dict, Tuple

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting sağlayan middleware.

    Özellikler:
    - IP bazlı rate limiting
    - Endpoint bazlı farklı limitler
    - Sliding window algoritması
    - Configurable limitler
    """

    def __init__(
        self,
        app: ASGIApp,
        default_requests_per_minute: int = 60,
        burst_requests_per_minute: int = 120,
        window_size: int = 60,  # saniye
        excluded_paths: set = None,
        rate_limits: Dict[str, Tuple[int, int]] = None,
    ):
        super().__init__(app)
        self.default_requests_per_minute = default_requests_per_minute
        self.burst_requests_per_minute = burst_requests_per_minute
        self.window_size = window_size
        self.excluded_paths = excluded_paths or {"/health", "/docs", "/openapi.json"}
        self.rate_limits = rate_limits or {}

        # Rate limiting storage
        self.request_counts: Dict[str, list] = defaultdict(list)

    def _get_client_ip(self, request: Request) -> str:
        """Client IP adresini alır."""
        # X-Forwarded-For header'ından IP al
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # X-Real-IP header'ından IP al
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Client host'undan IP al
        return request.client.host if request.client else "unknown"

    def _get_rate_limit(self, path: str) -> Tuple[int, int]:
        """Path için rate limit değerlerini döndürür."""
        # Özel path limitleri
        for pattern, (normal, burst) in self.rate_limits.items():
            if path.startswith(pattern):
                return normal, burst

        # Default limitler
        return self.default_requests_per_minute, self.burst_requests_per_minute

    def _is_rate_limited(self, client_ip: str, path: str, current_time: float) -> bool:
        """Rate limiting kontrolü yapar."""
        key = f"{client_ip}:{path}"
        requests = self.request_counts[key]

        # Eski request'leri temizle (window_size'dan eski)
        cutoff_time = current_time - self.window_size
        requests = [req_time for req_time in requests if req_time > cutoff_time]
        self.request_counts[key] = requests

        # Rate limit değerlerini al
        normal_limit, burst_limit = self._get_rate_limit(path)

        # Request sayısını kontrol et
        if len(requests) >= normal_limit:
            # Burst limit kontrolü
            recent_requests = [
                req_time
                for req_time in requests
                if req_time > current_time - 10  # Son 10 saniye
            ]
            if len(recent_requests) >= burst_limit:
                return True

        return False

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Request'i işler ve rate limiting uygular."""
        path = request.url.path
        client_ip = self._get_client_ip(request)
        current_time = time.time()

        # Excluded path kontrolü
        if path in self.excluded_paths:
            return await call_next(request)

        # Rate limiting kontrolü
        if self._is_rate_limited(client_ip, path, current_time):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        # Request'i kaydet
        key = f"{client_ip}:{path}"
        self.request_counts[key].append(current_time)

        # Response'u al
        response = await call_next(request)

        # Rate limit header'larını ekle
        normal_limit, burst_limit = self._get_rate_limit(path)
        response.headers["X-RateLimit-Limit"] = str(normal_limit)
        response.headers["X-RateLimit-Remaining"] = str(
            normal_limit - len(self.request_counts[key])
        )
        response.headers["X-RateLimit-Reset"] = str(
            int(current_time + self.window_size)
        )

        return response
