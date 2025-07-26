from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker

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
    """
    Veritabanı bağlantısını test eder. Bağlantı başarılıysa True, değilse False döner.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))  # text() ile kullanılmalı
        return True
    except OperationalError as e:
        print(f"Veritabanı bağlantı hatası: {e}")
        return False
