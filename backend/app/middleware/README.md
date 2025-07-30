# Middleware Kullanım Kılavuzu

Bu klasör, production-ready middleware'leri içerir. Bu middleware'ler güvenlik, performans ve izleme için tasarlanmıştır.

## Middleware'ler

### 1. SecurityHeadersMiddleware

Güvenlik header'larını otomatik olarak ekler:

- **X-Content-Type-Options**: nosniff
- **X-Frame-Options**: DENY  
- **X-XSS-Protection**: 1; mode=block
- **Strict-Transport-Security**: max-age=31536000; includeSubDomains
- **Content-Security-Policy**: Güvenli CSP politikası
- **Referrer-Policy**: strict-origin-when-cross-origin
- **Permissions-Policy**: Hassas API'leri devre dışı bırakır

### 2. RateLimitingMiddleware

API endpoint'leri için rate limiting sağlar:

- **IP bazlı rate limiting**
- **Endpoint bazlı farklı limitler**
- **Sliding window algoritması**
- **Burst protection**

Varsayılan ayarlar:
- Genel: 60 request/dakika
- Burst: 120 request/dakika
- Window: 60 saniye

### 3. LoggingMiddleware

Tüm request ve response'ları detaylı şekilde loglar:

- **Request detayları** (method, path, headers, body)
- **Response detayları** (status_code, headers, body)
- **Timing bilgileri**
- **Error handling**
- **Sensitive data filtering**

## Kullanım

### Otomatik Kullanım

Middleware'ler `main.py` dosyasında otomatik olarak etkinleştirilir:

```python
# Production middleware'leri ekle
if settings.ENABLE_LOGGING_MIDDLEWARE:
    app.add_middleware(LoggingMiddleware)

if settings.ENABLE_RATE_LIMITING:
    app.add_middleware(RateLimitingMiddleware)

if settings.ENABLE_SECURITY_HEADERS:
    app.add_middleware(SecurityHeadersMiddleware)
```

### Manuel Kullanım

```python
from app.middleware import (
    SecurityHeadersMiddleware,
    RateLimitingMiddleware,
    LoggingMiddleware
)

# Security headers
app.add_middleware(SecurityHeadersMiddleware)

# Rate limiting
app.add_middleware(
    RateLimitingMiddleware,
    default_requests_per_minute=60,
    burst_requests_per_minute=120,
    rate_limits={
        "/api/v1/auth/": (30, 60),
        "/api/v1/users/": (100, 200),
    }
)

# Logging
app.add_middleware(LoggingMiddleware)
```

## Konfigürasyon

### Environment Variables

`.env` dosyasında middleware ayarlarını yapılandırabilirsiniz:

```env
# Middleware ayarları
ENABLE_SECURITY_HEADERS=true
ENABLE_RATE_LIMITING=true
ENABLE_LOGGING_MIDDLEWARE=true

# Rate limiting ayarları
DEFAULT_RATE_LIMIT=60
BURST_RATE_LIMIT=120
RATE_LIMIT_WINDOW=60

# Logging ayarları
LOG_REQUEST_BODY=true
LOG_RESPONSE_BODY=true
LOG_HEADERS=true
MAX_LOG_BODY_SIZE=10240
```

### Settings.py

`core/settings.py` dosyasında middleware ayarları tanımlanmıştır:

```python
# Middleware ayarları
ENABLE_SECURITY_HEADERS: bool = True
ENABLE_RATE_LIMITING: bool = True
ENABLE_LOGGING_MIDDLEWARE: bool = True

# Rate limiting ayarları
DEFAULT_RATE_LIMIT: int = 60
BURST_RATE_LIMIT: int = 120
RATE_LIMIT_WINDOW: int = 60

# Logging ayarları
LOG_REQUEST_BODY: bool = True
LOG_RESPONSE_BODY: bool = True
LOG_HEADERS: bool = True
MAX_LOG_BODY_SIZE: int = 10240
```

## Test Etme

Middleware'leri test etmek için:

```bash
# Tüm middleware test'lerini çalıştır
pytest app/tests/test_middleware.py -v

# Sadece security headers test'lerini çalıştır
pytest app/tests/test_middleware.py::TestSecurityHeadersMiddleware -v

# Sadece rate limiting test'lerini çalıştır
pytest app/tests/test_middleware.py::TestRateLimitingMiddleware -v

# Sadece logging test'lerini çalıştır
pytest app/tests/test_middleware.py::TestLoggingMiddleware -v
```

## Production Önerileri

### 1. Security Headers

- Production'da HSTS preload'u etkinleştirin
- CSP politikasını uygulamanıza göre özelleştirin
- Permissions-Policy'yi ihtiyaçlarınıza göre ayarlayın

### 2. Rate Limiting

- Endpoint bazlı limitleri iş yüküne göre ayarlayın
- Burst limitlerini dikkatli yapılandırın
- Excluded path'leri genişletin

### 3. Logging

- Production'da log seviyesini INFO'ya ayarlayın
- Log rotation yapılandırın
- Sensitive data filtering'i genişletin
- Log aggregation kullanın

## Troubleshooting

### Rate Limiting Sorunları

1. **429 hatası alıyorsunuz**: Rate limit aşıldı
   - Limit değerlerini artırın
   - Burst limitlerini kontrol edin

2. **Rate limit header'ları eksik**: Middleware etkin değil
   - `ENABLE_RATE_LIMITING=true` kontrol edin

### Logging Sorunları

1. **Log'lar görünmüyor**: Logger seviyesi yanlış
   - `LOG_LEVEL=INFO` ayarlayın

2. **Performans sorunu**: Body logging çok büyük
   - `MAX_LOG_BODY_SIZE` değerini düşürün

### Security Headers Sorunları

1. **CSP hatası**: Content Security Policy çok katı
   - CSP politikasını uygulamanıza göre ayarlayın

2. **HSTS hatası**: HTTPS kullanmıyorsunuz
   - Production'da HTTPS kullanın

## Örnekler

### Custom Rate Limits

```python
app.add_middleware(
    RateLimitingMiddleware,
    rate_limits={
        "/api/v1/auth/login": (5, 10),      # Login için çok sıkı
        "/api/v1/auth/register": (2, 5),    # Register için çok sıkı
        "/api/v1/users/": (100, 200),       # User endpoint'leri için yüksek
        "/api/v1/orders/": (50, 100),       # Order endpoint'leri için orta
        "/api/v1/stocks/": (80, 160),       # Stock endpoint'leri için orta
    }
)
```

### Custom Security Headers

```python
app.add_middleware(
    SecurityHeadersMiddleware,
    csp_policy="default-src 'self'; script-src 'self' 'unsafe-inline';",
    hsts_max_age=31536000,
    hsts_include_subdomains=True,
    hsts_preload=True
)
```

### Custom Logging

```python
app.add_middleware(
    LoggingMiddleware,
    log_request_body=True,
    log_response_body=False,  # Response body'yi loglama
    sensitive_headers={"authorization", "cookie", "x-api-key"},
    sensitive_paths={"/api/v1/auth/login", "/api/v1/auth/register"},
    max_body_size=1024 * 5  # 5KB
)
``` 