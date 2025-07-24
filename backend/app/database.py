import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# PostgreSQL bağlantı stringini .env'den al
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy engine ve session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


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
