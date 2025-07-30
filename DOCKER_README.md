# GORU ERP Docker Kurulumu

Bu dosya, GORU ERP projesinin Docker ile nasıl çalıştırılacağını açıklar.

## 🚀 Hızlı Başlangıç

### Development Ortamı

```bash
# Development ortamını başlat
docker-compose up -d

# Logları izle
docker-compose logs -f backend

# Servisleri durdur
docker-compose down
```

### Production Ortamı

```bash
# Production ortamını başlat
docker-compose -f docker-compose.prod.yml up -d

# Logları izle
docker-compose -f docker-compose.prod.yml logs -f backend

# Servisleri durdur
docker-compose -f docker-compose.prod.yml down
```

## 📁 Dosya Yapısı

```
GORU/
├── docker-compose.yml              # Ana compose dosyası
├── docker-compose.override.yml     # Development override
├── docker-compose.prod.yml         # Production compose
└── backend/
    ├── Dockerfile                  # Multi-stage Dockerfile
    └── .dockerignore              # Docker ignore dosyası
```

## 🔧 Dockerfile Özellikleri

### Multi-Stage Build
- **Base Stage**: Ortak Python environment
- **Development Stage**: Hot reload ile development
- **Production Stage**: Optimize edilmiş production build

### Optimizasyonlar
- Alpine Linux tabanlı PostgreSQL
- Health check'ler
- Volume mapping ile hot reload
- Cache optimizasyonu

## 🛠️ Komutlar

### Development

```bash
# Sadece backend'i yeniden build et
docker-compose build backend

# Tüm servisleri yeniden build et
docker-compose build

# Backend'e bağlan
docker-compose exec backend bash

# Database'e bağlan
docker-compose exec db psql -U goru -d goru_db

# Logları temizle
docker-compose logs --tail=100 backend
```

### Production

```bash
# Production build
docker-compose -f docker-compose.prod.yml build

# Production'da çalıştır
docker-compose -f docker-compose.prod.yml up -d

# Production logları
docker-compose -f docker-compose.prod.yml logs -f
```

## 🔍 Health Check

- **Backend**: `http://localhost:8000/health`
- **Database**: PostgreSQL connection check
- **Interval**: 30s (dev), 60s (prod)

## 📊 Monitoring

```bash
# Container durumlarını kontrol et
docker-compose ps

# Resource kullanımını izle
docker stats

# Health check sonuçları
docker-compose exec backend curl http://localhost:8000/health
```

## 🗄️ Database

### Development
- **Port**: 5432
- **User**: goru
- **Password**: goru
- **Database**: goru_db

### Production
- **Port**: 5432
- **User**: goru
- **Password**: goru
- **Database**: goru_db

## 🔄 Hot Reload

Development ortamında kod değişiklikleri otomatik olarak yansır:

```bash
# Kod değişikliği yap
# Uvicorn otomatik olarak yeniden başlar
```

## 🧹 Temizlik

```bash
# Tüm container'ları ve volume'ları sil
docker-compose down -v

# Docker cache'ini temizle
docker system prune -a

# Sadece kullanılmayan image'ları sil
docker image prune
```

## 🚨 Sorun Giderme

### Backend Başlamıyor
```bash
# Logları kontrol et
docker-compose logs backend

# Container'ı yeniden başlat
docker-compose restart backend
```

### Database Bağlantı Hatası
```bash
# Database'in hazır olduğunu kontrol et
docker-compose exec db pg_isready -U goru -d goru_db

# Database'i yeniden başlat
docker-compose restart db
```

### Port Çakışması
```bash
# Kullanılan portları kontrol et
netstat -tulpn | grep :8000
netstat -tulpn | grep :5432

# Farklı port kullan
docker-compose up -d -p 8001:8000
```

## 📝 Environment Variables

### Development
```yaml
ENVIRONMENT: development
DEBUG: true
DATABASE_URL: postgresql://goru:goru@db:5432/goru_db
```

### Production
```yaml
ENVIRONMENT: production
DEBUG: false
DATABASE_URL: postgresql://goru:goru@db:5432/goru_db
```

## 🔐 Güvenlik

- Production'da environment variables kullanın
- Database şifrelerini güvenli tutun
- Health check'leri aktif tutun
- Logları düzenli kontrol edin 