"""
Configuration settings for Orchestratorr backend.

Manages environment variables and application settings.
"""

from typing import Optional, List

from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    # Radarr Configuration
    radarr_url: Optional[str] = None
    radarr_api_key: Optional[str] = None

    # Sonarr Configuration
    sonarr_url: Optional[str] = None
    sonarr_api_key: Optional[str] = None

    # Lidarr Configuration
    lidarr_url: Optional[str] = None
    lidarr_api_key: Optional[str] = None

    # Prowlarr Configuration
    prowlarr_url: Optional[str] = None
    prowlarr_api_key: Optional[str] = None

    # FastAPI Configuration
    fastapi_host: str = "0.0.0.0"
    fastapi_port: int = 8000
    fastapi_reload: bool = True

    # Frontend Configuration
    frontend_url: str = "http://localhost:5173"
    allowed_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("allowed_origins", pre=True)
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return v.split(",")
        return v


# Create settings instance
settings = Settings()