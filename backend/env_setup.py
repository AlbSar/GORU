#!/usr/bin/env python3
"""
Environment Setup Script
.env dosyasını oluşturmak için kullanılır
"""



def create_env_file():
    """Settings.py ile uyumlu .env dosyası oluşturur."""

    env_content = """# GORU ERP Backend - Environment Variables
# ======================================

# Database Configuration
DATABASE_URL=postgresql://goru:goru@localhost:5432/goru_db
TEST_DATABASE_URL=postgresql://goru:goru@localhost:5432/goru_test_db

# Application Configuration
DEBUG=true
SECRET_KEY=your-secret-key-here-change-in-production
API_V1_STR=/api/v1
PROJECT_NAME=GORU ERP Backend

# CORS Configuration
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Environment Configuration
APP_ENV=development
LOG_LEVEL=debug

# Mock System Configuration
USE_MOCK=false
MOCK_API_PREFIX=/mock

# Security Configuration
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
"""

    with open("../.env", "w", encoding="utf-8") as f:
        f.write(env_content)

    print("✅ Proje kökündeki .env dosyası güncellendi!")
    print("📝 Lütfen DATABASE_URL ve SECRET_KEY değerlerini güncelleyin.")


if __name__ == "__main__":
    create_env_file()
