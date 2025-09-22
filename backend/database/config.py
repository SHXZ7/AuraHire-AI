# backend/database/config.py

import os
from typing import Optional
from pydantic import BaseSettings

class DatabaseConfig(BaseSettings):
    """MongoDB database configuration using environment variables"""

    # MongoDB URL (primary method)
    mongodb_url: Optional[str] = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

    # Database name
    database_name: str = os.getenv("MONGODB_DATABASE", "aurahire_ai")

    # Connection settings
    max_connections: int = int(os.getenv("MONGODB_MAX_CONNECTIONS", "10"))
    min_connections: int = int(os.getenv("MONGODB_MIN_CONNECTIONS", "1"))

    # Connection timeout settings
    server_selection_timeout_ms: int = int(os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT", "5000"))
    connect_timeout_ms: int = int(os.getenv("MONGODB_CONNECT_TIMEOUT", "10000"))
    socket_timeout_ms: int = int(os.getenv("MONGODB_SOCKET_TIMEOUT", "5000"))

    # Additional settings
    retry_writes: bool = os.getenv("MONGODB_RETRY_WRITES", "true").lower() == "true"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra environment variables

    def get_mongodb_url(self) -> str:
        """Get the MongoDB connection URL"""
        return self.mongodb_url

    def get_database_name(self) -> str:
        """Get the database name"""
        return self.database_name

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global configuration instance
db_config = DatabaseConfig()
