# GORU ERP Backend - API Kullanım Dokümantasyonu

## 📋 İçindekiler

1. [Genel Bakış](#genel-bakış)
2. [Authentication](#authentication)
3. [Kullanıcı İşlemleri](#kullanıcı-işlemleri)
4. [Stok İşlemleri](#stok-işlemleri)
5. [Sipariş İşlemleri](#sipariş-işlemleri)
6. [Mock API Sistemi](#mock-api-sistemi)
7. [Hata Kodları](#hata-kodları)
8. [Test Örnekleri](#test-örnekleri)

## 🔍 Genel Bakış

GORU ERP Backend, FastAPI tabanlı bir REST API'dir. Aşağıdaki temel özellikleri sağlar:

- **Authentication**: JWT token tabanlı kimlik doğrulama
- **CRUD Operations**: Kullanıcı, stok ve sipariş yönetimi
- **Database**: PostgreSQL ve SQLite desteği
- **Middleware**: Logging, rate limiting, security headers
- **Mock System**: Geliştirme ve test için mock API'lar

### Base URL
```
http://localhost:8000
```

### API Versiyonu
```
/api/v1
```

## 🔐 Authentication

### Login
```http
POST /api/v1/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Başarılı Yanıt (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "username": "admin",
    "role": "admin",
    "permissions": ["read", "write", "delete", "admin"]
  }
}
```

**Hata Yanıtı (401):**
```json
{
  "detail": "Geçersiz kullanıcı adı veya şifre / Invalid username or password"
}
```

### Test Kullanıcıları
- **Admin**: `admin` / `admin123`
- **User**: `user` / `user123`

### Authorization Header
Tüm korumalı endpoint'ler için Authorization header'ı gereklidir:
```http
Authorization: Bearer <access_token>
```

## 👥 Kullanıcı İşlemleri

### Kullanıcı Oluşturma
```http
POST /api/v1/users/
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "name": "Test User",
  "email": "test@example.com",
  "password": "test123",
  "role": "customer",
  "is_active": true
}
```

**Başarılı Yanıt (201):**
```json
{
  "id": 1,
  "name": "Test User",
  "email": "test@example.com",
  "role": "customer",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### Kullanıcı Listesi
```http
GET /api/v1/users/
Authorization: Bearer <TOKEN>
```

**Başarılı Yanıt (200):**
```json
[
  {
    "id": 1,
    "name": "Test User",
    "email": "test@example.com",
    "role": "customer",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

### Kullanıcı Detayı
```http
GET /api/v1/users/{user_id}
Authorization: Bearer <TOKEN>
```

### Kullanıcı Güncelleme
```http
PUT /api/v1/users/{user_id}
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "name": "Updated User Name",
  "email": "updated@example.com"
}
```

### Kullanıcı Silme
```http
DELETE /api/v1/users/{user_id}
Authorization: Bearer <TOKEN>
```

**Başarılı Yanıt (204):** Boş yanıt

## 📦 Stok İşlemleri

### Stok Oluşturma
```http
POST /api/v1/stocks/
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "product_name": "Test Product",
  "quantity": 50,
  "unit_price": 25.0,
  "category": "Electronics",
  "supplier": "Test Supplier"
}
```

**Başarılı Yanıt (201):**
```json
{
  "id": 1,
  "product_name": "Test Product",
  "quantity": 50,
  "unit_price": 25.0,
  "category": "Electronics",
  "supplier": "Test Supplier",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### Stok Listesi
```http
GET /api/v1/stocks/
Authorization: Bearer <TOKEN>
```

### Stok Detayı
```http
GET /api/v1/stocks/{stock_id}
Authorization: Bearer <TOKEN>
```

### Stok Güncelleme
```http
PUT /api/v1/stocks/{stock_id}
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "quantity": 75,
  "unit_price": 30.0
}
```

### Stok Silme
```http
DELETE /api/v1/stocks/{stock_id}
Authorization: Bearer <TOKEN>
```

## 🛒 Sipariş İşlemleri

### Sipariş Oluşturma
```http
POST /api/v1/orders/
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "user_id": 1,
  "product_name": "Test Product",
  "amount": 100.0
}
```

**Başarılı Yanıt (201):**
```json
{
  "id": 1,
  "user_id": 1,
  "total_amount": 100.0,
  "status": "pending",
  "product_name": "Test Product",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### Sipariş Listesi
```http
GET /api/v1/orders/
Authorization: Bearer <TOKEN>
```

### Sipariş Detayı
```http
GET /api/v1/orders/{order_id}
Authorization: Bearer <TOKEN>
```

### Sipariş Güncelleme
```http
PUT /api/v1/orders/{order_id}
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "product_name": "Updated Product",
  "amount": 150.0,
  "status": "shipped"
}
```

### Sipariş Silme
```http
DELETE /api/v1/orders/{order_id}
Authorization: Bearer <TOKEN>
```

## 🎭 Mock API Sistemi

Mock API sistemi, geliştirme ve test süreçlerinde gerçek veritabanı bağımlılığını ortadan kaldırmak için kullanılır.

### Mock Modu Etkinleştirme
```env
USE_MOCK=true
MOCK_API_PREFIX=/mock
```

### Mock Endpoint'leri

#### Mock Kullanıcılar
```http
GET /mock/users              # Mock kullanıcı listesi
GET /mock/users/{id}         # Mock kullanıcı detayı
POST /mock/users             # Mock kullanıcı oluşturma
PUT /mock/users/{id}         # Mock kullanıcı güncelleme
DELETE /mock/users/{id}      # Mock kullanıcı silme
```

#### Mock Stoklar
```http
GET /mock/stocks             # Mock stok listesi
GET /mock/stocks/{id}        # Mock stok detayı
POST /mock/stocks            # Mock stok oluşturma
PUT /mock/stocks/{id}        # Mock stok güncelleme
DELETE /mock/stocks/{id}     # Mock stok silme
```

#### Mock Siparişler
```http
GET /mock/orders             # Mock sipariş listesi
GET /mock/orders/{id}        # Mock sipariş detayı
POST /mock/orders            # Mock sipariş oluşturma
PUT /mock/orders/{id}        # Mock sipariş güncelleme
DELETE /mock/orders/{id}     # Mock sipariş silme
```

### Mock Veri Örneği
```json
{
  "users": [
    {
      "id": 1,
      "name": "Mock User 1",
      "email": "mock1@example.com",
      "role": "customer"
    }
  ],
  "stocks": [
    {
      "id": 1,
      "product_name": "Mock Product 1",
      "quantity": 100,
      "unit_price": 25.0
    }
  ],
  "orders": [
    {
      "id": 1,
      "user_id": 1,
      "total_amount": 100.0,
      "status": "pending"
    }
  ]
}
```

## ❌ Hata Kodları

### HTTP Status Kodları

| Kod | Açıklama | Kullanım |
|-----|----------|----------|
| 200 | OK | Başarılı GET, PUT, PATCH |
| 201 | Created | Başarılı POST |
| 204 | No Content | Başarılı DELETE |
| 400 | Bad Request | Geçersiz istek verisi |
| 401 | Unauthorized | Kimlik doğrulama gerekli |
| 403 | Forbidden | Yetkisiz erişim |
| 404 | Not Found | Kaynak bulunamadı |
| 422 | Unprocessable Entity | Validasyon hatası |
| 429 | Too Many Requests | Rate limit aşıldı |
| 500 | Internal Server Error | Sunucu hatası |

### Hata Yanıt Formatları

#### 401 Unauthorized
```json
{
  "detail": "Missing authentication token"
}
```

#### 400 Bad Request
```json
{
  "detail": "Bu e-posta zaten kayıtlı. / Email already registered."
}
```

#### 404 Not Found
```json
{
  "detail": "Kullanıcı bulunamadı. / User not found."
}
```

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### 429 Rate Limit
```json
{
  "error": true,
  "message": "Rate limit exceeded. Please try again later."
}
```

## 🧪 Test Örnekleri

### cURL Komutları

#### Authentication
```bash
# Login
curl -X POST "http://localhost:8000/api/v1/login/" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Token'ı değişkene ata
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

#### Kullanıcı İşlemleri
```bash
# Kullanıcı oluştur
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "test123"
  }'

# Kullanıcı listesi
curl -X GET "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer $TOKEN"

# Kullanıcı detayı
curl -X GET "http://localhost:8000/api/v1/users/1" \
  -H "Authorization: Bearer $TOKEN"
```

#### Stok İşlemleri
```bash
# Stok oluştur
curl -X POST "http://localhost:8000/api/v1/stocks/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Test Product",
    "quantity": 50,
    "unit_price": 25.0
  }'

# Stok listesi
curl -X GET "http://localhost:8000/api/v1/stocks/" \
  -H "Authorization: Bearer $TOKEN"
```

#### Sipariş İşlemleri
```bash
# Sipariş oluştur
curl -X POST "http://localhost:8000/api/v1/orders/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "product_name": "Test Product",
    "amount": 100.0
  }'

# Sipariş listesi
curl -X GET "http://localhost:8000/api/v1/orders/" \
  -H "Authorization: Bearer $TOKEN"
```

### Python Requests Örnekleri

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000/api/v1"

# Login
def login(username="admin", password="admin123"):
    response = requests.post(f"{BASE_URL}/login/", json={
        "username": username,
        "password": password
    })
    return response.json()["access_token"]

# Token al
token = login()
headers = {"Authorization": f"Bearer {token}"}

# Kullanıcı oluştur
def create_user(name, email, password):
    response = requests.post(f"{BASE_URL}/users/", 
                           headers=headers,
                           json={
                               "name": name,
                               "email": email,
                               "password": password
                           })
    return response.json()

# Stok oluştur
def create_stock(product_name, quantity, unit_price):
    response = requests.post(f"{BASE_URL}/stocks/",
                           headers=headers,
                           json={
                               "product_name": product_name,
                               "quantity": quantity,
                               "unit_price": unit_price
                           })
    return response.json()

# Sipariş oluştur
def create_order(user_id, product_name, amount):
    response = requests.post(f"{BASE_URL}/orders/",
                           headers=headers,
                           json={
                               "user_id": user_id,
                               "product_name": product_name,
                               "amount": amount
                           })
    return response.json()

# Örnek kullanım
user = create_user("Test User", "test@example.com", "test123")
stock = create_stock("Test Product", 50, 25.0)
order = create_order(user["id"], "Test Product", 100.0)
```

### JavaScript/Fetch Örnekleri

```javascript
// Base URL
const BASE_URL = 'http://localhost:8000/api/v1';

// Login
async function login(username = 'admin', password = 'admin123') {
    const response = await fetch(`${BASE_URL}/login/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password })
    });
    const data = await response.json();
    return data.access_token;
}

// Token al
const token = await login();
const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
};

// Kullanıcı oluştur
async function createUser(name, email, password) {
    const response = await fetch(`${BASE_URL}/users/`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ name, email, password })
    });
    return await response.json();
}

// Stok oluştur
async function createStock(productName, quantity, unitPrice) {
    const response = await fetch(`${BASE_URL}/stocks/`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
            product_name: productName,
            quantity,
            unit_price: unitPrice
        })
    });
    return await response.json();
}

// Sipariş oluştur
async function createOrder(userId, productName, amount) {
    const response = await fetch(`${BASE_URL}/orders/`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
            user_id: userId,
            product_name: productName,
            amount
        })
    });
    return await response.json();
}

// Örnek kullanım
const user = await createUser('Test User', 'test@example.com', 'test123');
const stock = await createStock('Test Product', 50, 25.0);
const order = await createOrder(user.id, 'Test Product', 100.0);
```

## 📊 Swagger UI

API dokümantasyonuna erişmek için:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Bu sayfalar interaktif API dokümantasyonu sağlar ve endpoint'leri test etmenize olanak tanır.

---

**Son Güncelleme:** Güncel  
**API Versiyonu:** v1  
**Base URL:** http://localhost:8000  
**Dokümantasyon:** http://localhost:8000/docs 