#!/usr/bin/env python3
"""
Linting ve Formatting Düzeltme Scripti
Black, isort ve flake8 sorunlarını otomatik düzeltir
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Komut çalıştırır ve sonucu raporlar."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} başarılı!")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {description} başarısız!")
            if result.stderr:
                print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ {description} hatası: {e}")
        return False

def main():
    """Ana linting düzeltme işlemi."""
    print("🔧 Linting ve Formatting Düzeltme Başlıyor...")
    
    # Black formatting
    success1 = run_command("black app/", "Black formatting")
    
    # isort import sorting
    success2 = run_command("isort app/", "isort import sorting")
    
    # flake8 linting (sadece rapor)
    success3 = run_command("flake8 app/ --max-line-length=88 --ignore=E203,W503", "flake8 linting")
    
    # pylint static analysis
    success4 = run_command("pylint app/ --max-line-length=88", "pylint analysis")
    
    print("\n📊 Linting Sonuçları:")
    print(f"Black: {'✅' if success1 else '❌'}")
    print(f"isort: {'✅' if success2 else '❌'}")
    print(f"flake8: {'✅' if success3 else '❌'}")
    print(f"pylint: {'✅' if success4 else '❌'}")
    
    if all([success1, success2, success3, success4]):
        print("\n🎉 Tüm linting işlemleri başarılı!")
        return True
    else:
        print("\n⚠️ Bazı linting işlemleri başarısız oldu.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 