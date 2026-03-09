"""
Configuration management for orchestratorr backend.

Loads environment variables and provides a centralized config object.
"""

import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Supports both .env files and environment variables. Use python-dotenv
    to load .env files automatically.
    """

    # ========================================================================
    # Radarr Configuration
    # ========================================================================
    radarr_url: str = os.getenv("RADARR_URL", "http://localhost:7878")
    radarr_api_key: str = os.getenv("RADARR_API_KEY", "")

    # ========================================================================
    # Sonarr Configuration
    # ========================================================================
    sonarr_url: Optional[str] = os.getenv("SONARR_URL")
    sonarr_api_key: Optional[str] = os.getenv("SONARR_API_KEY")

    # ========================================================================
    # Lidarr Configuration
    # ========================================================================
    lidarr_url: Optional[str] = os.getenv("LIDARR_URL")
    lidarr_api_key: Optional[str] = os.getenv("LIDARR_API_KEY")

    # ========================================================================
    # Prowlarr Configuration
    # ========================================================================
    prowlarr_url: Optional[str] = os.getenv("PROWLARR_URL")
    prowlarr_api_key: Optional[str] = os.getenv("PROWLARR_API_KEY")

    # ========================================================================
    # Server Configuration
    # ========================================================================
    fastapi_host: str = os.getenv("FASTAPI_HOST", "0.0.0.0")
    fastapi_port: int = int(os.getenv("FASTAPI_PORT", "8000"))
    fastapi_reload: bool = os.getenv("FASTAPI_RELOAD", "true").lower() == "true"

    # ========================================================================
    # Frontend Configuration
    # ========================================================================
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    allowed_origins: list[str] = [
        o.strip()
        for o in os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:5173,http://localhost:3000",
        ).split(",")
    ]

    # ========================================================================
    # Logging Configuration
    # ========================================================================
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # ========================================================================
    # API Configuration
    # ========================================================================
    api_version: str = "v1"
    api_prefix: str = "/api/v1"

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
