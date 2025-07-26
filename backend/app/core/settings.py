"""
Uygulama ayarları ve konfigürasyon yönetimi.
Environment değişkenlerini Pydantic BaseSettings ile yönetir.
"""

import json
import os
from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Uygulama ayarları sınıfı.
    Environment değişkenlerini type-safe şekilde yönetir.
    """

    # Database Configuration
    DATABASE_URL: str = "postgresql://goru:goru@localhost:5432/goru_db"
    TEST_DATABASE_URL: str = (
        "postgresql://goru:goru@localhost:5432/goru_test_db"
    )

    # Application Configuration
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GORU ERP Backend"

    # CORS Configuration
    BACKEND_CORS_ORIGINS: Union[List[str], str] = (
        '["http://localhost:3000", "http://localhost:8080"]'
    )

    # Environment Configuration
    APP_ENV: str = "development"
    LOG_LEVEL: str = "debug"

    # Mock sistem ayarları
    USE_MOCK: bool = False  # Mock endpoint'leri etkinleştir/devre dışı bırak
    MOCK_API_PREFIX: str = "/mock"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """
        CORS origins string'ini JSON'dan parse eder.

        Args:
            v: JSON string formatında CORS origins

        Returns:
            List[str]: Parse edilmiş CORS origins listesi

        Raises:
            ValueError: JSON parse hatası durumunda
        """
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError as e:
                raise ValueError(f"CORS origins JSON parse hatası: {e}")
        return v

    @field_validator("USE_MOCK", mode="before")
    @classmethod
    def parse_use_mock(cls, v):
        """
        USE_MOCK environment variable'ını boolean'a çevirir.

        Args:
            v: Environment variable değeri (string veya bool)

        Returns:
            bool: Parse edilmiş boolean değer
        """
        if isinstance(v, bool):
            return v

        if isinstance(v, str):
            # String'den boolean'a çevir
            v_lower = v.lower().strip()
            if v_lower in ("true", "1", "yes", "on", "enabled"):
                return True
            elif v_lower in ("false", "0", "no", "off", "disabled", ""):
                return False
            else:
                # Geçersiz değer için default false
                print("Geçersiz USE_MOCK değeri: '{}'. "
                      "Default false kullanılıyor.".format(v))
                return False

        return False

    def get_cors_origins(self) -> List[str]:
        """
        CORS origins listesini döndürür.

        Returns:
            List[str]: CORS origins listesi
        """
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            try:
                return json.loads(self.BACKEND_CORS_ORIGINS)
            except json.JSONDecodeError:
                return ["http://localhost:3000", "http://localhost:8080"]
        return self.BACKEND_CORS_ORIGINS

    def get_mock_status(self) -> dict:
        """
        Mock sistem durumunu döndürür.

        Returns:
            dict: Mock sistem durumu bilgileri
        """
        return {
            "enabled": self.USE_MOCK,
            "prefix": self.MOCK_API_PREFIX,
            "environment": os.getenv("USE_MOCK", "not_set"),
            "parsed_value": self.USE_MOCK,
        }

    class Config:
        """
        Pydantic konfigürasyon sınıfı.
        """

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Settings instance'ı oluştur
settings = Settings()
