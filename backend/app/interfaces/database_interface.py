"""
Database interface for loose coupling.
"""

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session


class DatabaseInterface(ABC):
    """Database interface for loose coupling."""

    @abstractmethod
    def get_session(self) -> Session:
        """Get database session."""
        pass

    @abstractmethod
    def create_tables(self) -> None:
        """Create database tables."""
        pass

    @abstractmethod
    def get_engine(self):
        """Get database engine."""
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Test database connection."""
        pass
