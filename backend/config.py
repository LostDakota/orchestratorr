"""
Configuration management for orchestratorr backend.

Loads environment variables and provides a centralized config object.
"""

import json
import os
from typing import Optional

from pydantic import field_validator
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
    allowed_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value):
        """Parse ALLOWED_ORIGINS from environment variable.
        
        Supports:
        1. JSON array: ["http://localhost:5173", "http://localhost:3000"]
        2. Comma-separated string: "http://localhost:5173,http://localhost:3000"
        3. List (already parsed by Pydantic)
        4. Empty/None: returns default list
        """
        if value is None:
            return ["http://localhost:5173", "http://localhost:3000"]
        
        # If it's already a list, return it
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        
        # Convert to string and try JSON parsing first
        str_value = str(value)
        
        # Try to parse as JSON
        try:
            parsed = json.loads(str_value)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except (json.JSONDecodeError, TypeError):
            pass
        
        # Fall back to comma-separated string
        return [url.strip() for url in str_value.split(",") if url.strip()]

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
