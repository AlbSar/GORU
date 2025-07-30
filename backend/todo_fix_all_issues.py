#!/usr/bin/env python3
"""
Tüm test ve API sorunlarını çözmek için TODO listesi.
"""

TODOS = [
    {
        "id": "fix-fastapi-router-config",
        "title": "FastAPI Router Konfigürasyonu Düzeltme",
        "description": "main.py'de router'ların doğru path'lerle include edilmesi",
        "status": "pending",
        "priority": "high",
    },
    {
        "id": "fix-auth-headers-import",
        "title": "Auth Headers Import Sorunu",
        "description": "Test dosyalarında auth_headers fixture'ının doğru import edilmesi",
        "status": "pending",
        "priority": "high",
    },
    {
        "id": "fix-database-lock-issue",
        "title": "Database Kilitlenme Sorunu",
        "description": "Test ortamında sqlite database kilitlenmesinin çözülmesi",
        "status": "pending",
        "priority": "medium",
    },
    {
        "id": "fix-endpoint-404-errors",
        "title": "404 Endpoint Hataları",
        "description": "Tüm endpoint'lerin 404 döndürmesi sorununun çözülmesi",
        "status": "pending",
        "priority": "high",
    },
    {
        "id": "fix-test-fixtures",
        "title": "Test Fixture'ları Düzeltme",
        "description": "Test dosyalarında eksik fixture'ların eklenmesi",
        "status": "pending",
        "priority": "medium",
    },
    {
        "id": "fix-coverage-threshold",
        "title": "Coverage Threshold Enforcement",
        "description": "CI/CD'de coverage %90 threshold'unun uygulanması",
        "status": "pending",
        "priority": "low",
    },
    {
        "id": "fix-badge-updates",
        "title": "Coverage Badge Otomatik Güncelleme",
        "description": "Coverage badge'lerinin otomatik güncellenmesi",
        "status": "pending",
        "priority": "low",
    },
]


def print_todos():
    """TODO listesini yazdır."""
    print("📋 TODO Listesi:")
    print("=" * 50)

    for i, todo in enumerate(TODOS, 1):
        status_icon = "✅" if todo["status"] == "completed" else "⏳"
        priority_icon = (
            "🔴"
            if todo["priority"] == "high"
            else "🟡" if todo["priority"] == "medium" else "🟢"
        )

        print(f"{i}. {status_icon} {priority_icon} {todo['title']}")
        print(f"   📝 {todo['description']}")
        print(f"   🏷️  {todo['status'].upper()} | {todo['priority'].upper()}")
        print()


if __name__ == "__main__":
    print_todos()
