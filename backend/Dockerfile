# Multi-stage build için base image
FROM python:3.11-slim as base

# Sistem paketlerini güncelle ve gerekli paketleri yükle
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Python environment'ını ayarla
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

# Non-root kullanıcı oluştur
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Çalışma dizinini ayarla
WORKDIR /app

# Development stage
FROM base as development

# Requirements dosyasını kopyala ve bağımlılıkları yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tüm uygulama kodunu kopyala
COPY . .

# Dosya sahipliğini değiştir
RUN chown -R appuser:appuser /app

# Kullanıcıyı değiştir
USER appuser

# Development için uvicorn'u hot reload ile çalıştır
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production

# Requirements dosyasını kopyala ve bağımlılıkları yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sadece gerekli dosyaları kopyala (development dosyaları hariç)
COPY app/ ./app/
COPY alembic.ini .
COPY migrations/ ./migrations/

# Dosya sahipliğini değiştir
RUN chown -R appuser:appuser /app

# Kullanıcıyı değiştir
USER appuser

# Production için uvicorn'u çalıştır
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# Health check ekle
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Test stage
FROM base as test

# Requirements dosyasını kopyala ve bağımlılıkları yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Test dosyalarını kopyala
COPY . .

# Dosya sahipliğini değiştir
RUN chown -R appuser:appuser /app

# Kullanıcıyı değiştir
USER appuser

# Test komutunu çalıştır
CMD ["pytest", "-v", "--cov=app", "--cov-report=html", "--cov-report=term"] 