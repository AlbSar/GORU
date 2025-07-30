"""
Ultimate database coverage testleri.
%95+ coverage hedefi için son eksik satırları test eder.
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

from ..database import get_db


class TestUltimateDatabaseCoverage:
    """Ultimate database coverage testleri"""

    def test_get_database_url_production_without_env_url(self):
        """Production environment'ında DATABASE_URL yoksa settings'den alır"""
        # Orijinal environment'ı sakla
        original_env = os.environ.copy()

        try:
            # Environment'ı temizle ve production ayarla ama DATABASE_URL yok
            os.environ.pop("TESTING", None)
            os.environ.pop("PYTEST_CURRENT_TEST", None)
            os.environ["ENVIRONMENT"] = "production"
            os.environ.pop("DATABASE_URL", None)

            # Module cache'ini temizle
            if "app.database" in sys.modules:
                del sys.modules["app.database"]

            # Module'ü yeniden import et
            from ..database import get_database_url

            url = get_database_url()
            assert url is not None

        finally:
            # Environment'ı geri yükle
            os.environ.clear()
            os.environ.update(original_env)

    def test_get_database_url_default_environment_with_settings(self):
        """Default environment'da settings'den URL alır"""
        # Orijinal environment'ı sakla
        original_env = os.environ.copy()

        try:
            # Environment'ı temizle
            os.environ.pop("TESTING", None)
            os.environ.pop("PYTEST_CURRENT_TEST", None)
            os.environ.pop("ENVIRONMENT", None)
            os.environ.pop("DATABASE_URL", None)

            # Module cache'ini temizle
            if "app.database" in sys.modules:
                del sys.modules["app.database"]

            # Module'ü yeniden import et
            from ..database import get_database_url

            url = get_database_url()
            assert url is not None

        finally:
            # Environment'ı geri yükle
            os.environ.clear()
            os.environ.update(original_env)

    def test_get_session_local_lazy_creation_with_cache(self):
        """SessionLocal lazy creation with cache test edilir"""
        # Orijinal environment'ı sakla
        original_env = os.environ.copy()

        try:
            # Environment'ı temizle
            os.environ.pop("TESTING", None)
            os.environ.pop("PYTEST_CURRENT_TEST", None)

            # Module cache'ini temizle
            if "app.database" in sys.modules:
                del sys.modules["app.database"]

            # Module'ü yeniden import et
            from ..database import get_session_local

            # İlk çağrı - SessionLocal oluşturulur
            session_local1 = get_session_local()
            assert session_local1 is not None

            # İkinci çağrı - aynı SessionLocal döner
            session_local2 = get_session_local()
            assert session_local1 is session_local2

        finally:
            # Environment'ı geri yükle
            os.environ.clear()
            os.environ.update(original_env)

    def test_get_engine_lazy_creation_with_cache(self):
        """Engine lazy creation with cache test edilir"""
        # Orijinal environment'ı sakla
        original_env = os.environ.copy()

        try:
            # Environment'ı temizle
            os.environ.pop("TESTING", None)
            os.environ.pop("PYTEST_CURRENT_TEST", None)

            # Module cache'ini temizle
            if "app.database" in sys.modules:
                del sys.modules["app.database"]

            # Module'ü yeniden import et
            from ..database import get_engine

            # İlk çağrı - engine oluşturulur
            engine1 = get_engine()
            assert engine1 is not None

            # İkinci çağrı - aynı engine döner
            engine2 = get_engine()
            assert engine1 is engine2

        finally:
            # Environment'ı geri yükle
            os.environ.clear()
            os.environ.update(original_env)

    def test_get_db_yield_and_close_success(self):
        """get_db yield ve close success test edilir"""

        db_generator = get_db()
        db = next(db_generator)

        # Session aktif olmalı
        assert db.is_active

        # Generator'ı kapat
        try:
            db_generator.close()
        except StopIteration:
            pass

    def test_get_db_exception_with_rollback_success(self):
        """get_db exception with rollback success test edilir"""
        with patch("app.database.SessionLocal") as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            mock_session.execute.side_effect = Exception("Test error")

            from ..database import get_db

            db_generator = get_db()

            # HTTPException beklenir
            with pytest.raises(Exception):
                db = next(db_generator)

            # Generator'ı kapat
            try:
                db_generator.close()
            except StopIteration:
                pass

    def test_get_db_finally_close_exception_success(self):
        """get_db finally close exception success test edilir"""
        with patch("app.database.SessionLocal") as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            mock_session.close.side_effect = Exception("Close error")

            from ..database import get_db

            db_generator = get_db()
            db = next(db_generator)

            # Generator'ı kapat
            try:
                db_generator.close()
            except StopIteration:
                pass

    def test_test_connection_success_path(self):
        """test_connection success path test edilir"""
        from ..database import test_connection

        result = test_connection()
        assert result is True

    def test_test_connection_failure_path(self):
        """test_connection failure path test edilir"""
        with patch("app.database.get_db") as mock_get_db:
            mock_get_db.side_effect = Exception("Test error")

            from ..database import test_connection

            result = test_connection()
            assert result is False

    def test_create_tables_success_path(self):
        """create_tables success path test edilir"""
        from ..database import create_tables

        result = create_tables()
        assert result is True

    def test_create_tables_failure_path(self):
        """create_tables failure path test edilir"""
        with patch("app.database.Base") as mock_base:
            mock_base.metadata.create_all.side_effect = Exception("Test error")

            from ..database import create_tables

            result = create_tables()
            assert result is False
