"""
Interface definitions for loose coupling.
Modüller arası bağımlılıkları azaltmak için interface'ler tanımlar.
"""

from .auth_interface import AuthInterface
from .database_interface import DatabaseInterface
from .settings_interface import SettingsInterface

__all__ = ["AuthInterface", "DatabaseInterface", "SettingsInterface"]
