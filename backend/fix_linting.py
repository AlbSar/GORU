#!/usr/bin/env python3
"""
Linting sorunlarını otomatik olarak düzeltmek için script.
"""

import os
import subprocess
import sys


def run_command(command, description):
    """Komut çalıştır ve sonucu göster."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} başarılı")
            return True
        else:
            print(f"❌ {description} başarısız:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ {description} hatası: {e}")
        return False

def fix_linting_issues():
    """Linting sorunlarını düzelt."""
    
    print("🚀 Linting sorunları düzeltiliyor...")
    
    # 1. Black formatting
    success1 = run_command("black app/", "Black formatting")
    
    # 2. isort import sorting
    success2 = run_command("isort --profile black app/", "Import sorting")
    
    # 3. Ruff auto-fix
    success3 = run_command("ruff check --fix app/", "Ruff auto-fix")
    
    # 4. Kullanılmayan import'ları kaldır
    success4 = run_command("ruff check --select F401 --fix app/", "Unused imports removal")
    
    # 5. Line length sorunlarını düzelt
    success5 = run_command("ruff check --select E501 --fix app/", "Line length fixes")
    
    # 6. Whitespace sorunlarını düzelt
    success6 = run_command("ruff check --select E203,W291,W292,W293 --fix app/", "Whitespace fixes")
    
    # 7. F-string sorunlarını düzelt
    success7 = run_command("ruff check --select F541 --fix app/", "F-string fixes")
    
    # 8. Bare except sorunlarını düzelt
    success8 = run_command("ruff check --select E722 --fix app/", "Bare except fixes")
    
    # 9. Comparison sorunlarını düzelt
    success9 = run_command("ruff check --select E712 --fix app/", "Comparison fixes")
    
    # 10. Redefinition sorunlarını düzelt
    success10 = run_command("ruff check --select F811 --fix app/", "Redefinition fixes")
    
    # 11. Undefined name sorunlarını düzelt
    success11 = run_command("ruff check --select F821 --fix app/", "Undefined name fixes")
    
    # 12. Local variable sorunlarını düzelt
    success12 = run_command("ruff check --select F841 --fix app/", "Local variable fixes")
    
    # 13. Module level import sorunlarını düzelt
    success13 = run_command("ruff check --select E402 --fix app/", "Module level import fixes")
    
    print("\n📊 Düzeltme Sonuçları:")
    print(f"Black formatting: {'✅' if success1 else '❌'}")
    print(f"Import sorting: {'✅' if success2 else '❌'}")
    print(f"Ruff auto-fix: {'✅' if success3 else '❌'}")
    print(f"Unused imports: {'✅' if success4 else '❌'}")
    print(f"Line length: {'✅' if success5 else '❌'}")
    print(f"Whitespace: {'✅' if success6 else '❌'}")
    print(f"F-string: {'✅' if success7 else '❌'}")
    print(f"Bare except: {'✅' if success8 else '❌'}")
    print(f"Comparison: {'✅' if success9 else '❌'}")
    print(f"Redefinition: {'✅' if success10 else '❌'}")
    print(f"Undefined name: {'✅' if success11 else '❌'}")
    print(f"Local variable: {'✅' if success12 else '❌'}")
    print(f"Module level import: {'✅' if success13 else '❌'}")
    
    # Son kontrol
    print("\n🔍 Son linting kontrolü...")
    final_check = run_command("ruff check app/", "Final linting check")
    
    if final_check:
        print("🎉 Tüm linting sorunları düzeltildi!")
    else:
        print("⚠️ Bazı linting sorunları hala mevcut.")
    
    return final_check

if __name__ == "__main__":
    fix_linting_issues() 