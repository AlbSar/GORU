[![CI](https://github.com/AlbSar/GORU/actions/workflows/ci.yml/badge.svg)](https://github.com/AlbSar/GORU/actions)
[![Coverage](https://codecov.io/gh/AlbSar/GORU/branch/main/graph/badge.svg)](https://codecov.io/gh/AlbSar/GORU)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)](https://github.com/AlbSar/GORU)

# GORU ERP Backend

Bu proje, gerçek bir ekip çalışması ve yazılım geliştirme sürecinin tüm iniş çıkışlarını yansıtan, FastAPI tabanlı bir ERP backend uygulamasıdır. Projeyi geliştirirken hem teknik hem de pratik birçok zorlukla karşılaştık ve her adımda gerçek bir insan dokunuşu ve öğrenme süreci yaşandı.

## Hızlı Başlangıç

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

## Testler

- Localde testleri çalıştırmak için:
  ```sh
  cd backend
  pip install -r requirements.txt
  pytest --cov=app --cov-report=term-missing
  ```
- Docker ile test:
  ```sh
  docker build -t goru-backend-test:local -f backend/Dockerfile backend
  docker run --rm -e DATABASE_URL=postgresql://<USER>:<PASSWORD>@localhost:5432/<DB> goru-backend-test:local pytest --cov=app --cov-report=term-missing

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

### Linting ve Code Quality

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
  ```

## CI/CD ve Otomasyon

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

## API Örnekleri

- Kullanıcı oluşturma:
  ```http
  POST /users/
  Content-Type: application/json
  Authorization: Bearer <TOKEN>
  {
    "name": "Test User",
    "email": "test@example.com",
    "password": "test123"
  }
  ```
- Hata kodları:
  - 401: Yetkisiz erişim
  - 422: Eksik veya hatalı veri
  - 404: Kaynak bulunamadı

## Notlar
- Kod kalitesi ve test kapsamı otomatik olarak CI pipeline'ında kontrol edilir.
- Tüm önemli geliştirme ve otomasyon adımları README ve calisma_notu.md dosyalarında açıklanmıştır.
- Herhangi bir adımda hata alırsanız, hata mesajını paylaşın; birlikte çözüm bulabiliriz!
