#!/usr/bin/env python3
"""
Test dosyasındaki endpoint path'lerini düzeltmek için script.
"""

import re


def fix_paths():
    """Test dosyasındaki tüm path'leri düzelt."""
    
    # Dosyayı oku
    with open('app/tests/test_routes_coverage_90.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Path'leri değiştir
    patterns = [
        (r'client\.post\("/users/', 'client.post("/api/v1/users/'),
        (r'client\.get\("/users/', 'client.get("/api/v1/users/'),
        (r'client\.put\("/users/', 'client.put("/api/v1/users/'),
        (r'client\.delete\("/users/', 'client.delete("/api/v1/users/'),
        (r'client\.post\("/orders/', 'client.post("/api/v1/orders/'),
        (r'client\.get\("/orders/', 'client.get("/api/v1/orders/'),
        (r'client\.put\("/orders/', 'client.put("/api/v1/orders/'),
        (r'client\.delete\("/orders/', 'client.delete("/api/v1/orders/'),
        (r'client\.post\("/stocks/', 'client.post("/api/v1/stocks/'),
        (r'client\.get\("/stocks/', 'client.get("/api/v1/stocks/'),
        (r'client\.put\("/stocks/', 'client.put("/api/v1/stocks/'),
        (r'client\.delete\("/stocks/', 'client.delete("/api/v1/stocks/'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # Dosyayı yaz
    with open('app/tests/test_routes_coverage_90.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Path'ler başarıyla düzeltildi!")

if __name__ == "__main__":
    fix_paths() 