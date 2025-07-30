# Docker Kullanım Kılavuzu

Bu dokümantasyon, GORU projesinin Docker ile nasıl çalıştırılacağını açıklar.

## 🐳 Docker Yapılandırması

### Güncellenmiş Özellikler

- **Multi-stage build**: Development, production ve test ortamları için ayrı aşamalar
- **Güvenlik**: Non-root kullanıcı ile çalışma
- **Optimizasyon**: Gereksiz dosyaların .dockerignore ile filtrelenmesi
- **Resource limits**: Memory ve CPU limitleri
- **Health checks**: Otomatik sağlık kontrolü
- **Logging**: Gelişmiş log yapılandırması

## 📁 Dosya Yapısı

```
├── backend/
│   ├── Dockerfile          # Multi-stage Docker build
│   ├── .dockerignore       # Docker ignore dosyası
│   └── requirements.txt    # Python bağımlılıkları
├── docker-compose.yml      # Development ortamı
├── docker-compose.prod.yml # Production ortamı
├── build.sh               # Bash build script (Linux/Mac)
├── build.ps1              # PowerShell build script (Windows)
└── DOCKER_README.md       # Bu dosya
```

## 🚀 Hızlı Başlangıç

### Windows PowerShell Kullanarak

```powershell
# Development ortamını başlat
.\build.ps1 dev

# Production ortamını başlat
.\build.ps1 prod

# Testleri çalıştır
.\build.ps1 test

# Tüm container'ları durdur
.\build.ps1 stop
```

### Linux/Mac Bash Kullanarak

```bash
# Development ortamını başlat
./build.sh dev

# Production ortamını başlat
./build.sh prod

# Testleri çalıştır
./build.sh test

# Tüm container'ları durdur
./build.sh stop
```

## 🔧 Manuel Docker Komutları

### Development Ortamı

```bash
# Development image'ını build et
docker build -t goru-backend:dev --target development ./backend

# Development ortamını başlat
docker-compose up -d

# Logları görüntüle
docker-compose logs -f backend
```

### Production Ortamı

```bash
# Production image'ını build et
docker build -t goru-backend:prod --target production ./backend

# Production ortamını başlat
docker-compose -f docker-compose.prod.yml up -d

# Logları görüntüle
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Test Ortamı

```bash
# Test image'ını build et
docker build -t goru-backend:test --target test ./backend

# Testleri çalıştır
docker-compose --profile test up test --build --abort-on-container-exit
```

## 📊 Environment Değişkenleri

### Development
- `ENVIRONMENT=development`
- `DEBUG=true`
- `LOG_LEVEL=DEBUG`
- `PYTHONPATH=/app`

### Production
- `ENVIRONMENT=production`
- `DEBUG=false`
- `LOG_LEVEL=INFO`
- `WORKERS=4`

## 🔍 Health Check Endpoints

- **Development**: `http://localhost:8000/health`
- **Production**: `http://localhost:8000/health`

## 📈 Resource Limits

### Development
- **Backend**: 1GB memory limit, 512MB reservation
- **Database**: 512MB memory limit, 256MB reservation

### Production
- **Backend**: 2GB memory limit, 1GB reservation, 2 CPU cores
- **Database**: 1GB memory limit, 512MB reservation, 1 CPU core

## 🛠️ Troubleshooting

### Container Başlatılamıyor
```bash
# Container loglarını kontrol et
docker-compose logs backend

# Container durumunu kontrol et
docker-compose ps
```

### Database Bağlantı Hatası
```bash
# Database container'ının çalıştığını kontrol et
docker-compose ps db

# Database loglarını kontrol et
docker-compose logs db
```

### Memory Sorunları
```bash
# Docker resource kullanımını kontrol et
docker stats

# Gereksiz container'ları temizle
.\build.ps1 cleanup
```

## 🔒 Güvenlik Özellikleri

1. **Non-root kullanıcı**: Container'lar root olmayan kullanıcı ile çalışır
2. **Resource limits**: Memory ve CPU limitleri
3. **Health checks**: Otomatik sağlık kontrolü
4. **Environment separation**: Development ve production ortamları ayrı

## 📝 Log Yapılandırması

### Development
- Log seviyesi: DEBUG
- Hot reload aktif
- Detaylı hata mesajları

### Production
- Log seviyesi: INFO
- Worker processes (4 worker)
- Optimized logging

## 🧪 Test Yapılandırması

```bash
# Test coverage ile çalıştır
docker-compose --profile test up test --build --abort-on-container-exit

# Test sonuçlarını görüntüle
docker-compose logs test
```

## 📦 Image Boyutları

- **Development**: ~500MB (tüm development araçları dahil)
- **Production**: ~300MB (sadece gerekli dosyalar)
- **Test**: ~450MB (test araçları dahil)

## 🔄 Update ve Maintenance

### Image'ları Güncelle
```bash
# Tüm image'ları yeniden build et
.\build.ps1 build-all

# Eski image'ları temizle
.\build.ps1 cleanup
```

### Database Migration
```bash
# Migration'ları çalıştır
docker-compose exec backend alembic upgrade head
```

## 📞 Destek

Herhangi bir sorun yaşarsanız:

1. Container loglarını kontrol edin
2. Health check endpoint'lerini test edin
3. Resource kullanımını kontrol edin
4. Docker daemon'ın çalıştığından emin olun 