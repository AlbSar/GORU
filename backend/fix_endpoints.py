#!/usr/bin/env python3
"""
Test dosyalarındaki endpoint path'lerini düzeltmek ve auth header'ları eklemek için script.
"""

import glob
import os
import re


def fix_endpoints_in_file(file_path):
    """Tek dosyada endpoint path'lerini düzelt."""
    print(f"İşleniyor: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Eski path'leri yeni path'lerle değiştir
    patterns = [
        (r'"/api/v1/users/', '"/users/'),
        (r'"/api/v1/orders/', '"/orders/'),
        (r'"/api/v1/stocks/', '"/stocks/'),
        (r'"/api/v1/login/', '"/login/'),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    # Auth header'ı eksik olan endpoint'lere ekle
    # GET, POST, PUT, DELETE işlemlerinde header yoksa ekle
    auth_patterns = [
        # GET işlemleri
        (
            r'(client\.get\("/users/[^"]*")(?!\s*,\s*headers)',
            r"\1, headers=auth_headers",
        ),
        (
            r'(client\.get\("/orders/[^"]*")(?!\s*,\s*headers)',
            r"\1, headers=auth_headers",
        ),
        (
            r'(client\.get\("/stocks/[^"]*")(?!\s*,\s*headers)',
            r"\1, headers=auth_headers",
        ),
        # POST işlemleri
        (
            r'(client\.post\("/users/[^"]*"[^)]*)(?!\s*,\s*headers)',
            r"\1, headers=auth_headers",
        ),
        (
            r'(client\.post\("/orders/[^"]*"[^)]*)(?!\s*,\s*headers)',
            r"\1, headers=auth_headers",
        ),
        (
            r'(client\.post\("/stocks/[^"]*"[^)]*)(?!\s*,\s*headers)',
            r"\1, headers=auth_headers",
        ),
        # PUT işlemleri
        (
            r'(client\.put\("/users/[^"]*"[^)]*)(?!\s*,\s*headers)',
            r"\1, headers=auth_headers",
        ),
        (
            r'(client\.put\("/orders/[^"]*"[^)]*)(?!\s*,\s*headers)',
            r"\1, headers=auth_headers",
        ),
        (
            r'(client\.put\("/stocks/[^"]*"[^)]*)(?!\s*,\s*headers)',
            r"\1, headers=auth_headers",
        ),
        # DELETE işlemleri
        (
            r'(client\.delete\("/users/[^"]*")(?!\s*,\s*headers)',
            r"\1, headers=auth_headers",
        ),
        (
            r'(client\.delete\("/orders/[^"]*")(?!\s*,\s*headers)',
            r"\1, headers=auth_headers",
        ),
        (
            r'(client\.delete\("/stocks/[^"]*")(?!\s*,\s*headers)',
            r"\1, headers=auth_headers",
        ),
    ]

    for pattern, replacement in auth_patterns:
        content = re.sub(pattern, replacement, content)

    # Dosyayı yaz
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ {file_path} düzeltildi")


def fix_all_test_files():
    """Tüm test dosyalarını düzelt."""
    # Test dosyalarını bul
    test_files = glob.glob("app/tests/test_*.py")
    test_files.append("app/test_db.py")  # Ana test dosyasını da ekle

    print(f"Toplam {len(test_files)} test dosyası bulundu:")
    for file in test_files:
        print(f"  - {file}")

    # Her dosyayı düzelt
    for file_path in test_files:
        if os.path.exists(file_path):
            fix_endpoints_in_file(file_path)
        else:
            print(f"⚠️  Dosya bulunamadı: {file_path}")

    print("\n🎉 Tüm endpoint path'leri düzeltildi!")


def add_auth_fixtures():
    """Test dosyalarına auth fixture'ları ekle."""
    print("\n🔧 Auth fixture'ları ekleniyor...")

    # conftest.py'ye auth fixture'ları ekle
    conftest_path = "app/tests/conftest.py"
    if os.path.exists(conftest_path):
        with open(conftest_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Auth fixture'ları zaten varsa ekleme
        if "auth_headers" not in content:
            auth_fixtures = '''
@pytest.fixture
def auth_headers():
    """Geçerli auth header'ları."""
    return {
        "Authorization": "Bearer valid-test-token-12345",
        "Content-Type": "application/json",
    }


@pytest.fixture
def invalid_auth_headers():
    """Geçersiz auth header'ları."""
    return {
        "Authorization": "Bearer invalid-token",
        "Content-Type": "application/json",
    }


@pytest.fixture
def no_auth_headers():
    """Auth header'ları olmadan."""
    return {"Content-Type": "application/json"}

'''
            # Fixture'ları dosyanın sonuna ekle
            content += auth_fixtures

            with open(conftest_path, "w", encoding="utf-8") as f:
                f.write(content)

            print("✅ Auth fixture'ları eklendi")
        else:
            print("ℹ️  Auth fixture'ları zaten mevcut")


if __name__ == "__main__":
    print("🚀 Test endpoint'lerini düzeltme başlıyor...")

    # Auth fixture'larını ekle
    add_auth_fixtures()

    # Tüm test dosyalarını düzelt
    fix_all_test_files()

    print("\n✨ Tüm işlemler tamamlandı!")
    print("📝 Şimdi testleri çalıştırabilirsiniz: python -m pytest")
