"""
Utils/Anonymizer modülü testleri.
Veri anonimleştirme ve pseudonymization fonksiyonlarını test eder.
"""

import pytest
import hashlib
from ..utils.anonymizer import DataAnonymizer


class TestDataAnonymizer:
    """DataAnonymizer sınıfı testleri."""

    def test_anonymize_email(self):
        """E-posta anonimleştirme testi."""
        # Normal e-posta
        email = "test@example.com"
        anonymized = DataAnonymizer.anonymize_email(email)
        assert anonymized.endswith("@example.com")
        assert anonymized == "t**t@example.com"  # İlk ve son karakter korunur
        
        # Farklı domain
        email2 = "john.doe@company.org"
        anonymized2 = DataAnonymizer.anonymize_email(email2)
        assert anonymized2.endswith("@company.org")
        assert anonymized2.startswith("***")
        
        # Uzun e-posta
        email3 = "very.long.email.address@test.domain.com"
        anonymized3 = DataAnonymizer.anonymize_email(email3)
        assert anonymized3.endswith("@test.domain.com")
        assert anonymized3.startswith("***")

    def test_anonymize_name(self):
        """İsim anonimleştirme testi."""
        # Tek isim
        name = "John"
        anonymized = DataAnonymizer.anonymize_name(name)
        assert anonymized == "J***"
        
        # İki isim
        name2 = "John Doe"
        anonymized2 = DataAnonymizer.anonymize_name(name2)
        assert anonymized2 == "J*** D**"  # Son karakter korunmaz
        
        # Üç isim
        name3 = "John Michael Doe"
        anonymized3 = DataAnonymizer.anonymize_name(name3)
        assert anonymized3 == "J*** M*** D***"
        
        # Boş string
        anonymized_empty = DataAnonymizer.anonymize_name("")
        assert anonymized_empty == ""
        
        # Tek karakter
        anonymized_single = DataAnonymizer.anonymize_name("A")
        assert anonymized_single == "A"

    def test_anonymize_phone(self):
        """Telefon anonimleştirme testi."""
        # Türk telefon numarası
        phone = "+905551234567"
        anonymized = DataAnonymizer.anonymize_phone(phone)
        assert anonymized == "+90*******567"  # Gerçek implementasyona göre
        
        # US telefon numarası
        phone2 = "+12345678901"
        anonymized2 = DataAnonymizer.anonymize_phone(phone2)
        assert anonymized2 == "+123****8901"
        
        # Kısa numara
        phone3 = "12345"
        anonymized3 = DataAnonymizer.anonymize_phone(phone3)
        assert anonymized3 == "1***5"
        
        # Çok kısa numara
        phone4 = "123"
        anonymized4 = DataAnonymizer.anonymize_phone(phone4)
        assert anonymized4 == "123"  # 3 karakter veya daha az anonimleştirilmez

    def test_pseudonymize_with_hash(self):
        """Hash ile pseudonymization testi."""
        data = "sensitive_data"
        salt = "test_salt"
        
        # Aynı veri ve salt ile aynı hash üretmeli
        hash1 = DataAnonymizer.pseudonymize_with_hash(data, salt)
        hash2 = DataAnonymizer.pseudonymize_with_hash(data, salt)
        assert hash1 == hash2
        
        # Farklı salt ile farklı hash üretmeli
        hash3 = DataAnonymizer.pseudonymize_with_hash(data, "different_salt")
        assert hash1 != hash3
        
        # Hash uzunluğunu kontrol et (SHA-256 = 64 karakter)
        assert len(hash1) == 64
        
        # Hex format kontrolü
        int(hash1, 16)  # Hex değilse exception fırlatır

    def test_generate_fake_user_data(self):
        """Fake kullanıcı verisi üretme testi."""
        fake_user = DataAnonymizer.generate_fake_user_data()
        
        # Gerekli alanların varlığını kontrol et
        required_fields = ["name", "email", "phone", "address", "company"]
        for field in required_fields:
            assert field in fake_user
            assert fake_user[field] is not None
            assert isinstance(fake_user[field], str)
            assert len(fake_user[field]) > 0
        
        # E-posta format kontrolü
        assert "@" in fake_user["email"]
        assert "." in fake_user["email"]
        
        # Telefon format kontrolü (Türkiye için)
        assert fake_user["phone"].startswith("+90") or fake_user["phone"].startswith("0")
        
        # İki kez çalıştırıldığında farklı veri üretmeli
        fake_user2 = DataAnonymizer.generate_fake_user_data()
        assert fake_user != fake_user2

    def test_anonymize_dataset(self):
        """Dataset anonimleştirme testi."""
        # Test verisi
        dataset = [
            {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+905551234567",
                "age": 30,
                "city": "Istanbul"
            },
            {
                "id": 2,
                "name": "Jane Smith",
                "email": "jane@test.com",
                "phone": "+905559876543",
                "age": 25,
                "city": "Ankara"
            }
        ]
        
        # Anonimleştirme alanları
        anonymize_fields = ["name", "email", "phone"]
        
        # Anonimleştir
        anonymized_dataset = DataAnonymizer.anonymize_dataset(dataset, anonymize_fields)
        
        # Anonimleştirilmiş veriyi kontrol et
        assert len(anonymized_dataset) == len(dataset)
        
        for i, record in enumerate(anonymized_dataset):
            original = dataset[i]
            
            # ID ve diğer alanlar değişmemeli
            assert record["id"] == original["id"]
            assert record["age"] == original["age"]
            assert record["city"] == original["city"]
            
            # Anonimleştirilen alanlar değişmeli
            assert record["name"] != original["name"]
            assert record["email"] != original["email"]
            assert record["phone"] != original["phone"]
            
            # Anonimleştirme formatı doğru mu
            assert record["name"].endswith("***") or " " in record["name"]
            assert "@" in record["email"]
            assert record["phone"].startswith("+90")

    def test_anonymize_dataset_empty_fields(self):
        """Boş alanlar ile dataset anonimleştirme testi."""
        dataset = [{"name": "John", "email": "john@test.com"}]
        
        # Boş anonymize_fields
        result = DataAnonymizer.anonymize_dataset(dataset, [])
        assert result == dataset  # Değişmemeli
        
        # None dataset
        result2 = DataAnonymizer.anonymize_dataset(None, ["name"])
        assert result2 is None

    def test_anonymize_dataset_missing_fields(self):
        """Eksik alanlar ile dataset anonimleştirme testi."""
        dataset = [{"name": "John", "email": "john@test.com"}]
        
        # Olmayan alan adı
        result = DataAnonymizer.anonymize_dataset(dataset, ["name", "nonexistent_field"])
        
        # Sadece var olan alanlar anonimleştirilmeli
        assert result[0]["name"] != dataset[0]["name"]  # Anonimleşti
        assert result[0]["email"] == dataset[0]["email"]  # Değişmedi
        assert "nonexistent_field" not in result[0]  # Eklenmedi

    def test_edge_cases(self):
        """Edge case testleri."""
        # Boş string'ler
        assert DataAnonymizer.anonymize_email("") == ""
        assert DataAnonymizer.anonymize_name("") == ""
        assert DataAnonymizer.anonymize_phone("") == ""
        
        # None değerler
        assert DataAnonymizer.anonymize_email(None) == ""
        assert DataAnonymizer.anonymize_name(None) == ""
        assert DataAnonymizer.anonymize_phone(None) == ""
        
        # Geçersiz e-posta formatı
        invalid_email = "invalid_email"
        anonymized = DataAnonymizer.anonymize_email(invalid_email)
        # @ işareti yoksa, tüm string anonimleştirilir
        assert anonymized == "***"

    def test_turkish_characters(self):
        """Türkçe karakter testleri."""
        # Türkçe isim
        turkish_name = "Ahmet Öğretmen"
        anonymized = DataAnonymizer.anonymize_name(turkish_name)
        assert anonymized == "A*** Ö***"
        
        # Türkçe e-posta
        turkish_email = "ahmet@örnek.com"
        anonymized_email = DataAnonymizer.anonymize_email(turkish_email)
        assert anonymized_email.endswith("@örnek.com")

    def test_hash_consistency(self):
        """Hash tutarlılık testleri."""
        data = "test_data"
        salt = "test_salt"
        
        # Çoklu çalıştırmada aynı hash
        hashes = [DataAnonymizer.pseudonymize_with_hash(data, salt) for _ in range(5)]
        assert all(h == hashes[0] for h in hashes)
        
        # Boş string hash
        empty_hash = DataAnonymizer.pseudonymize_with_hash("", salt)
        assert len(empty_hash) == 64
        
        # None hash
        none_hash = DataAnonymizer.pseudonymize_with_hash(None, salt)
        assert len(none_hash) == 64

    def test_performance_large_dataset(self):
        """Büyük dataset performans testi."""
        # 100 kayıtlı dataset oluştur
        large_dataset = [
            {
                "id": i,
                "name": f"User {i}",
                "email": f"user{i}@test.com",
                "phone": f"+90555{i:07d}"
            }
            for i in range(100)
        ]
        
        # Anonimleştirme süresi makul olmalı (2 saniyeden az)
        import time
        start = time.time()
        
        result = DataAnonymizer.anonymize_dataset(large_dataset, ["name", "email", "phone"])
        
        end = time.time()
        duration = end - start
        
        assert duration < 2.0  # 2 saniyeden az sürmeli
        assert len(result) == 100
        assert all(record["name"] != f"User {record['id']}" for record in result) 