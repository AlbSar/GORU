"""
GORU ERP Backend API.
FastAPI tabanlı REST API uygulaması.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.settings import settings
from .routes import router

# FastAPI app instance'ı oluştur
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "GORU Backend API - Mock Mode ve Endpoints\n\n"
        "Mock Mode: USE_MOCK=true ise /mock/ prefix'i ile "
        "mock endpoint'ler aktif olur.\n"
        "Gerçek Endpoints: /api/v1/ prefix'i ile gerçek "
        "veritabanı endpoint'leri.\n\n"
        "Mock Endpoints: /mock/users, /mock/stocks, /mock/orders\n"
        "Real Endpoints: /api/v1/users, /api/v1/stocks, /api/v1/orders"
    ),
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS middleware yapılandırması
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ana router'ı dahil et (gerçek API endpoint'leri)
app.include_router(router, prefix=settings.API_V1_STR)

# Mock router'ı koşullu olarak dahil et
if settings.USE_MOCK:
    try:
        from .mock_routes import mock_router

        app.include_router(mock_router)
        print(
            "Mock router aktif: {} prefix'i ile".format(
                settings.MOCK_API_PREFIX
            )
        )
    except ImportError as e:
        print("Mock router import hatası: {}".format(e))
    except Exception as e:
        print("Mock router dahil etme hatası: {}".format(e))
else:
    print("Mock router devre dışı (USE_MOCK=false)")


@app.get("/", tags=["System"])
def read_root():
    """
    API root endpoint.

    Returns:
        dict: API durumu ve konfigürasyon bilgileri
    """
    return {
        "message": "GORU ERP Backend API çalışıyor!",
        "version": "1.0.0",
        "mock_mode": settings.USE_MOCK,
        "api_prefix": settings.API_V1_STR,
        "mock_prefix": (
            settings.MOCK_API_PREFIX if settings.USE_MOCK else None
        ),
        "environment": settings.APP_ENV,
        "debug": settings.DEBUG,
    }


@app.get("/health", tags=["System"])
def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Sistem sağlık durumu
    """
    return {
        "status": "healthy",
        "mock_enabled": settings.USE_MOCK,
        "timestamp": (
            "2024-01-01T00:00:00Z"  # Gerçek uygulamada datetime.now() kullanılır
        ),
    }
