"""
FastAPI uygulaması ana dosyası.
ERP sistemi için API endpoint'lerini sağlar.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .core.settings import settings
from .database import Base
from .middleware import (
    LoggingMiddleware,
    RateLimitingMiddleware,
    SecurityHeadersMiddleware,
)
from .routes import orders_router, stocks_router, users_router

# Logging konfigürasyonu
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama başlangıç ve kapanış işlemleri"""
    # Startup
    logger.info("Uygulama başlatılıyor...")

    # Mock modunda veya test modunda veritabanı bağlantısı kurma
    import os

    from .core.settings import settings

    is_testing = os.getenv("TESTING") or os.getenv("PYTEST_CURRENT_TEST")

    if not settings.USE_MOCK and not is_testing:
        from .database import get_engine

        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        logger.info("Veritabanı tabloları oluşturuldu.")
    else:
        if settings.USE_MOCK:
            logger.info("Mock modu aktif - veritabanı bağlantısı atlanıyor.")
        if is_testing:
            logger.info("Test modu aktif - veritabanı bağlantısı atlanıyor.")

    yield

    # Shutdown
    logger.info("Uygulama kapatılıyor...")


app = FastAPI(
    title="GORU ERP API",
    description="""
    ERP sistemi için RESTful API
    
    ## Özellikler
    * **Rate Limiting**: IP bazlı rate limiting
    * **Security Headers**: CORS, CSP, HSTS güvenlik header'ları
    * **Request Logging**: Detaylı request/response logging
    * **Monitoring**: Health check, metrics ve status endpoint'leri
    * **Production Ready**: Production ortamı için optimize edilmiş middleware'ler
    
    ## Monitoring Endpoints
    * `GET /health` - Temel health check
    * `GET /metrics` - Prometheus uyumlu sistem metrikleri
    * `GET /status` - Detaylı servis durumu
    
    ## Middleware'ler
    * **Security Headers**: X-Content-Type-Options, X-Frame-Options, CSP, HSTS
    * **Rate Limiting**: IP bazlı, endpoint bazlı farklı limitler
    * **Logging**: Request/response timing ve detayları
    """,
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "monitoring",
            "description": "Monitoring ve health check endpoint'leri",
        },
        {"name": "users", "description": "Kullanıcı yönetimi endpoint'leri"},
        {"name": "orders", "description": "Sipariş yönetimi endpoint'leri"},
        {"name": "stocks", "description": "Stok yönetimi endpoint'leri"},
    ],
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Production middleware'leri ekle
if settings.ENABLE_LOGGING_MIDDLEWARE:
    app.add_middleware(LoggingMiddleware)

if settings.ENABLE_RATE_LIMITING:
    app.add_middleware(
        RateLimitingMiddleware,
        default_requests_per_minute=settings.DEFAULT_RATE_LIMIT,
        burst_requests_per_minute=settings.BURST_RATE_LIMIT,
        window_size=settings.RATE_LIMIT_WINDOW,
        rate_limits={
            "/api/v1/auth/": (30, 60),  # Auth endpoint'leri için daha sıkı limit
            "/api/v1/users/": (100, 200),  # User endpoint'leri için yüksek limit
            "/api/v1/orders/": (50, 100),  # Order endpoint'leri için orta limit
            "/api/v1/stocks/": (80, 160),  # Stock endpoint'leri için orta limit
        },
    )

if settings.ENABLE_SECURITY_HEADERS:
    app.add_middleware(SecurityHeadersMiddleware)


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTPException'ları handle et"""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url),
        },
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Pydantic validation hatalarını handle et"""
    logger.warning(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "details": exc.errors(),
            "status_code": 422,
            "path": str(request.url),
        },
    )


@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    """Database integrity hatalarını handle et"""
    logger.error(f"Database Integrity Error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Database constraint violation",
            "details": str(exc),
            "status_code": 400,
            "path": str(request.url),
        },
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Genel SQLAlchemy hatalarını handle et"""
    logger.error(f"Database Error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Database error occurred",
            "status_code": 500,
            "path": str(request.url),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Genel exception'ları handle et"""
    logger.error(f"Unexpected Error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "status_code": 500,
            "path": str(request.url),
        },
    )


# Router'ları ekle
app.include_router(users_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")
app.include_router(stocks_router, prefix="/api/v1")

# Mock router'ı ekle (sadece USE_MOCK=true ise)
if settings.USE_MOCK:
    from .mock_routes import mock_router

    app.include_router(mock_router)


@app.get("/")
async def root():
    """Ana endpoint"""
    response = {"detail": "GORU ERP API", "version": "1.0.0"}
    if settings.USE_MOCK:
        response["mock_mode"] = True
        response["mock_prefix"] = settings.MOCK_API_PREFIX
    return response


@app.get("/health", tags=["monitoring"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "GORU ERP API"}


@app.get("/metrics", tags=["monitoring"])
async def metrics():
    """Prometheus uyumlu metrics endpoint"""
    import time

    import psutil

    # Sistem metrikleri
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    # Uygulama metrikleri
    process = psutil.Process()
    process_memory = process.memory_info()

    metrics_data = {
        "timestamp": time.time(),
        "system": {
            "cpu_percent": cpu_percent,
            "memory_total": memory.total,
            "memory_available": memory.available,
            "memory_percent": memory.percent,
            "disk_total": disk.total,
            "disk_used": disk.used,
            "disk_percent": disk.percent,
        },
        "application": {
            "process_memory_rss": process_memory.rss,
            "process_memory_vms": process_memory.vms,
            "process_cpu_percent": process.cpu_percent(),
            "process_create_time": process.create_time(),
        },
        "service": {"name": "GORU ERP API", "version": "1.0.0", "status": "healthy"},
    }

    return metrics_data


@app.get("/status", tags=["monitoring"])
async def service_status():
    """Detaylı servis durumu endpoint'i"""
    import time

    from .core.settings import settings

    # Database URL'ini güvenli şekilde parse et
    db_url = settings.DATABASE_URL
    if "@" in db_url:
        db_display = db_url.split("@")[1]
    else:
        db_display = "configured"

    status_data = {
        "service": "GORU ERP API",
        "version": "1.0.0",
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "mock_mode": settings.USE_MOCK,
        "middleware": {
            "security_headers": settings.ENABLE_SECURITY_HEADERS,
            "rate_limiting": settings.ENABLE_RATE_LIMITING,
            "logging": settings.ENABLE_LOGGING_MIDDLEWARE,
        },
        "database": {
            "url": db_display,
            "type": "postgresql" if "postgresql" in db_url else "sqlite",
        },
        "timestamp": time.time(),
    }

    return status_data
