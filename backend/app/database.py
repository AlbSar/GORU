"""
Database bağlantısı ve session yönetimi.
Environment variable'lara göre dinamik database yapılandırması.
"""

import os

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from .core.settings import settings


# Lazy engine creation - sadece gerektiğinde oluştur
_engine = None
_SessionLocal = None
_database_url = None


def get_database_url():
    """Database URL'ini lazy olarak döndürür."""
    global _database_url
    if _database_url is None:
        if os.getenv("TESTING") or os.getenv("PYTEST_CURRENT_TEST"):
            # Test ortamında SQLite kullan
            _database_url = "sqlite:///./test.db"
        else:
            # Production ortamında PostgreSQL kullan
            _database_url = settings.DATABASE_URL
    return _database_url


def get_engine():
    """Engine'i lazy olarak oluşturur."""
    global _engine
    if _engine is None:
        database_url = get_database_url()
        if database_url.startswith("sqlite"):
            # SQLite için özel yapılandırma
            _engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            # PostgreSQL için connection pooling
            _engine = create_engine(
                database_url,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                echo=settings.DEBUG,
            )
    return _engine


def get_session_local():
    """SessionLocal'ı lazy olarak oluşturur."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=get_engine()
        )
    return _SessionLocal


# Backward compatibility için - lazy loading
def engine():
    return get_engine()


def SessionLocal():
    return get_session_local()


Base = declarative_base()


def get_db():
    """
    Database session dependency.
    FastAPI dependency injection için kullanılır.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    """Database bağlantısını test eder."""
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        print(f"Database bağlantı hatası: {e}")
        return False


def create_tables():
    """Tüm tabloları oluşturur."""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tabloları oluşturuldu!")
        return True
    except Exception as e:
        print(f"❌ Tablo oluşturma hatası: {e}")
        return False
