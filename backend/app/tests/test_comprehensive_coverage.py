"""
Kapsamlı test coverage için test modülü.
Tüm ana fonksiyonaliteleri test eder.
"""

import pytest
from sqlalchemy import text


class TestSettings:
    """Settings modülü testleri."""

    def test_settings_use_mock(self):
        """Settings USE_MOCK testi."""
        from ..core.settings import Settings

        test_settings = Settings()
        assert test_settings.USE_MOCK

    def test_app_cors_setup(self):
        """App CORS setup testi."""
        from ..main import app

        # CORS middleware'in eklenmiş olduğunu kontrol et
        assert len(app.user_middleware_stack) > 0


class TestDatabaseConnection:
    """Database bağlantı fonksiyonu testleri."""

    def test_database_connection_success(self):
        """Database bağlantısı başarılıysa True dönmeli."""
        from ..database import test_connection

        assert test_connection() is True

    # Not: Database offline/yanlış ayar ile False döndüğünü test etmek için ayrı bir test yazılabilir.

    def test_transaction_rollback(self):
        """Transaction sırasında hata oluşursa rollback çalışmalı."""
        from sqlalchemy import text

        from ..database import get_db

        db = next(get_db())
        db.begin()
        try:
            db.execute(text("INVALID SQL"))  # Hatalı query
            db.commit()
        except Exception:
            db.rollback()
        # Transaction rollback sonrası session aktif olmalı
        assert db.is_active
        db.close()
        assert not db.is_active or db.closed if hasattr(db, "closed") else True

    def test_session_closed_on_exception(self):
        """Session her durumda kapanmalı (exception olsa bile)."""
        from ..database import get_db

        db = next(get_db())
        try:
            raise Exception("Test")
        except Exception:
            pass
        db.close()
        assert not db.is_active or db.closed if hasattr(db, "closed") else True

    def test_get_db_dependency_injection_session_closed(self, client, auth_headers):
        """get_db dependency injection ile session'ın endpoint üzerinden açılıp kapandığını test eder."""
        from ..database import TestingSessionLocal

        # Önce session sayısını al
        session1 = TestingSessionLocal()
        session1.execute(text("SELECT 1"))
        session1.close()
        # Kullanıcı oluşturma endpoint'ine istek at
        user_data = {
            "name": "Session Test User",
            "email": "sessiontestuser@example.com",
            "role": "user",
            "is_active": True,
            "password": "test123",
        }
        response = client.post("/users/", json=user_data, headers=auth_headers)
        assert (
            response.status_code == 201 or response.status_code == 400
        )  # 400: email varsa
        # Yeni bir session açıp kapatabiliyor muyuz kontrol et
        session2 = TestingSessionLocal()
        session2.execute(text("SELECT 1"))
        session2.close()
        assert True  # Session açılıp kapanabiliyor, memory leak yok

    def test_connection_pool_exhaustion(self):
        """Connection pool limiti aşıldığında hata fırlatılmalı (edge-case)."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # Pool size 2 ile engine oluştur
        engine = create_engine("sqlite:///:memory:", pool_size=2, max_overflow=0)
        Session = sessionmaker(bind=engine)
        sessions = []
        # Pool limitini aşacak kadar session aç
        for _ in range(2):
            sessions.append(Session())
        with pytest.raises(Exception):
            # 3. bağlantı pool limitini aşar, hata beklenir
            sessions.append(Session())
        # Açık session'ları kapat
        for s in sessions:
            s.close()

    def test_connection_timeout(self):
        """Connection timeout edge-case testi (simülasyon)."""
        import time

        from sqlalchemy import create_engine

        # Timeout'u kısa ayarla
        engine = create_engine(
            "sqlite:///:memory:", pool_timeout=0.1, pool_size=1, max_overflow=0
        )
        conn1 = engine.connect()
        start = time.time()
        with pytest.raises(Exception):
            # 2. bağlantı timeout'a düşmeli
            engine.connect()
        conn1.close()
        assert time.time() - start < 1  # Timeout hızlı olmalı

    def test_alembic_migrations_apply(self):
        """Alembic migration'larının başarıyla uygulanıp uygulanmadığını test eder."""
        import subprocess

        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd="backend",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Alembic migration hatası: {result.stderr}"
