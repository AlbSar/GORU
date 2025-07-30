"""
Database bağlantı ve session testleri
"""

import pytest
from app.database import create_tables, get_db, get_engine, test_connection
from sqlalchemy.exc import SQLAlchemyError


def test_database_connection():
    """Database bağlantı testi"""
    assert test_connection() is True


def test_create_tables():
    """Tablo oluşturma testi"""
    assert create_tables() is True


def test_get_db():
    """Database session generator testi"""
    db = next(get_db())
    try:
        assert db is not None
        # Test transaction
        db.begin()
        db.rollback()
    finally:
        db.close()


def test_db_rollback():
    """Transaction rollback testi"""
    db = next(get_db())
    try:
        db.begin()
        # Invalid SQL to force error
        with pytest.raises(SQLAlchemyError):
            db.execute("INVALID SQL")
        db.rollback()
    finally:
        db.close()


def test_multiple_connections():
    """Çoklu bağlantı testi"""
    engine = get_engine()
    Session1 = next(get_db())
    Session2 = next(get_db())

    try:
        assert Session1 is not None
        assert Session2 is not None
        assert Session1 is not Session2
    finally:
        Session1.close()
        Session2.close()
