# Environment Setup Guide

## 🎯 Database Seçimi

### Test Ortamı (SQLite)
```bash
# Test ortamında SQLite kullan
export ENVIRONMENT=test
export TESTING=1
python -m pytest app/tests/
```

### Development Ortamı (SQLite)
```bash
# Development ortamında SQLite kullan (hızlı geliştirme)
export ENVIRONMENT=development
python app/main.py
```

### Production Ortamı (PostgreSQL)
```bash
# Production ortamında PostgreSQL kullan
export ENVIRONMENT=production
export DATABASE_URL=postgresql://user:pass@localhost:5432/db
python app/main.py
```

## 🔄 Migration Süreci

### 1. Development'tan Production'a Geçiş
```bash
# Migration script'ini çalıştır
cd backend
python -m app.scripts.migrate_to_postgresql

# Migration'ı doğrula
python -m app.scripts.migrate_to_postgresql --verify
```

### 2. Environment Variables
```bash
# .env dosyası
ENVIRONMENT=production
DATABASE_URL=postgresql://goru:goru@localhost:5432/goru_db
DEBUG=false
```

## 📊 Database Karşılaştırması

| Özellik | SQLite (Test/Dev) | PostgreSQL (Production) |
|---------|-------------------|------------------------|
| **Hız** | ⚡ Çok hızlı | 🐌 Yavaş (setup) |
| **Kurulum** | 📦 Basit | 🔧 Karmaşık |
| **Concurrent** | ❌ Tek kullanıcı | ✅ Çoklu kullanıcı |
| **ACID** | ✅ Tam | ✅ Tam |
| **Backup** | 📁 Dosya kopyala | 🗄️ pg_dump |
| **Scale** | ❌ Sınırlı | ✅ Büyük ölçek |

## 🚀 Production Deployment

### 1. PostgreSQL Kurulumu
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows
# PostgreSQL installer kullan
```

### 2. Database Oluşturma
```sql
CREATE DATABASE goru_db;
CREATE USER goru WITH PASSWORD 'goru';
GRANT ALL PRIVILEGES ON DATABASE goru_db TO goru;
```

### 3. Environment Setup
```bash
# Production environment
export ENVIRONMENT=production
export DATABASE_URL=postgresql://goru:goru@localhost:5432/goru_db
export DEBUG=false
export SECRET_KEY=your-production-secret-key
```

## 🔧 Test vs Production Farkları

### Test Ortamı
- ✅ SQLite (hızlı)
- ✅ In-memory database
- ✅ Otomatik cleanup
- ✅ Basit setup

### Production Ortamı
- ✅ PostgreSQL (güçlü)
- ✅ Persistent storage
- ✅ Backup/restore
- ✅ Connection pooling
- ✅ ACID compliance

## 📈 Performance Monitoring

### SQLite Performance
```python
# Test ortamında performans
import time
start = time.time()
# Test işlemleri
end = time.time()
print(f"Test süresi: {end - start:.2f}s")
```

### PostgreSQL Performance
```python
# Production ortamında performans
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM users"))
    print(f"Kullanıcı sayısı: {result.scalar()}")
```

## 🛡️ Security Considerations

### Test Ortamı
- ✅ Basit authentication
- ✅ Local file access
- ✅ Development secrets

### Production Ortamı
- ✅ Strong authentication
- ✅ Network security
- ✅ Environment secrets
- ✅ SSL/TLS encryption

## 📝 Migration Checklist

- [ ] PostgreSQL kurulumu
- [ ] Database oluşturma
- [ ] User/permission ayarları
- [ ] Environment variables
- [ ] Migration script çalıştırma
- [ ] Data verification
- [ ] Performance testing
- [ ] Backup strategy
- [ ] Monitoring setup 