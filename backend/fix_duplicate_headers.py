#!/usr/bin/env python3
"""
Test dosyalarındaki tekrarlanan headers parametrelerini düzeltmek için script.
"""

import glob
import os
import re


def fix_duplicate_headers_in_file(file_path):
    """Tek dosyada tekrarlanan headers parametrelerini düzelt."""
    print(f"İşleniyor: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Tekrarlanan headers parametrelerini düzelt
    patterns = [
        # headers=auth_headers, headers=auth_headers -> headers=auth_headers
        (r"headers=auth_headers,\s*headers=auth_headers", "headers=auth_headers"),
        (r"headers=headers,\s*headers=auth_headers", "headers=auth_headers"),
        (r"headers=admin_headers,\s*headers=auth_headers", "headers=admin_headers"),
        (r"headers=user_headers,\s*headers=auth_headers", "headers=user_headers"),
        (r"headers=viewer_headers,\s*headers=auth_headers", "headers=viewer_headers"),
        # headers=headers, headers=headers -> headers=headers
        (r"headers=headers,\s*headers=headers", "headers=headers"),
        # headers=invalid_headers, headers=auth_headers -> headers=invalid_headers
        (r"headers=invalid_headers,\s*headers=auth_headers", "headers=invalid_headers"),
    ]

    for pattern, replacement in patterns:
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
            fix_duplicate_headers_in_file(file_path)
        else:
            print(f"⚠️  Dosya bulunamadı: {file_path}")

    print("\n🎉 Tüm tekrarlanan headers parametreleri düzeltildi!")


if __name__ == "__main__":
    print("🚀 Tekrarlanan headers parametrelerini düzeltme başlıyor...")

    # Tüm test dosyalarını düzelt
    fix_all_test_files()

    print("\n✨ Tüm işlemler tamamlandı!")
    print("📝 Şimdi testleri çalıştırabilirsiniz: python -m pytest")
