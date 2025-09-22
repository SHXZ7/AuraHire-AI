# backend/database/__init__.py

from .connection import init_database, close_database
from .config import DatabaseConfig

__all__ = ["init_database", "close_database", "DatabaseConfig"]