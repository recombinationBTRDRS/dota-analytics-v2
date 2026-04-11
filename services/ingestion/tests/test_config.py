"""Tests for configuration management.

Test suite for:
- Settings loading from enviroment
- .env file support
- Validation of settings values
- Dependency injection
"""

import pytest
import os 
from pathlib import Path
from pydantic import ValidationError

from app.config import Settings, get_settings


class TestSettingsDefaults:
    """Test default values for settings."""

    def test_default_service_name(self):
        """Test default service name."""
        settings = Settings()
        assert settings.SERVICE_NAME == "ingestion"
    
    def test_default_service_port(self):
        """Test default service port."""
        settings = Settings()
        assert settings.SERVICE_PORT == 8001
    
    def test_default_debug_mode(self):
        """Test default debug mode."""
        settings = Settings()
        assert settings.DEBUG is True
    
    def test_default_log_level(self):
        """Test default log level."""
        settings = Settings()
        assert settings.LOG_LEVEL == "INFO"
    
    def test_default_mongodb_db_name(self):
        """Test default MongoDB database name."""
        settings = Settings()
        assert settings.MONGODB_DB_NAME == "dota2_analytics"


class TestSettingsValidation:
    """Test validation of settings values."""

    def test_invalid_log_level(self):
        """Test that invalid log level raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(LOG_LEVEL="INVALID")
        assert "Log level must be one of" in str(exc_info.value)

    def test_valid_log_level(self):
        """Test that all valid log levels are accepted."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            settings = Settings(LOG_LEVEL=level)
            assert settings.LOG_LEVEL == level

    def test_invalid_timeout(self):
        """Test that negative timeout raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(OPENDOTA_TIMEOUT=-1)
        assert "Must be a positive number" in str(exc_info.value)

    def test_invalid_discovety_limit(self):
        """Test that zero discovery limit raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(DISCOVERY_LIMIT=0)
        assert "Must be a positive integer" in str(exc_info.value)

    def test_valid_timeout(self):
        """Test that positive timeout is accepted."""
        settings = Settings(OPENDOTA_TIMEOUT=60)
        assert settings.OPENDOTA_TIMEOUT == 60


class TestSettingsDependencyInjection:
    """Test dependency injection functionality."""

    def test_get_settings_returns_settings(self):
        """Teest that get_settings returns Settings instance."""
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_get_settings_is_singleton(self):
        """Test that get_settings returns same instancs (cached)."""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2

    def test_settings_module_instancs(self):
        """Test that settings module instance is avaliable"""
        from app.config import settings
        assert isinstance(settings, Settings)

class TestSettingsEnviromentVariables:
    """Test loading from enviroment variables."""

    def test_env_var_override(self, monkeypatch):
        """Test that enviroment variables override defaults."""
        monkeypatch.setenv("SERVICE_PORT", "9000")
        settings = Settings()
        assert settings.SERVICE_PORT == 9000

    def test_env_var_debug_mode(self, monkeypatch):
        """Test DEBUG environment variable."""
        monkeypatch.setenv("DEBUG", "false")
        settings = Settings()
        assert settings.DEBUG is False
    
    def test_env_var_log_level(self, monkeypatch):
        """Test LOG_LEVEL environment variable."""
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        settings = Settings()
        assert settings.LOG_LEVEL == "DEBUG"


class TestSettingsCors:
    """Test CORS configuration."""
    
    def test_default_cors_origins(self):
        """Test default CORS origins."""
        settings = Settings()
        assert "*" in settings.CORS_ORIGINS
    
    def test_default_cors_credentials(self):
        """Test default CORS credentials."""
        settings = Settings()
        assert settings.CORS_CREDENTIALS is True

class TestSettingsAutoRebuild:
    """Test auto-rebuild configuration."""

    def test_default_auto_rebuild_enabled(self):
        """Test that auto-rebuild is enabled by default ."""
        settings = Settings()
        assert settings.AUTO_REBUILD_AFTER_INGEST is True

    def test_rebuild_batch_threshold(self):
        """Test rebuild batch threshold."""
        settings = Settings()
        assert settings.REBUILD_BATCH_THRESHOLD == 10

class TestSettingsOpenDota:
    """Test OpenDota API configuration."""
    
    def test_default_opendota_url(self):
        """Test default OpenDota API URL."""
        settings = Settings()
        assert settings.OPENDOTA_BASE_URL == "https://api.opendota.com/api"
    
    def test_opendota_retries(self):
        """Test OpenDota retry count."""
        settings = Settings()
        assert settings.OPENDOTA_RETRIES == 3
    
    def test_opendota_rate_limit(self):
        """Test OpenDota rate limit."""
        settings = Settings()
        assert settings.OPENDOTA_RATE_LIMIT == 60