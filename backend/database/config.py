# backend/database/config.py

import os
from typing import Optional
from pydantic_settings import BaseSettings

class DatabaseConfig(BaseSettings):
    """PostgreSQL database configuration using environment variables"""
    
    # Database URL (primary method)
    database_url: Optional[str] = os.getenv("DATABASE_URL")
    
    # Fallback PostgreSQL connection parameters (if DATABASE_URL not provided)
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    postgres_db: str = os.getenv("POSTGRES_DB", "resume_matcher")
    postgres_user: str = os.getenv("POSTGRES_USER", "postgres")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "password")
    
    # Connection pool settings
    pool_size: int = int(os.getenv("DB_POOL_SIZE", "5"))
    max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    pool_timeout: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    pool_recycle: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    
    # Connection settings
    echo_sql: bool = os.getenv("DB_ECHO_SQL", "false").lower() == "true"
    
    def get_database_url(self) -> str:
        """Get the PostgreSQL database URL"""
        if self.database_url:
            return self.database_url
        else:
            # Fallback to building from individual components
            return (
                f"postgresql://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )
    
    def get_async_database_url(self) -> str:
        """Get the async PostgreSQL database URL for asyncpg"""
        if self.database_url:
            # Replace postgresql:// with postgresql+asyncpg://
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://")
        else:
            # Fallback to building from individual components
            return (
                f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global configuration instance
db_config = DatabaseConfig()