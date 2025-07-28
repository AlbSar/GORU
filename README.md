[![CI](https://github.com/AlbSar/GORU/actions/workflows/ci.yml/badge.svg)](https://github.com/AlbSar/GORU/actions)
[![Coverage](https://codecov.io/gh/AlbSar/GORU/branch/main/graph/badge.svg)](https://codecov.io/gh/AlbSar/GORU)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Coverage](https://img.shields.io/badge/coverage-75%25-brightgreen)](https://github.com/AlbSar/GORU)

# GORU ERP Backend

Bu proje, gerçek bir ekip çalışması ve yazılım geliştirme sürecinin tüm iniş çıkışlarını yansıtan, FastAPI tabanlı bir ERP backend uygulamasıdır. Projeyi geliştirirken hem teknik hem de pratik birçok zorlukla karşılaştık ve her adımda gerçek bir insan dokunuşu ve öğrenme süreci yaşandı.

## 🚀 Hızlı Başlangıç

1. Repoyu klonlayın:
   ```sh
   git clone https://github.com/AlbSar/GORU.git
   cd GORU
   ```
2. Localde PostgreSQL başlatın veya Docker Compose ile tüm ortamı ayağa kaldırın:
   ```sh
   docker-compose up --build
   ```
3. API dokümantasyonu için:
   - [http://localhost:8000/docs](http://localhost:8000/docs)

## 🧪 Testler

### Test Coverage Durumu
- **Genel Coverage**: %75 (hedef %90+)
- **Auth Module**: %90 ✅
- **Routes Module**: %75 🔄
- **Database Module**: %48 (hedef %90+)
- **Utils & Scripts**: %90+ ✅

### Test Çalıştırma
```bash
# Localde testleri çalıştırmak için:
cd backend
pip install -r requirements.txt
pytest --cov=app --cov-report=term-missing

# Kapsamlı test suite'i çalıştırma:
pytest app/tests/test_routes_coverage_90.py -v --cov=app.routes --cov-report=term-missing

# Docker ile test:
docker build -t goru-backend-test:local -f backend/Dockerfile backend
docker run --rm -e DATABASE_URL=postgresql://<USER>:<PASSWORD>@localhost:5432/<DB> goru-backend-test:local pytest --cov=app --cov-report=term-missing
```

### Test Kategorileri
- **CRUD Operations**: 18 test (create, read, update, delete)
- **Error Handling**: 16 test (422, 400, 500 errors)
- **Auth & Permission**: 12 test (401, 403, token validation)
- **Transaction & Rollback**: 5 test (database transactions)
- **Database Constraints**: 7 test (unique, foreign key, not null)
- **Integration Tests**: 6 test (end-to-end scenarios)
- **Edge Cases**: 6 test (large data, special chars)

### Mock API Sistemi

Geliştirme ve test süreçlerinde gerçek veritabanı bağımlılığını ortadan kaldırmak için mock API sistemi:

```bash
# Mock modu etkin
export USE_MOCK=true

# Mock endpoint'leri:
# GET /mock/users - Mock kullanıcı listesi
# GET /mock/orders - Mock sipariş listesi  
# GET /mock/stocks - Mock stok listesi
# Tüm CRUD operasyonları desteklenir
```

## 🔧 Linting ve Code Quality

```bash
# Kod formatlaması
black backend/app/ --line-length 88
isort backend/app/ --profile black

# Linting kontrolü  
flake8 backend/app/
ruff check backend/app/

# Pre-commit hooks (otomatik olarak çalışır)
pre-commit run --all-files
```

## 📊 CI/CD ve Otomasyon

Github Actions pipeline'ında testler için izole bir PostgreSQL servisi otomatik olarak başlatılır. Test container'ı bu veritabanına `localhost` üzerinden bağlanır. Localde ise kendi veritabanı ayarınızla çalışabilirsiniz.

Örnek `.github/workflows/ci.yml`:
```yaml
jobs:
  build-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: <USER>
          POSTGRES_PASSWORD: <PASSWORD>
          POSTGRES_DB: <DB>
        ports:
          - 5432:5432
        options: >-
          --health-cmd="pg_isready -U <USER>"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5
    steps:
      - name: Kodu checkout et
        uses: actions/checkout@v4
      - name: Docker image build (local)
        run: |
          docker build -t goru-backend-test:ci -f backend/Dockerfile backend
      - name: Docker container içinde testleri çalıştır
        env:
          DATABASE_URL: postgresql://<USER>:<PASSWORD>@localhost:5432/<DB>
        run: |
          docker run --rm -e DATABASE_URL=${DATABASE_URL} goru-backend-test:ci pytest --cov=app --cov-report=xml
```

## 🔐 API Örnekleri

### Kullanıcı İşlemleri
```http
# Kullanıcı oluşturma
POST /api/v1/users/
Content-Type: application/json
Authorization: Bearer <TOKEN>
{
  "name": "Test User",
  "email": "test@example.com",
  "password": "test123"
}

# Kullanıcı listesi
GET /api/v1/users/
Authorization: Bearer <TOKEN>
```

### Sipariş İşlemleri
```http
# Sipariş oluşturma
POST /api/v1/orders/
Content-Type: application/json
Authorization: Bearer <TOKEN>
{
  "user_id": 1,
  "product_name": "Test Product",
  "amount": 100.0
}

# Sipariş listesi
GET /api/v1/orders/
Authorization: Bearer <TOKEN>
```

### Stok İşlemleri
```http
# Stok oluşturma
POST /api/v1/stocks/
Content-Type: application/json
Authorization: Bearer <TOKEN>
{
  "product_name": "Test Product",
  "quantity": 50,
  "unit_price": 25.0
}

# Stok listesi
GET /api/v1/stocks/
Authorization: Bearer <TOKEN>
```

### Hata Kodları
- **401**: Yetkisiz erişim (Unauthorized)
- **403**: Erişim reddedildi (Forbidden)
- **404**: Kaynak bulunamadı (Not Found)
- **422**: Eksik veya hatalı veri (Unprocessable Entity)
- **500**: Sunucu hatası (Internal Server Error)

## 📈 Test Coverage Hedefleri

### Sprint 3 Coverage Durumu
- **Auth Module**: %90 ✅ (28 Temmuz 2025'te tamamlandı)
- **Routes Module**: %75 🔄 (hedef %90+)
- **Database Module**: %48 (hedef %90+)
- **Utils & Scripts**: %90+ ✅
- **Mock Router**: %100 ✅

### Test Başarı Oranları
- **Error Handling**: %93.8 (15/16 test)
- **Edge Cases**: %100 (6/6 test)
- **Integration Tests**: %66.7 (4/6 test)
- **Auth & Permission**: %50 (6/12 test)
- **CRUD Operations**: %33.3 (6/18 test)

## 📋 Son Güncellemeler (28 Temmuz 2025)

### ✅ Tamamlanan İşler
- **Routes Coverage Test Suite**: 69 test senaryosu oluşturuldu
- **Endpoint Path Düzeltmeleri**: Tüm path'ler `/api/v1/` prefix'i ile güncellendi
- **Test Kategorileri**: 7 ana kategori tamamlandı
- **Error Handling**: %93.8 başarı oranı
- **Edge Cases**: %100 başarı oranı

### 🔄 Devam Eden İşler
- **Fixture Sorunları**: 15 test düzeltilmesi gerekiyor
- **Auth Testleri**: 6 test düzeltilmesi gerekiyor
- **Transaction Testleri**: 3 test düzeltilmesi gerekiyor
- **Integration Testleri**: 2 test düzeltilmesi gerekiyor

### 📊 Oluşturulan Dosyalar
- `test_routes_coverage_90.py`: Ana test dosyası (69 test)
- `fix_paths.py`: Path düzeltme script'i
- `COVERAGE_REPORT_90.md`: Detaylı coverage raporu
- `calisma_notu_28072025_gunluk.md`: Günlük çalışma notu

## 🎯 Sonraki Adımlar

### Kısa Vadeli (1-2 saat)
1. **Fixture Sorunlarını Düzelt** (15 test)
2. **Auth Testlerini Düzelt** (6 test)
3. **Transaction Testlerini Düzelt** (3 test)

### Orta Vadeli (3-4 saat)
1. **Integration Testlerini Düzelt** (2 test)
2. **Validation Testlerini Düzelt** (3 test)
3. **Eksik Coverage Alanlarını Test Et** (46 satır)

### Uzun Vadeli (1 gün)
1. **%90+ Coverage Hedefine Ulaş**
2. **Performance Testleri Ekle**
3. **Security Testleri Ekle**

## 📚 Dokümantasyon

- **API Dokümantasyonu**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Test Coverage Raporu**: `COVERAGE_REPORT_90.md`
- **Günlük Çalışma Notu**: `calisma_notu_28072025_gunluk.md`
- **Sprint 3 Durumu**: `calisma/sprint3.txt`

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📝 Notlar

- Kod kalitesi ve test kapsamı otomatik olarak CI pipeline'ında kontrol edilir.
- Tüm önemli geliştirme ve otomasyon adımları README ve calisma_notu.md dosyalarında açıklanmıştır.
- Herhangi bir adımda hata alırsanız, hata mesajını paylaşın; birlikte çözüm bulabiliriz!
- Test coverage'ı %90+ hedefine ulaşmak için aktif çalışma devam etmektedir.

---

**Son Güncelleme:** 28 Temmuz 2025  
**Test Coverage:** %75 (hedef %90+)  
**Test Sayısı:** 69 test (40 başarılı, 29 başarısız)  
**Sprint 3 Durumu:** 🔄 Devam ediyor
