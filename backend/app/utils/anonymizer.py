"""
Veri anonimleştirme araçları.
Hassas verileri anonim veya pseudonim hale getirir.
"""

import hashlib
import re
from typing import Any, Dict, List

from faker import Faker

fake = Faker("tr_TR")


class DataAnonymizer:
    """Veri anonimleştirme sınıfı."""

    @staticmethod
    def anonymize_email(email: str) -> str:
        """E-posta adresini anonimleştirir."""
        if "@" not in email:
            return email

        username, domain = email.split("@", 1)
        # İlk ve son karakteri saklayıp ortasını * ile değiştir
        if len(username) > 2:
            anonymized_username = (
                username[0] + "*" * (len(username) - 2) + username[-1]
            )
        else:
            anonymized_username = "*" * len(username)

        return f"{anonymized_username}@{domain}"

    @staticmethod
    def anonymize_name(name: str) -> str:
        """İsmi anonimleştirir."""
        if not name:
            return name

        words = name.split()
        anonymized_words = []

        for word in words:
            if len(word) > 1:
                anonymized_word = word[0] + "*" * (len(word) - 1)
            else:
                anonymized_word = "*"
            anonymized_words.append(anonymized_word)

        return " ".join(anonymized_words)

    @staticmethod
    def pseudonymize_with_hash(data: str, salt: str = "goru_salt") -> str:
        """Veriyi hash ile pseudonim hale getirir."""
        if not data:
            return data

        hash_obj = hashlib.sha256((data + salt).encode())
        return hash_obj.hexdigest()[:8]  # İlk 8 karakter

    @staticmethod
    def anonymize_phone(phone: str) -> str:
        """Telefon numarasını anonimleştirir."""
        if not phone:
            return phone

        # Sadece rakamları al
        digits = re.sub(r"\D", "", phone)

        if len(digits) >= 4:
            # İlk 3 ve son 2 rakamı göster, ortasını * ile değiştir
            anonymized = digits[:3] + "*" * (len(digits) - 5) + digits[-2:]
        else:
            anonymized = "*" * len(digits)

        # Orijinal formatı korumaya çalış
        result = phone
        for i, digit in enumerate(digits):
            result = result.replace(
                digit, anonymized[i] if i < len(anonymized) else "*", 1
            )

        return result

    @staticmethod
    def anonymize_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Kullanıcı verisini anonimleştirir."""
        anonymized = user_data.copy()

        if "email" in anonymized:
            anonymized["email"] = DataAnonymizer.anonymize_email(
                anonymized["email"]
            )

        if "name" in anonymized:
            anonymized["name"] = DataAnonymizer.anonymize_name(
                anonymized["name"]
            )

        if "phone" in anonymized:
            anonymized["phone"] = DataAnonymizer.anonymize_phone(
                anonymized["phone"]
            )

        return anonymized

    @staticmethod
    def generate_fake_user_data() -> Dict[str, Any]:
        """Sahte kullanıcı verisi üretir."""
        return {
            "name": fake.name(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "address": fake.address(),
            "company": fake.company(),
            "role": fake.random_element(elements=["admin", "user", "manager"]),
        }

    @staticmethod
    def anonymize_dataset(
        data_list: List[Dict[str, Any]], fields_to_anonymize: List[str]
    ) -> List[Dict[str, Any]]:
        """Veri setindeki belirtilen alanları anonimleştirir."""
        anonymized_list = []

        for item in data_list:
            anonymized_item = item.copy()

            for field in fields_to_anonymize:
                if field in anonymized_item:
                    if field == "email":
                        anonymized_item[field] = (
                            DataAnonymizer.anonymize_email(
                                anonymized_item[field]
                            )
                        )
                    elif field == "name":
                        anonymized_item[field] = DataAnonymizer.anonymize_name(
                            anonymized_item[field]
                        )
                    elif field == "phone":
                        anonymized_item[field] = (
                            DataAnonymizer.anonymize_phone(
                                anonymized_item[field]
                            )
                        )
                    else:
                        # Genel hash-based pseudonymization
                        anonymized_item[field] = (
                            DataAnonymizer.pseudonymize_with_hash(
                                str(anonymized_item[field])
                            )
                        )

            anonymized_list.append(anonymized_item)

        return anonymized_list
