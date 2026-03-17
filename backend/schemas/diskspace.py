"""
Disk space schema for *arr API responses.

Provides a unified schema for disk space information from all *arr services.
"""

from pydantic import BaseModel, Field


class DiskSpace(BaseModel):
    """
    Disk space information for a single root folder.
    
    This schema represents disk space usage for a specific path,
    as returned by *arr services' disk space endpoints.
    """
    
    path: str = Field(description="The root folder path")
    label: str = Field(default="", description="Human-readable label for the path")
    total: int = Field(description="Total space in bytes")
    used: int = Field(description="Used space in bytes")
    free: int = Field(description="Free space in bytes")
    
    @property
    def percent_used(self) -> float:
        """Calculate the percentage of disk space used."""
        if self.total == 0:
            return 0.0
        return (self.used / self.total) * 100
    
    @property
    def total_gb(self) -> float:
        """Total space in gigabytes."""
        return self.total / (1024 * 1024 * 1024)
    
    @property
    def used_gb(self) -> float:
        """Used space in gigabytes."""
        return self.used / (1024 * 1024 * 1024)
    
    @property
    def free_gb(self) -> float:
        """Free space in gigabytes."""
        return self.free / (1024 * 1024 * 1024)
    
    class Config:
        extra = "ignore"
        json_schema_extra = {
            "example": {
                "path": "/movies",
                "label": "Movies",
                "total": 1099511627776,
                "used": 549755813888,
                "free": 549755813888,
            }
        }


class ServiceDiskSpace(BaseModel):
    """
    Disk space information for a single service.
    
    Aggregates all root folder disk spaces for one *arr service.
    """
    
    service: str = Field(description="Service name (radarr, sonarr, lidarr)")
    service_name: str = Field(description="Display name for the service")
    disk_spaces: list[DiskSpace] = Field(default_factory=list, description="List of disk spaces for this service")
    status: str = Field(default="unknown", description="Service status: online, offline, not_configured")
    error: str | None = Field(default=None, description="Error message if fetch failed")
    
    class Config:
        extra = "ignore"


class AggregatedDiskSpace(BaseModel):
    """
    Aggregated disk space information from all configured services.
    
    This is the top-level response returned by the disk space endpoint.
    """
    
    services: list[ServiceDiskSpace] = Field(default_factory=list, description="Disk space for each service")
    total_services: int = Field(description="Total number of services checked")
    online_services: int = Field(description="Number of services that responded successfully")
    
    class Config:
        extra = "ignore"
