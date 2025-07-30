"""
Logging Middleware.
Tüm gelen/giden request ve response'ları loglar.
"""

import json
import logging
import time
from typing import Callable, Dict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Logger'ı yapılandır
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Request ve response'ları loglayan middleware.

    Özellikler:
    - Request detayları (method, path, headers, body)
    - Response detayları (status_code, headers, body)
    - Timing bilgileri
    - Error handling
    - Sensitive data filtering
    """

    def __init__(
        self,
        app: ASGIApp,
        log_request_body: bool = True,
        log_response_body: bool = True,
        log_headers: bool = True,
        sensitive_headers: set = None,
        sensitive_paths: set = None,
        max_body_size: int = 1024 * 10,  # 10KB
    ):
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.log_headers = log_headers
        self.sensitive_headers = sensitive_headers or {
            "authorization",
            "cookie",
            "x-api-key",
            "x-auth-token",
        }
        self.sensitive_paths = sensitive_paths or {
            "/api/v1/auth/login",
            "/api/v1/auth/register",
        }
        self.max_body_size = max_body_size

    def _filter_sensitive_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Hassas header'ları filtreler."""
        filtered_headers = {}
        for key, value in headers.items():
            if key.lower() in self.sensitive_headers:
                filtered_headers[key] = "[REDACTED]"
            else:
                filtered_headers[key] = value
        return filtered_headers

    def _truncate_body(self, body: str, max_size: int = None) -> str:
        """Body'yi belirtilen boyuta kısaltır."""
        if max_size is None:
            max_size = self.max_body_size

        if len(body) > max_size:
            return body[:max_size] + "... [TRUNCATED]"
        return body

    def _is_sensitive_path(self, path: str) -> bool:
        """Path'in hassas olup olmadığını kontrol eder."""
        return any(sensitive_path in path for sensitive_path in self.sensitive_paths)

    async def _get_request_body(self, request: Request) -> str:
        """Request body'sini alır."""
        if not self.log_request_body:
            return ""

        try:
            body = await request.body()
            if body:
                # JSON body'yi decode et
                try:
                    body_str = body.decode("utf-8")
                    # JSON formatında ise pretty print yap
                    json.loads(body_str)
                    return self._truncate_body(body_str)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return f"[BINARY DATA - {len(body)} bytes]"
            return ""
        except Exception as e:
            return f"[ERROR READING BODY: {str(e)}]"

    async def _get_response_body(self, response: Response) -> str:
        """Response body'sini alır."""
        if not self.log_response_body:
            return ""

        try:
            # Response body'sini al
            if hasattr(response, "body"):
                body = response.body
                if isinstance(body, bytes):
                    try:
                        body_str = body.decode("utf-8")
                        return self._truncate_body(body_str)
                    except UnicodeDecodeError:
                        return f"[BINARY DATA - {len(body)} bytes]"
                elif isinstance(body, str):
                    return self._truncate_body(body)
            return ""
        except Exception as e:
            return f"[ERROR READING RESPONSE BODY: {str(e)}]"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Request'i işler ve loglar."""
        start_time = time.time()

        # Request bilgilerini topla
        path = request.url.path
        method = request.method
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")

        # Request body'sini al
        request_body = ""
        if not self._is_sensitive_path(path):
            request_body = await self._get_request_body(request)

        # Request headers'ını al
        request_headers = {}
        if self.log_headers:
            request_headers = self._filter_sensitive_headers(dict(request.headers))

        # Request log'u
        log_data = {
            "type": "request",
            "method": method,
            "path": path,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "headers": request_headers,
            "body": request_body,
            "timestamp": time.time(),
        }

        logger.info(f"REQUEST: {method} {path} from {client_ip}", extra=log_data)

        try:
            # Response'u al
            response = await call_next(request)

            # Timing hesapla
            process_time = time.time() - start_time

            # Response headers'ını al
            response_headers = {}
            if self.log_headers:
                response_headers = dict(response.headers)

            # Response body'sini al
            response_body = ""
            if not self._is_sensitive_path(path):
                response_body = await self._get_response_body(response)

            # Response log'u
            log_data = {
                "type": "response",
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "process_time": round(process_time, 4),
                "client_ip": client_ip,
                "headers": response_headers,
                "body": response_body,
                "timestamp": time.time(),
            }

            # Status code'a göre log seviyesi
            if response.status_code >= 400:
                logger.warning(
                    f"RESPONSE: {method} {path} -> {response.status_code} "
                    f"({process_time:.4f}s)",
                    extra=log_data,
                )
            else:
                logger.info(
                    f"RESPONSE: {method} {path} -> {response.status_code} "
                    f"({process_time:.4f}s)",
                    extra=log_data,
                )

            # Response header'ına timing bilgisi ekle
            response.headers["X-Process-Time"] = str(round(process_time, 4))

            return response

        except Exception as e:
            # Error durumunda log
            process_time = time.time() - start_time
            log_data = {
                "type": "error",
                "method": method,
                "path": path,
                "error": str(e),
                "process_time": round(process_time, 4),
                "client_ip": client_ip,
                "timestamp": time.time(),
            }

            logger.error(
                f"ERROR: {method} {path} -> {str(e)} ({process_time:.4f}s)",
                extra=log_data,
                exc_info=True,
            )
            raise
