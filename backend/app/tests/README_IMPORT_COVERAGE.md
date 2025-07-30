# Import Coverage Test

Bu test, projedeki tüm modüllerin import edilebilirliğini kontrol eder ve CI/CD pipeline'da zorunlu olarak çalışır.

## 🎯 Amaç

- Tüm modül ve klasörlerin test ortamında import edilebildiğini doğrular
- Import hatalarını erken tespit eder
- CI/CD pipeline'da bu testin çalışmasını zorunlu kılar

## 📋 Test Kapsamı

### Test Edilen Modüller

#### Ana Modüller
- `app.main` - FastAPI uygulaması
- `app.auth` - Kimlik doğrulama modülü
- `app.database` - Veritabanı bağlantısı
- `app.models` - SQLAlchemy modelleri
- `app.schemas` - Pydantic şemaları
- `app.mock_routes` - Mock route'lar
- `app.mock_services` - Mock servisler

#### Core Modülleri
- `app.core.security` - Güvenlik fonksiyonları
- `app.core.settings` - Uygulama ayarları

#### Route Modülleri
- `app.routes.common` - Ortak route fonksiyonları
- `app.routes.users` - Kullanıcı route'ları
- `app.routes.stocks` - Stok route'ları
- `app.routes.orders` - Sipariş route'ları

#### Interface Modülleri
- `app.interfaces.auth_interface` - Auth interface
- `app.interfaces.database_interface` - Database interface
- `app.interfaces.settings_interface` - Settings interface

#### Implementation Modülleri
- `app.implementations.auth_implementation` - Auth implementation

#### Middleware Modülleri
- `app.middleware.header_validation` - Header doğrulama
- `app.middleware.logging_middleware` - Logging middleware
- `app.middleware.rate_limiting` - Rate limiting
- `app.middleware.security_headers` - Güvenlik header'ları

#### Utility Modülleri
- `app.utils.anonymizer` - Veri anonimleştirme

#### Script Modülleri
- `app.scripts.create_tables` - Tablo oluşturma
- `app.scripts.generate_dummy_data` - Test verisi oluşturma
- `app.scripts.migrate_to_postgresql` - PostgreSQL migration
- `app.scripts.seed_demo_data` - Demo veri ekleme

## 🚀 Çalıştırma

### Tek Test Çalıştırma
```bash
cd backend
python -m pytest app/tests/test_import_coverage.py -v
```

### Tüm Import Testleri
```bash
cd backend
python -m pytest app/tests/test_import_coverage.py::test_import_coverage -v
```

### Kritik Modül Testleri
```bash
cd backend
python -m pytest app/tests/test_import_coverage.py::test_critical_modules -v
```

### Modül Attribute Testleri
```bash
cd backend
python -m pytest app/tests/test_import_coverage.py::test_module_attributes -v
```

## 📊 Test Sonuçları

### Başarılı Test Çıktısı
```
🔍 Testing import coverage for 35 modules...
============================================================
✅ PASS app
✅ PASS app.main
✅ PASS app.auth
...
✅ PASS app.scripts.seed_demo_data

============================================================
📊 IMPORT COVERAGE RESULTS
============================================================
Total modules tested: 35
Successful imports: 35
Failed imports: 0
Success rate: 100.00%
```

### Hata Durumunda
```
❌ FAIL app.scripts.seed_demo_data

❌ IMPORT ERRORS:
----------------------------------------
Module: app.scripts.seed_demo_data
Error Type: ImportError
Error Message: No module named 'models'
Details: Failed to import app.scripts.seed_demo_data: No module named 'models'
```

## 🔧 Sorun Giderme

### Yaygın Sorunlar

1. **Import Hatası**: `No module named 'models'`
   - **Çözüm**: Relative import kullanın: `from ..models import ...`

2. **Attribute Hatası**: `Module missing attribute`
   - **Çözüm**: Modülde eksik attribute'u ekleyin

3. **Database Hatası**: `no such table`
   - **Not**: Bu import testini etkilemez, sadece test temizleme sırasında oluşur

### Test Düzeltme Adımları

1. **Import hatası varsa**:
   ```python
   # Yanlış
   from models import User
   
   # Doğru
   from ..models import User
   ```

2. **Attribute eksikse**:
   ```python
   # schemas.py'de eksik attribute'u ekleyin
   class UserRead(BaseModel):
       id: int
       name: str
       # ... diğer alanlar
   ```

3. **Test dosyasını güncelleyin**:
   ```python
   # test_import_coverage.py'de doğru attribute'ları kontrol edin
   'app.schemas': ['UserCreate', 'UserRead'],  # UserResponse değil
   ```

## 🏗️ CI/CD Entegrasyonu

### GitHub Actions
- `.github/workflows/import-coverage.yml` dosyası otomatik olarak çalışır
- Her PR'da import testleri zorunlu olarak çalışır
- Başarısız import testleri PR'ı bloklar

### Yerel Geliştirme
```bash
# Pre-commit hook olarak ekleyin
cd backend
python -m pytest app/tests/test_import_coverage.py::test_import_coverage
```

## 📈 Metrikler

- **Toplam Modül Sayısı**: 35
- **Kritik Modüller**: 7
- **Route Modülleri**: 3
- **Middleware Modülleri**: 4
- **Utility Modülleri**: 1
- **Script Modülleri**: 4

## 🎯 Acceptance Kriterleri

- ✅ Hiçbir import hatası olmamalı
- ✅ Tüm modüller başarıyla import edilmeli
- ✅ Kritik modüller gerekli attribute'lara sahip olmalı
- ✅ Test %100 başarı oranına sahip olmalı
- ✅ CI/CD pipeline'da zorunlu olarak çalışmalı

## 🔄 Güncelleme

Yeni modül eklendiğinde:

1. `test_import_coverage.py` dosyasında `get_all_modules()` metoduna ekleyin
2. Gerekirse yeni test fonksiyonu ekleyin
3. Testi çalıştırın ve doğrulayın
4. CI/CD pipeline'da test edin 