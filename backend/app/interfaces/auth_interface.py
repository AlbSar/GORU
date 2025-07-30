"""
Authentication interface for loose coupling.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional


class AuthInterface(ABC):
    """Authentication interface for loose coupling."""

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Hash a password."""
        pass

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password."""
        pass

    @abstractmethod
    def verify_token(self, token: str) -> Dict:
        """Verify a JWT token."""
        pass

    @abstractmethod
    def get_current_user(self, credentials: Optional[str] = None) -> Dict:
        """Get current authenticated user."""
        pass

    @abstractmethod
    def check_permission(self, required_permission: str):
        """Check if user has required permission."""
        pass
