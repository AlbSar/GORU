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
from .routes import router

# Logging konfigürasyonu
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama başlangıç ve kapanış işlemleri"""
    # Startup
    logger.info("Uygulama başlatılıyor...")

    # Mock modunda veya test modunda veritabanı bağlantısı kurma
    from .core.settings import settings
    import os

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
    description="ERP sistemi için RESTful API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTPException'ları handle et"""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
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
            "error": True,
            "message": "Validation error",
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
            "error": True,
            "message": "Database constraint violation",
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
            "error": True,
            "message": "Database error occurred",
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
            "error": True,
            "message": "Internal server error",
            "status_code": 500,
            "path": str(request.url),
        },
    )


# Router'ı ekle
app.include_router(router, prefix="/api/v1")

# Mock router'ı ekle (sadece USE_MOCK=true ise)
if settings.USE_MOCK:
    from .mock_routes import mock_router

    app.include_router(mock_router)


@app.get("/")
async def root():
    """Ana endpoint"""
    response = {"message": "GORU ERP API", "version": "1.0.0"}
    if settings.USE_MOCK:
        response["mock_mode"] = True
        response["mock_prefix"] = settings.MOCK_API_PREFIX
    return response


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "GORU ERP API"}
