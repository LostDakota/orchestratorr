"""
System-level monitoring routes for Orchestratorr.

Provides endpoints for system-related information such as disk space.
"""

import os
import shutil
from typing import List, Dict
from .proxy import get_radarr_client, get_lidarr_client, get_sonarr_client
from backend.schemas import DiskSpace, ClientUsedSpace
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1/system", tags=["system"])

@router.get("/disk-space")
async def get_system_disk_space() -> List[DiskSpace]:
    """
    API endpoint to retrieve disk space information.
    
    Query Parameters:
    - paths (optional): List of paths to check
    
    Returns:
        List of disk space information for specified paths
    """
    try:
        return await get_disk_space()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve disk space: {str(e)}")