# GORU ERP Backend - Environment Setup Dokümantasyonu

## 📋 İçindekiler

1. [Sistem Gereksinimleri](#sistem-gereksinimleri)
2. [Kurulum Adımları](#kurulum-adımları)
3. [Environment Variables](#environment-variables)
4. [Database Kurulumu](#database-kurulumu)
5. [Docker Kurulumu](#docker-kurulumu)
6. [Development Setup](#development-setup)
7. [Production Setup](#production-setup)
8. [Troubleshooting](#troubleshooting)

## 💻 Sistem Gereksinimleri

### Minimum Gereksinimler
- **Python**: 3.11+ (3.13.5 önerilen)
- **PostgreSQL**: 15+ (development için SQLite da kullanılabilir)
- **Docker**: 20.10+ (opsiyonel)
- **Git**: 2.30+

### Önerilen Gereksinimler
- **RAM**: 4GB+ (development), 8GB+ (production)
- **CPU**: 2+ cores (development), 4+ cores (production)
- **Disk**: 10GB+ boş alan
- **OS**: Linux/macOS/Windows 10+

## 🚀 Kurulum Adımları

### 1. Repository Klonlama
```bash
# Repository'yi klonla
git clone https://github.com/AlbSar/GORU.git
cd GORU

# Branch kontrolü
git branch
git checkout main
```

### 2. Python Environment Kurulumu
```bash
# Python versiyonunu kontrol et
python --version  # 3.11+ olmalı

# Virtual environment oluştur
python -m venv venv

# Virtual environment'ı aktifleştir
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

# Bağımlılıkları yükle
cd backend
pip install -r requirements.txt
```

### 3. Environment Dosyası Oluşturma
```bash
# Root dizine dön
cd ..

# Environment dosyasını kopyala
cp env.example .env

# .env dosyasını düzenle
# Windows
notepad .env

# Linux/macOS
nano .env
```

## 🔧 Environment Variables

### Temel Ayarlar
```env
# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================
APP_ENV=development
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=debug

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================
SECRET_KEY=your-super-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
# PostgreSQL (Production)
DATABASE_URL=postgresql://username:password@localhost:5432/goru_db
TEST_DATABASE_URL=postgresql://username:password@localhost:5432/goru_test_db

# SQLite (Development/Test)
DEV_DATABASE_URL=sqlite:///./dev.db
TEST_SQLITE_URL=sqlite:///./test.db

# =============================================================================
# CORS CONFIGURATION
# =============================================================================
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# =============================================================================
# MIDDLEWARE CONFIGURATION
# =============================================================================
ENABLE_SECURITY_HEADERS=true
ENABLE_RATE_LIMITING=true
ENABLE_LOGGING_MIDDLEWARE=true
DEFAULT_RATE_LIMIT=60
BURST_RATE_LIMIT=120
RATE_LIMIT_WINDOW=60

# =============================================================================
# MOCK SYSTEM CONFIGURATION
# =============================================================================
USE_MOCK=false
MOCK_API_PREFIX=/mock

# =============================================================================
# API CONFIGURATION
# =============================================================================
API_V1_STR=/api/v1
PROJECT_NAME=GORU ERP Backend
VALID_TOKEN=test-token-12345
```

### Production Ayarları
```env
# Production için değiştirilmesi gerekenler
APP_ENV=production
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# Güvenli secret key'ler
SECRET_KEY=your-production-secret-key-here
JWT_SECRET_KEY=your-production-jwt-secret-key-here

# Production database
DATABASE_URL=postgresql://prod_user:prod_password@prod_host:5432/goru_prod_db

# Production CORS
BACKEND_CORS_ORIGINS=["https://yourdomain.com", "https://api.yourdomain.com"]

# Production middleware
ENABLE_SECURITY_HEADERS=true
ENABLE_RATE_LIMITING=true
DEFAULT_RATE_LIMIT=100
BURST_RATE_LIMIT=200

# Mock system kapalı
USE_MOCK=false
```

## 🗄️ Database Kurulumu

### PostgreSQL Kurulumu

#### Windows
```bash
# PostgreSQL indir ve kur
# https://www.postgresql.org/download/windows/

# PostgreSQL servisini başlat
net start postgresql-x64-15

# psql ile bağlan
psql -U postgres

# Database oluştur
CREATE DATABASE goru_db;
CREATE DATABASE goru_test_db;
CREATE USER goru_user WITH PASSWORD 'goru_password';
GRANT ALL PRIVILEGES ON DATABASE goru_db TO goru_user;
GRANT ALL PRIVILEGES ON DATABASE goru_test_db TO goru_user;
```

#### Linux (Ubuntu/Debian)
```bash
# PostgreSQL kur
sudo apt update
sudo apt install postgresql postgresql-contrib

# PostgreSQL servisini başlat
sudo systemctl start postgresql
sudo systemctl enable postgresql

# PostgreSQL kullanıcısına geç
sudo -u postgres psql

# Database oluştur
CREATE DATABASE goru_db;
CREATE DATABASE goru_test_db;
CREATE USER goru_user WITH PASSWORD 'goru_password';
GRANT ALL PRIVILEGES ON DATABASE goru_db TO goru_user;
GRANT ALL PRIVILEGES ON DATABASE goru_test_db TO goru_user;
```

#### macOS
```bash
# Homebrew ile PostgreSQL kur
brew install postgresql

# PostgreSQL servisini başlat
brew services start postgresql

# Database oluştur
createdb goru_db
createdb goru_test_db
```

### SQLite Kurulumu (Development)
```bash
# SQLite genellikle Python ile birlikte gelir
# Ek kurulum gerekmez

# Database dosyaları otomatik oluşturulur
# dev.db ve test.db dosyaları backend/ klasöründe oluşur
```

### Database Migration
```bash
# Backend klasörüne geç
cd backend

# Alembic migration'ları çalıştır
alembic upgrade head

# Test database için migration
python -m pytest app/tests/test_database_coverage.py -v
```

## 🐳 Docker Kurulumu

### Docker Compose ile Kurulum
```bash
# Docker Compose dosyasını kontrol et
cat docker-compose.yml

# Servisleri başlat
docker-compose up --build

# Arka planda çalıştır
docker-compose up -d --build

# Servisleri durdur
docker-compose down

# Logları görüntüle
docker-compose logs -f
```

### Docker Compose Override
```bash
# Development override
cat docker-compose.override.yml

# Production override
cat docker-compose.prod.yml
```

### Manuel Docker Kurulumu
```bash
# Backend image'ını build et
docker build -t goru-backend:latest backend/

# Container'ı çalıştır
docker run -d \
  --name goru-backend \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://goru_user:goru_password@host.docker.internal:5432/goru_db \
  goru-backend:latest

# Container loglarını görüntüle
docker logs -f goru-backend

# Container'a bağlan
docker exec -it goru-backend bash
```

## 🔧 Development Setup

### Local Development
```bash
# Virtual environment'ı aktifleştir
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

# Backend klasörüne geç
cd backend

# Bağımlılıkları yükle
pip install -r requirements.txt

# Development server'ı başlat
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Alternatif olarak
python -m uvicorn app.main:app --reload
```

### Development Environment Variables
```env
# Development için .env
APP_ENV=development
DEBUG=true
LOG_LEVEL=debug

# SQLite kullan (development için)
DATABASE_URL=sqlite:///./dev.db
TEST_DATABASE_URL=sqlite:///./test.db

# Mock system açık (development için)
USE_MOCK=true

# CORS ayarları
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"]

# Rate limiting gevşek
DEFAULT_RATE_LIMIT=1000
BURST_RATE_LIMIT=2000
```

### Development Tools
```bash
# Linting
black backend/app/ --line-length 88
isort backend/app/ --profile black
flake8 backend/app/
ruff check backend/app/

# Pre-commit hooks
pre-commit install
pre-commit run --all-files

# Test çalıştırma
python -m pytest --cov=app --cov-report=term-missing

# Coverage raporu
python -m pytest --cov=app --cov-report=html
# htmlcov/index.html dosyasını aç
```

## 🚀 Production Setup

### Production Environment Variables
```env
# Production için .env
APP_ENV=production
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# PostgreSQL kullan
DATABASE_URL=postgresql://prod_user:prod_password@prod_host:5432/goru_prod_db

# Mock system kapalı
USE_MOCK=false

# Güvenlik ayarları
ENABLE_SECURITY_HEADERS=true
ENABLE_RATE_LIMITING=true
DEFAULT_RATE_LIMIT=60
BURST_RATE_LIMIT=120

# CORS ayarları
BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
```

### Production Deployment
```bash
# Docker ile production
docker-compose -f docker-compose.prod.yml up -d

# Manuel production deployment
docker build -t goru-backend:prod backend/
docker run -d \
  --name goru-backend-prod \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://prod_user:prod_password@prod_host:5432/goru_prod_db \
  -e APP_ENV=production \
  -e DEBUG=false \
  goru-backend:prod
```

### Production Monitoring
```bash
# Health check
curl http://localhost:8000/health

# API docs
curl http://localhost:8000/docs

# Logs
docker logs -f goru-backend-prod

# Metrics
curl http://localhost:8000/metrics
```

## 🧪 Test Environment

### Test Database Setup
```bash
# Test database oluştur
createdb goru_test_db

# Test environment variables
export TEST_DATABASE_URL=postgresql://goru_user:goru_password@localhost:5432/goru_test_db
export TEST_SQLITE_URL=sqlite:///./test.db

# Test çalıştır
python -m pytest --cov=app --cov-report=term-missing

# Belirli test dosyalarını çalıştır
python -m pytest app/tests/test_users_fixed.py -v
python -m pytest app/tests/test_stocks_fixed.py -v
python -m pytest app/tests/test_orders.py -v
```

### Test Environment Variables
```env
# Test için .env.test
APP_ENV=test
DEBUG=true
LOG_LEVEL=debug

# Test database
DATABASE_URL=sqlite:///./test.db
TEST_DATABASE_URL=sqlite:///./test.db

# Mock system açık
USE_MOCK=true

# Test ayarları
ENABLE_SECURITY_HEADERS=false
ENABLE_RATE_LIMITING=false
```

## 🔍 Troubleshooting

### Yaygın Sorunlar

#### 1. Import Hataları
```bash
# Hata: ImportError: cannot import name 'ALGORITHM' from 'app.auth'
# Çözüm: Import path'lerini düzelt
# app/tests/test_auth_error_handling.py dosyasını güncelle
```

#### 2. Database Bağlantı Sorunları
```bash
# Hata: Connection refused
# Çözüm: PostgreSQL servisini başlat
sudo systemctl start postgresql  # Linux
net start postgresql-x64-15      # Windows
brew services start postgresql    # macOS

# Hata: Database does not exist
# Çözüm: Database oluştur
createdb goru_db
createdb goru_test_db
```

#### 3. Port Çakışması
```bash
# Hata: Address already in use
# Çözüm: Port'u değiştir
uvicorn app.main:app --reload --port 8001

# Veya mevcut process'i bul ve durdur
lsof -i :8000
kill -9 <PID>
```

#### 4. Permission Sorunları
```bash
# Hata: Permission denied
# Çözüm: Dosya izinlerini düzelt
chmod +x backend/scripts/*.py
chmod 755 backend/
```

#### 5. Virtual Environment Sorunları
```bash
# Hata: Module not found
# Çözüm: Virtual environment'ı aktifleştir
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Veya yeniden oluştur
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

### Debug Komutları
```bash
# Python versiyonu kontrol et
python --version

# Virtual environment kontrol et
which python
pip list

# Database bağlantısını test et
python backend/test_db.py

# Environment variables kontrol et
python -c "import os; print(os.environ.get('DATABASE_URL'))"

# Port kullanımını kontrol et
netstat -tulpn | grep :8000

# Docker container durumu
docker ps
docker logs <container_name>
```

### Log Dosyaları
```bash
# Application logs
tail -f backend/logs/app.log

# Docker logs
docker logs -f goru-backend

# System logs
journalctl -u postgresql -f  # Linux
```

## 📊 Monitoring ve Logging

### Health Check Endpoints
```bash
# Health check
curl http://localhost:8000/health

# API docs
curl http://localhost:8000/docs

# Metrics
curl http://localhost:8000/metrics
```

### Logging Konfigürasyonu
```python
# backend/app/core/settings.py
LOG_LEVEL = "debug"  # development
LOG_LEVEL = "info"   # production

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### Performance Monitoring
```bash
# Memory kullanımı
docker stats goru-backend

# CPU kullanımı
top -p $(pgrep -f uvicorn)

# Database bağlantıları
psql -U goru_user -d goru_db -c "SELECT * FROM pg_stat_activity;"
```

---

**Son Güncelleme:** Güncel  
**Environment:** Development/Production  
**Database:** PostgreSQL/SQLite  
**Docker:** Supported  
**Python:** 3.11+ 