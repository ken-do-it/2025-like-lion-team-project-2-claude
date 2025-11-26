# -*- coding: utf-8 -*-
"""
Configuration management using Pydantic Settings
Loads environment variables from .env file
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    # Application
    APP_NAME: str = "AI Music Sharing Platform API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/music_db"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False  # Set to True for SQL query logging

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_TTL_JWKS: int = 3600  # 1 hour
    REDIS_TTL_TRACK_METADATA: int = 300  # 5 minutes
    REDIS_TTL_USER_PROFILE: int = 600  # 10 minutes
    REDIS_TTL_TRENDING: int = 60  # 1 minute

    # Auth Server
    AUTH_SERVER_URL: str = "https://auth.example.com"
    JWKS_URL: str = "https://auth.example.com/.well-known/jwks.json"
    JWT_ALGORITHM: str = "RS256"
    JWT_AUDIENCE: Optional[str] = "music-api"

    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "music-files"
    S3_PRESIGNED_URL_EXPIRATION: int = 3600  # 1 hour

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080"
    CORS_ALLOW_CREDENTIALS: bool = True

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Celery (optional)
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Pydantic Settings Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """
        Convert CORS_ORIGINS string to list
        """
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        """
        Check if running in production environment
        """
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """
        Check if running in development environment
        """
        return self.ENVIRONMENT.lower() == "development"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    Using lru_cache to create singleton pattern
    """
    return Settings()


# Convenience accessor
settings = get_settings()
