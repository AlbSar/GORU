"""
Ortak yardımcı fonksiyonlar ve bağımlılıklar.
Tüm route modülleri tarafından kullanılan ortak işlevleri içerir.
"""

import os

from fastapi import APIRouter
from sqlalchemy.orm import Session

from ..database import Base, SessionLocal, get_engine


def get_db():
    """
    TR: Her istek için veritabanı oturumu sağlar.
    EN: Provides a database session per request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables_if_needed():
    """Tabloları sadece production ortamında oluşturur."""
    if (
        os.getenv("ENVIRONMENT") != "test"
        and os.getenv("USE_MOCK") != "true"
        and os.getenv("TESTING") != "true"
    ):
        try:
            engine = get_engine()
            Base.metadata.create_all(bind=engine)
            print("Tüm tablolar güncel modellerle oluşturuldu.")
        except Exception as e:
            print(f"Tablo oluşturma hatası (göz ardı edildi): {e}")
