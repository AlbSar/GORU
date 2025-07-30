"""
Settings interface for loose coupling.
"""

from abc import ABC, abstractmethod
from typing import List


class SettingsInterface(ABC):
    """Settings interface for loose coupling."""

    @abstractmethod
    def get_database_url(self) -> str:
        """Get database URL."""
        pass

    @abstractmethod
    def get_jwt_secret_key(self) -> str:
        """Get JWT secret key."""
        pass

    @abstractmethod
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins."""
        pass

    @abstractmethod
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        pass

    @abstractmethod
    def is_mock_enabled(self) -> bool:
        """Check if mock mode is enabled."""
        pass
