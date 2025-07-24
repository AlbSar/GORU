[![Build Status](https://github.com/AlbSar/GORU/actions/workflows/ci.yml/badge.svg)](https://github.com/AlbSar/GORU/actions)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)](https://github.com/AlbSar/GORU)

# GORU ERP Backend

GORU ERP projesi için FastAPI, React ve PostgreSQL tabanlı backend uygulaması.

... (devamı mevcut README içeriğiyle birleştirilecek)

Aşağıda, **local geliştirme ve test** odaklı bir yol haritası, kopyalanabilir kod örnekleri ve ileriye dönük otomasyon için rehber bulacaksınız.

---

## 1. **Docker Image Build & Test (Local Build + Container İçinde Test)**

### a) **Github Actions Adımı (ci.yml)**
`.github/workflows/ci.yml` dosyanıza ekleyin:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-test:
    runs-on: ubuntu-latest
    steps:
      - name: Kodu checkout et
        uses: actions/checkout@v4

      - name: Docker image build (local)
        run: |
          docker build -t goru-backend-test:ci -f backend/Dockerfile .

      - name: Docker container içinde testleri çalıştır
        run: |
          docker run --rm goru-backend-test:ci pytest --cov=app --cov-report=xml
```
**Açıklama:**  
- Her push/pull request’te image local olarak build edilir.
- Testler, image içinde (container’da) çalıştırılır.
- Otomatik deployment veya push adımı yoktur.

---

## 2. **Kapsamlı Otomasyon için Hazırlık (Sadece CI)**

### a) **README.md’ye Badge Ekle**
README.md dosyanın en üstüne ekle:

```markdown
[![Build Status](https://github.com/<kullanici>/<repo>/actions/workflows/ci.yml/badge.svg)](https://github.com/<kullanici>/<repo}/actions)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)](https://github.com/<kullanici>/<repo})
```
> **Not:** `<kullanici>` ve `<repo>` kısımlarını kendi Github kullanıcı adı ve repo adınızla değiştirin.

---

## 3. **İleriye Dönük Otomasyon (Otomatik Deploy’a Hazırlık)**

### a) **Gelecekte Otomatik Deploy Eklemek için Template**
- SSH ile sunucuya bağlanıp deploy etmek için aşağıdaki job’u CI pipeline’ınıza kolayca ekleyebilirsiniz:

```yaml
  deploy:
    needs: build-test
    runs-on: ubuntu-latest
    steps:
      - name: Sunucuya SSH ile bağlan ve deploy et
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            docker pull <dockerhub_kullanici>/goru-backend:latest
            cd /path/to/your/app
            docker-compose up -d
```
> **Not:** Bu adımı şimdilik eklemeyin, sadece ileride kolayca entegre edebilirsiniz.

---

## 4. **Debug ve Geliştirme Kolaylığı**

### a) **Localde Testleri Tekrar Koşturmak için Komutlar**
- Sanal ortamda:
  ```sh
  cd backend
  pip install -r requirements.txt
  pytest --cov=app --cov-report=term-missing
  ```
- Docker ile:
  ```sh
  docker build -t goru-backend-test:local -f backend/Dockerfile .
  docker run --rm goru-backend-test:local pytest --cov=app --cov-report=term-missing
  ```

### b) **Docker Compose ile Local Test Ortamı**
`docker-compose.yml` örneği (proje köküne):

```yaml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: goru
      POSTGRES_PASSWORD: goru
      POSTGRES_DB: goru_db
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    environment:
      DATABASE_URL: postgresql://goru:goru@db:5432/goru_db
    depends_on:
      - db
    ports:
      - "8000:8000"
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000

volumes:
  pgdata:
```
**Kullanım:**
```sh
docker-compose up --build
```
- Testleri container içinde çalıştırmak için:
  ```sh
  docker-compose run backend pytest --cov=app --cov-report=term-missing
  ```

---

## 5. **Ekstra: Gelecekte Otomatik Deploy için Not**
- SSH ile deploy job’unu eklemek için sadece secrets ve sunucu ayarlarını eklemeniz yeterli.
- Docker image push ve sunucuya çekme adımlarını pipeline’a ekleyebilirsiniz (örnek yukarıda).

---

### **Özet**
- **ci.yml**: Sadece build ve test (deployment yok).
- **README.md**: Build ve coverage badge.
- **docker-compose.yml**: Local geliştirme ve test ortamı.
- **Gelecekte**: SSH deploy job’u kolayca eklenebilir.

Her adımda hata alırsanız, hata mesajını paylaşın, hızlıca debug için yardımcı olabilirim!
