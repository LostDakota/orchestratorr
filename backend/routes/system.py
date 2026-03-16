"""
System-level monitoring routes for Orchestratorr.

Provides endpoints for system-related information such as disk space.
"""

import os
import shutil
from typing import List, Dict

from fastapi import APIRouter, HTTPException

system_router = APIRouter(prefix="/api/v1/system", tags=["system"])

def get_disk_space(paths: List[str] = None) -> List[Dict]:
    """
    Retrieve disk space information for specified paths.
    
    If no paths are provided, use default media directories.
    
    Args:
        paths (List[str], optional): List of paths to check. Defaults to None.
    
    Returns:
        List[Dict]: Disk space information for each path
    """
    default_media_paths = [
        "/movies",
        "/tv",
        "/music"
    ]
    
    # Use provided paths or default paths
    check_paths = paths or default_media_paths
    
    disk_spaces = []
    
    for path in check_paths:
        try:
            # Ensure path exists
            if not os.path.exists(path):
                continue
            
            # Get disk usage statistics
            total, used, free = shutil.disk_usage(path)
            
            disk_spaces.append({
                "path": path,
                "total": total / (1024 * 1024 * 1024),  # Convert to GB
                "used": used / (1024 * 1024 * 1024),    # Convert to GB
                "free": free / (1024 * 1024 * 1024),    # Convert to GB
                "percent_used": (used / total) * 100
            })
        except Exception as e:
            # Log error but continue checking other paths
            print(f"Error checking disk space for {path}: {e}")
    
    return disk_spaces

@system_router.get("/disk-space")
async def get_system_disk_space(paths: List[str] = None) -> List[Dict]:
    """
    API endpoint to retrieve disk space information.
    
    Query Parameters:
    - paths (optional): List of paths to check
    
    Returns:
        List of disk space information for specified paths
    """
    try:
        return get_disk_space(paths)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve disk space: {str(e)}")