"""
Son eksik coverage'ları tamamlayan testler.
Environment variable'ları geçici olarak değiştirerek test eder.
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest


class TestFinalDatabaseCoverage:
    """Son eksik coverage'ları tamamlayan testler"""

    def test_get_database_url_development_environment(self):
        """Development environment test edilir"""
        # Orijinal environment'ı sakla
        original_env = os.environ.copy()

        try:
            # Environment'ı temizle ve development ayarla
            os.environ.pop("TESTING", None)
            os.environ.pop("PYTEST_CURRENT_TEST", None)
            os.environ["ENVIRONMENT"] = "development"

            # Module cache'ini temizle
            if "app.database" in sys.modules:
                del sys.modules["app.database"]

            # Module'ü yeniden import et
            from ..database import get_database_url

            url = get_database_url()
            assert "sqlite" in url
            assert "dev.db" in url

        finally:
            # Environment'ı geri yükle
            os.environ.clear()
            os.environ.update(original_env)

    def test_get_database_url_production_environment(self):
        """Production environment test edilir"""
        # Orijinal environment'ı sakla
        original_env = os.environ.copy()

        try:
            # Environment'ı temizle ve production ayarla
            os.environ.pop("TESTING", None)
            os.environ.pop("PYTEST_CURRENT_TEST", None)
            os.environ["ENVIRONMENT"] = "production"
            os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/test"

            # Module cache'ini temizle
            if "app.database" in sys.modules:
                del sys.modules["app.database"]

            # Module'ü yeniden import et
            from ..database import get_database_url

            url = get_database_url()
            assert "postgresql" in url
            assert "user:pass@localhost/test" in url

        finally:
            # Environment'ı geri yükle
            os.environ.clear()
            os.environ.update(original_env)

    def test_get_database_url_default_environment(self):
        """Default environment test edilir"""
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

    def test_postgresql_engine_configuration(self):
        """PostgreSQL engine configuration test edilir"""
        # Orijinal environment'ı sakla
        original_env = os.environ.copy()

        try:
            # Environment'ı temizle ve production ayarla
            os.environ.pop("TESTING", None)
            os.environ.pop("PYTEST_CURRENT_TEST", None)
            os.environ["ENVIRONMENT"] = "production"
            os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/test"

            # Module cache'ini temizle
            if "app.database" in sys.modules:
                del sys.modules["app.database"]

            # Module'ü yeniden import et
            from ..database import get_engine

            engine = get_engine()
            assert engine is not None

        finally:
            # Environment'ı geri yükle
            os.environ.clear()
            os.environ.update(original_env)

    def test_session_local_lazy_creation(self):
        """SessionLocal lazy creation test edilir"""
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

            session_local1 = get_session_local()
            session_local2 = get_session_local()

            # Aynı session local instance'ı döndürülmeli (lazy loading)
            assert session_local1 is session_local2

        finally:
            # Environment'ı geri yükle
            os.environ.clear()
            os.environ.update(original_env)

    def test_test_connection_exception_handling(self):
        """test_connection exception handling test edilir"""
        with patch("app.database.get_db") as mock_get_db:
            mock_get_db.side_effect = Exception("Test error")

            from ..database import test_connection

            result = test_connection()
            assert result is False

    def test_create_tables_exception_handling(self):
        """create_tables exception handling test edilir"""
        with patch("app.database.Base") as mock_base:
            mock_base.metadata.create_all.side_effect = Exception("Test error")

            from ..database import create_tables

            result = create_tables()
            assert result is False

    def test_get_db_close_exception_handling(self):
        """get_db close exception handling test edilir"""
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

    def test_get_db_rollback_exception_handling(self):
        """get_db rollback exception handling test edilir"""
        with patch("app.database.SessionLocal") as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            mock_session.execute.side_effect = Exception("Test error")
            mock_session.rollback.side_effect = Exception("Rollback error")

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
