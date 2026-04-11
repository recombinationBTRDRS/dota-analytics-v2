"""Configuration management using pudantic-settings.

This module provides centralized configuration management with:
- Enviroment variable support
- .env file loading
- Type validation (Pydantic)
- Dependency injection for FastAPI
"""

from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from enviroment variables and .env file".
    
    Enviroment variables take precedence over .env file values.
    """

    # ========================================================================
    # SERVICE CONFIGURATION
    # ========================================================================
    SERVICE_NAME: str = Field(default="ingestion", description="Service name")
    SERVICE_PORT: int = Field(default= 8001, description="Service port") 
    DEBUG: bool = Field(default=True, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")


    # ========================================================================
    # OPENDOTA API CONFIGURATION
    # ========================================================================
    OPENDOTA_BASE_URL: str = Field(
        default="https://api.opendota.com/api",
        description="OpenDota API base URL"
    )
    OPENDOTA_TIMEOUT: int = Field(
        default=30,
        description="HTTP request timeout in seconds"
    )
    OPENDOTA_RETRIES: int = Field(
        default=3,
        description="Number of retry attempts for failed requests"
    ) 
    OPENDOTA_RATE_LIMIT: int = Field(
        default=60,
        description="Rate limit in requests per minute"
    )



    # ========================================================================
    # MATCH DISCOVERY CONFIGURATION
    # ========================================================================
    DISCOVERY_LOBBY_TYPE: int = Field(
        default=7,
        description="Lobby type filter (7 = ranked)"
    )
    DISCOVERY_MIN_RANK_TIER: int = Field(
        default=10,
        description="Minimum rank tier (10 = Herald)"
    )
    DISCOVERY_LIMIT: int = Field(
        default=100,
        description="Number of matches to discover per run"
    )
    DISCOVERY_INTERVAL_SEC: int = Field(
        default=300,
        description="Discovery scheduler interval in seconds"
    )

    # ========================================================================
    # DATABASE CONFIGURATION
    # ========================================================================
    MONGODB_URL: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URL"
    )
    MONGODB_DB_NAME: str = Field(
        default="dota2_analytics",
        description="MongoDB database name"
    )

    # ========================================================================
    # CACHE CONFIGURATION
    # ========================================================================
    REDIS_URL: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL"
    )
    REDIS_DB: int = Field(
        default=0,
        description="Redis datbase number"
    )

    # ========================================================================
    # AUTO-REBUILD CONFIGURATION
    # ========================================================================
    AUTO_REBUID_AFTER_INGEST: bool = Field(
        default=True,
        description="Automatically rebuild pre-computed stats after ingestion"
    )
    REBUILD_BATCH_THRESHOLD: int = Field(
        default=10,
        description="Number of mathes to trigger rebuild"
    )

    # ========================================================================
    # LOGGING CONFIGURATION
    # ========================================================================
    LOG_FORMAT: str = Field(
        default="json",
        description="Log format (json or text)"
    )

    # ========================================================================
    # CORS CONFIGURATION
    # ========================================================================
    CORS_ORIGINS: list[str] = Field(
        default=["*"],
        description="CORS allowed origins"
    )
    CORS_CREDENTIALS: bool = Field(
        default=True,
        description="Allow CORS credentials"
    )
    CORS_METHODS: list[str] = Field(
        default=["*"],
        description="CORS allowed methods"
    )
    CORS_HEADERS: list[str] = Field(
        default=["*"],
        description="CORS allowed headers"
    )


    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    @field_validator("OPENDOTA_TIMEOUT","DISCOVERY_INTERVAL_SEC")
    def validate_positive_nubers(cls, v: int) -> int:
        """Ensure timeout and interval are positive."""
        if v <= 0:
            raise ValueError("Must be a positive number")
        return v
    
    @field_validator("DISCOVERY_LIMIT", "REBUILD_BATCH_THRESHOLD")
    def validate_positive_integers(cls, v:int) -> int:
        """Ensure limits are positive integers."""
        if v <= 0:
            raise ValueError("Must be a positive integer")
        return v

    @field_validator("LOG_LEVEL")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is valid."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    
@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance (singleton pattern).

    Returns:
        Settings: Application settings instanse

    Example:
        settings = get_settings()
        print(settings.SERVICE_PORT) # 8001
        
    """
    return Settings()

# For FastAPI Depends
settings = get_settings()
