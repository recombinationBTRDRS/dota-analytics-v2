from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from enviroment variables"""

    # Service
    SERVICE_NAME: str = "ingestion"
    SERVICE_PORT: int = 8001
    DEBUG: bool = True

    # OpenDota API
    OPENDOTA_BASE_URL: str = "https://api.opendota.com/api"
    OPENDOTA_TIMEOUT: int = 30
    OPENDOTA_RETRIES: int = 3
    OPENDOTA_RATE_LIMIT: int = 60

    # Discovery settings
    DISCOVERY_LOBBY_TYPE: int = 7 # 7 = ranked
    DISCOVERY_MIN_RANK_TIER: int = 10 # Herald
    DISCOVERY_INTERVAL_SEC: int = 300 # 5 minutes

    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "dota2_analytics"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json" 

    # Auto rebuild
    AUTO_REBUILD_AFTER_INGEST: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# For FastAPI Depends
settings = get_settings()
