"""
System-level monitoring routes for Orchestratorr.

Provides endpoints for system-related information such as disk space.
"""

import asyncio
import logging
from typing import List, Dict, Optional

from fastapi import APIRouter, HTTPException

from backend.schemas import DiskSpace
from backend.clients.radarr import RadarrClient
from backend.clients.sonarr import SonarrClient
from backend.clients.lidarr import LidarrClient
from backend.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/system", tags=["system"])


class ServiceDiskInfo:
    """Helper class to store disk space info for a service."""
    def __init__(self, name: str, display_name: str):
        self.name = name
        self.display_name = display_name
        self.disk_spaces: List[DiskSpace] = []
        self.status = "unknown"
        self.error: Optional[str] = None


async def fetch_radarr_disk_space() -> ServiceDiskInfo:
    """Fetch disk space from Radarr."""
    info = ServiceDiskInfo("radarr", "Radarr")
    
    if not settings.radarr_url or not settings.radarr_api_key:
        info.status = "not_configured"
        return info
    
    try:
        client = RadarrClient(base_url=settings.radarr_url, api_key=settings.radarr_api_key)
        async with client:
            disk_spaces = await client.get_disk_space()
            info.disk_spaces = disk_spaces
            info.status = "online"
    except Exception as e:
        logger.error(f"Failed to fetch Radarr disk space: {e}")
        info.status = "offline"
        info.error = str(e)
    
    return info


async def fetch_sonarr_disk_space() -> ServiceDiskInfo:
    """Fetch disk space from Sonarr."""
    info = ServiceDiskInfo("sonarr", "Sonarr")
    
    if not settings.sonarr_url or not settings.sonarr_api_key:
        info.status = "not_configured"
        return info
    
    try:
        client = SonarrClient(base_url=settings.sonarr_url, api_key=settings.sonarr_api_key)
        async with client:
            disk_spaces = await client.get_disk_space()
            info.disk_spaces = disk_spaces
            info.status = "online"
    except Exception as e:
        logger.error(f"Failed to fetch Sonarr disk space: {e}")
        info.status = "offline"
        info.error = str(e)
    
    return info


async def fetch_lidarr_disk_space() -> ServiceDiskInfo:
    """Fetch disk space from Lidarr."""
    info = ServiceDiskInfo("lidarr", "Lidarr")
    
    if not settings.lidarr_url or not settings.lidarr_api_key:
        info.status = "not_configured"
        return info
    
    try:
        client = LidarrClient(base_url=settings.lidarr_url, api_key=settings.lidarr_api_key)
        async with client:
            disk_spaces = await client.get_disk_space()
            info.disk_spaces = disk_spaces
            info.status = "online"
    except Exception as e:
        logger.error(f"Failed to fetch Lidarr disk space: {e}")
        info.status = "offline"
        info.error = str(e)
    
    return info


@router.get("/disk-space")
async def get_system_disk_space() -> Dict:
    """
    API endpoint to retrieve disk space information from all configured services.
    
    Fetches disk space from Radarr, Sonarr, and Lidarr concurrently.
    Each service can have multiple root folders with their own disk space.
    
    Returns:
        Dict containing:
        - services: List of services with their disk space info
        - total_services: Number of services checked
        - online_services: Number of services that responded successfully
    """
    try:
        # Fetch all disk spaces concurrently
        results = await asyncio.gather(
            fetch_radarr_disk_space(),
            fetch_sonarr_disk_space(),
            fetch_lidarr_disk_space(),
        )
        
        # Convert to response format
        services = []
        online_count = 0
        
        for info in results:
            service_data = {
                "name": info.name,
                "display_name": info.display_name,
                "status": info.status,
                "disk_spaces": [
                    {
                        "path": ds.path,
                        "label": ds.label,
                        "free_space": ds.freeSpace,
                        "total_space": ds.totalSpace,
                        "used_space": ds.totalSpace - ds.freeSpace,
                        "percent_used": round(((ds.totalSpace - ds.freeSpace) / ds.totalSpace) * 100, 2) if ds.totalSpace > 0 else 0,
                        "free_gb": round(ds.freeSpace / (1024**3), 2),
                        "total_gb": round(ds.totalSpace / (1024**3), 2),
                        "used_gb": round((ds.totalSpace - ds.freeSpace) / (1024**3), 2),
                    }
                    for ds in info.disk_spaces
                ],
            }
            if info.error:
                service_data["error"] = info.error
            
            services.append(service_data)
            
            if info.status == "online":
                online_count += 1
        
        return {
            "services": services,
            "total_services": len(results),
            "online_services": online_count,
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve disk space: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve disk space: {str(e)}")
