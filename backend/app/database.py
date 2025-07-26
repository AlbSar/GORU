"""
Database bağlantısı ve session yönetimi.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .core.settings import settings

# PostgreSQL bağlantı stringini settings'den al
DATABASE_URL = settings.DATABASE_URL

# SQLAlchemy engine ve session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
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
        return True
    except Exception as e:
        print(f"Database bağlantı hatası: {e}")
        return False
