#!/usr/bin/env python3
"""
Environment variables generator script.
Bu script güvenli secret key'ler oluşturur ve .env dosyası oluşturur.
"""

import secrets
import os
from pathlib import Path


def generate_secret_key(length: int = 32) -> str:
    """Güvenli bir secret key oluşturur."""
    return secrets.token_urlsafe(length)


def create_env_file():
    """Development için .env dosyası oluşturur."""
    
    # Güvenli secret key'ler oluştur
    secret_key = generate_secret_key(32)
    jwt_secret_key = generate_secret_key(32)
    
    env_content = f"""# =============================================================================
# GORU ERP Backend - Development Environment
# =============================================================================

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
# Development için güvenli secret key'ler
SECRET_KEY={secret_key}
JWT_SECRET_KEY={jwt_secret_key}
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
# Development için SQLite kullan
DATABASE_URL=sqlite:///./dev.db
TEST_DATABASE_URL=sqlite:///./test.db
DEV_DATABASE_URL=sqlite:///./dev.db
TEST_SQLITE_URL=sqlite:///./test.db

# =============================================================================
# CORS CONFIGURATION
# =============================================================================
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"]

# =============================================================================
# MIDDLEWARE CONFIGURATION
# =============================================================================
ENABLE_SECURITY_HEADERS=true
ENABLE_RATE_LIMITING=true
ENABLE_LOGGING_MIDDLEWARE=true

# Rate Limiting
DEFAULT_RATE_LIMIT=60
BURST_RATE_LIMIT=120
RATE_LIMIT_WINDOW=60

# Logging
LOG_REQUEST_BODY=true
LOG_RESPONSE_BODY=true
LOG_HEADERS=true
MAX_LOG_BODY_SIZE=10240

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

# =============================================================================
# AUTHENTICATION CONFIGURATION
# =============================================================================
# Development test token
VALID_TOKEN=test-token-12345
"""
    
    # .env dosyasını oluştur
    env_path = Path(".env")
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print("✅ .env dosyası oluşturuldu!")
    print(f"📁 Dosya konumu: {env_path.absolute()}")
    print(f"🔑 Secret Key: {secret_key}")
    print(f"🔑 JWT Secret Key: {jwt_secret_key}")
    print("\n⚠️  ÖNEMLİ: Bu dosyayı git'e commit etmeyin!")
    print("📝 .gitignore dosyasına .env ekleyin.")


def create_production_env():
    """Production için örnek .env dosyası oluşturur."""
    
    production_env_content = """# =============================================================================
# GORU ERP Backend - Production Environment
# =============================================================================
# Bu dosyayı production sunucusunda kullanın

# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================
APP_ENV=production
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================
# Production'da mutlaka değiştirin!
SECRET_KEY=CHANGE_THIS_IN_PRODUCTION
JWT_SECRET_KEY=CHANGE_THIS_IN_PRODUCTION
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
# Production PostgreSQL
DATABASE_URL=postgresql://username:password@localhost:5432/goru_db
TEST_DATABASE_URL=postgresql://username:password@localhost:5432/goru_test_db

# =============================================================================
# CORS CONFIGURATION
# =============================================================================
BACKEND_CORS_ORIGINS=["https://yourdomain.com", "https://api.yourdomain.com"]

# =============================================================================
# MIDDLEWARE CONFIGURATION
# =============================================================================
ENABLE_SECURITY_HEADERS=true
ENABLE_RATE_LIMITING=true
ENABLE_LOGGING_MIDDLEWARE=true

# Rate Limiting
DEFAULT_RATE_LIMIT=60
BURST_RATE_LIMIT=120
RATE_LIMIT_WINDOW=60

# Logging
LOG_REQUEST_BODY=false
LOG_RESPONSE_BODY=false
LOG_HEADERS=true
MAX_LOG_BODY_SIZE=10240

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

# =============================================================================
# AUTHENTICATION CONFIGURATION
# =============================================================================
# Production'da test token kullanmayın
VALID_TOKEN=
"""
    
    # .env.production dosyasını oluştur
    env_prod_path = Path(".env.production")
    with open(env_prod_path, "w", encoding="utf-8") as f:
        f.write(production_env_content)
    
    print("✅ .env.production dosyası oluşturuldu!")
    print(f"📁 Dosya konumu: {env_prod_path.absolute()}")
    print("\n⚠️  ÖNEMLİ: Production'da secret key'leri değiştirin!")


if __name__ == "__main__":
    print("🔧 Environment variables generator")
    print("=" * 50)
    
    # Development .env oluştur
    create_env_file()
    print()
    
    # Production .env oluştur
    create_production_env()
    print()
    
    print("🎉 Tamamlandı!")
    print("\n📋 Sonraki adımlar:")
    print("1. .env dosyasını kontrol edin")
    print("2. Uygulamayı test edin")
    print("3. Production'da secret key'leri değiştirin")
    print("4. .gitignore'a .env ekleyin") 