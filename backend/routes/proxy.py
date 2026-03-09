"""
FastAPI proxy router for *arr services.

Routes all incoming requests from the frontend to the appropriate *arr client
(Radarr, Sonarr, Lidarr, Prowlarr) and aggregates responses.

All routes are prefixed with /api/v1/proxy.
"""

import asyncio
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from backend.clients.radarr import RadarrClient
from backend.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/proxy", tags=["proxy"])


# ============================================================================
# Dependency Injection
# ============================================================================


def get_radarr_client() -> RadarrClient:
    """
    Dependency injection for RadarrClient.

    Reads configuration from environment variables (via settings) and instantiates
    a RadarrClient with the appropriate base URL and API key.

    Returns:
        RadarrClient: Configured async client for Radarr API

    Raises:
        HTTPException: If required configuration is missing
    """
    if not settings.radarr_url or not settings.radarr_api_key:
        logger.error("Missing Radarr configuration (RADARR_URL or RADARR_API_KEY)")
        raise HTTPException(
            status_code=503,
            detail="Radarr service not configured",
        )

    return RadarrClient(base_url=settings.radarr_url, api_key=settings.radarr_api_key)


def get_sonarr_client() -> Optional[RadarrClient]:
    """
    Dependency injection for Sonarr client (placeholder).

    Currently returns None. Implement when Sonarr client is available.

    Returns:
        None
    """
    # TODO: Implement SonarrClient
    return None


def get_lidarr_client() -> Optional[RadarrClient]:
    """
    Dependency injection for Lidarr client (placeholder).

    Currently returns None. Implement when Lidarr client is available.

    Returns:
        None
    """
    # TODO: Implement LidarrClient
    return None


def get_prowlarr_client() -> Optional[RadarrClient]:
    """
    Dependency injection for Prowlarr client (placeholder).

    Currently returns None. Implement when Prowlarr client is available.

    Returns:
        None
    """
    # TODO: ImplementProwlarrClient
    return None


# ============================================================================
# Aggregate Health Check Routes
# ============================================================================


@router.get("/status")
async def get_aggregate_status(
    radarr: RadarrClient = Depends(get_radarr_client),
) -> dict:
    """
    Get aggregated health status for all *arr services.

    Concurrently fetches status from all available services without blocking.
    Returns a unified JSON object with each service's status and version.

    Returns:
        dict: Aggregated status object
        {
            "radarr": {
                "status": "online" | "offline" | "degraded",
                "version": "4.7.0.7191",
                "uptime": true
            },
            "sonarr": {...},
            "lidarr": {...},
            "prowlarr": {...},
            "timestamp": "2026-03-09T00:17:00Z"
        }

    Note:
        If a service fails, its status is set to "offline" and the request
        does not fail. The API remains available even if individual services
        are down.
    """

    async def fetch_service_status(client, service_name):
        """Fetch status for a single service, handling errors gracefully."""
        if client is None:
            return {service_name: {"status": "not_configured", "version": None}}

        try:
            status = await client.get_status()
            return {
                service_name: {
                    "status": "online",
                    "version": status.get("version", "Unknown"),
                    "uptime": True,
                }
            }
        except HTTPException as e:
            logger.warning(f"{service_name} returned HTTP error: {e.status_code}")
            return {
                service_name: {
                    "status": "offline" if e.status_code >= 500 else "degraded",
                    "version": None,
                    "uptime": False,
                }
            }
        except Exception as e:
            logger.error(f"Error fetching {service_name} status: {str(e)}")
            return {
                service_name: {
                    "status": "offline",
                    "version": None,
                    "uptime": False,
                }
            }

    # Fetch all service statuses concurrently
    results = await asyncio.gather(
        fetch_service_status(radarr, "radarr"),
        fetch_service_status(get_sonarr_client(), "sonarr"),
        fetch_service_status(get_lidarr_client(), "lidarr"),
        fetch_service_status(get_prowlarr_client(), "prowlarr"),
    )

    # Aggregate results
    aggregated = {}
    for result in results:
        aggregated.update(result)

    # Add timestamp
    from datetime import datetime, timezone

    aggregated["timestamp"] = datetime.now(timezone.utc).isoformat()

    return aggregated


# ============================================================================
# Radarr Routes
# ============================================================================


@router.get("/radarr/status")
async def get_radarr_status(
    radarr: RadarrClient = Depends(get_radarr_client),
) -> dict:
    """
    Get Radarr system status and version information.

    Returns:
        dict: Radarr status response (see RadarrClient.get_status())

    Raises:
        HTTPException: If Radarr is unreachable or returns an error
    """
    try:
        return await radarr.get_status()
    except Exception as e:
        logger.error(f"Radarr status request failed: {str(e)}")
        raise


@router.get("/radarr/movies")
async def get_radarr_movies(
    radarr: RadarrClient = Depends(get_radarr_client),
    search: Optional[str] = Query(None, description="Search term for movie title"),
    monitored: Optional[bool] = Query(None, description="Filter by monitored status"),
    status: Optional[str] = Query(
        None, description="Filter by status (Missing, Downloaded, etc.)"
    ),
) -> list | dict:
    """
    Get Radarr movie library with optional filtering.

    Query Parameters:
    - search (str): Filter movies by title (case-insensitive substring match)
    - monitored (bool): Filter by monitored status (true/false)
    - status (str): Filter by status (Missing, Downloaded, Announced, etc.)

    Returns:
        list: List of movies matching the filters

    Example:
        GET /api/v1/proxy/radarr/movies?monitored=true&status=Downloaded

    Raises:
        HTTPException: If Radarr is unreachable or returns an error
    """
    try:
        movies = await radarr.get_movies()

        # If no filters, return all movies
        if not any([search, monitored is not None, status]):
            return movies

        # Apply filters
        filtered = movies
        if search:
            search_lower = search.lower()
            filtered = [m for m in filtered if search_lower in m.get("title", "").lower()]

        if monitored is not None:
            filtered = [m for m in filtered if m.get("monitored") == monitored]

        if status:
            filtered = [m for m in filtered if m.get("status") == status]

        return filtered

    except Exception as e:
        logger.error(f"Radarr movie list request failed: {str(e)}")
        raise


@router.get("/radarr/movies/{movie_id}")
async def get_radarr_movie(
    movie_id: int,
    radarr: RadarrClient = Depends(get_radarr_client),
) -> dict:
    """
    Get a specific Radarr movie by ID.

    Parameters:
        movie_id (int): Radarr internal movie ID

    Returns:
        dict: Movie object with full metadata

    Raises:
        HTTPException: If movie not found or Radarr is unreachable
    """
    try:
        return await radarr.get_movies(movie_id=movie_id)
    except Exception as e:
        logger.error(f"Radarr movie detail request failed: {str(e)}")
        raise


@router.post("/radarr/command/search")
async def radarr_search_movies(
    movie_ids: list[int],
    radarr: RadarrClient = Depends(get_radarr_client),
) -> dict:
    """
    Trigger a manual search for missing Radarr movies.

    Request Body:
        {
            "movie_ids": [1, 2, 3]
        }

    Returns:
        dict: Command response with command ID and status

    Raises:
        HTTPException: If command fails or Radarr is unreachable
    """
    try:
        if not movie_ids:
            raise HTTPException(
                status_code=400,
                detail="movie_ids cannot be empty",
            )

        return await radarr.command_search(movie_ids)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Radarr search command failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Search command failed: {str(e)}",
        )


@router.post("/radarr/command/refresh")
async def radarr_refresh_movies(
    movie_ids: Optional[list[int]] = None,
    radarr: RadarrClient = Depends(get_radarr_client),
) -> dict:
    """
    Trigger a refresh of movie metadata from sources.

    Request Body (optional):
        {
            "movie_ids": [1, 2, 3]  // Refresh specific movies, or omit to refresh all
        }

    Returns:
        dict: Command response with command ID and status

    Raises:
        HTTPException: If command fails or Radarr is unreachable
    """
    try:
        if movie_ids and len(movie_ids) == 1:
            return await radarr.command_refresh(movie_id=movie_ids[0])
        else:
            return await radarr.command_refresh()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Radarr refresh command failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Refresh command failed: {str(e)}",
        )


@router.get("/radarr/calendar")
async def get_radarr_calendar(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    radarr: RadarrClient = Depends(get_radarr_client),
) -> list:
    """
    Get Radarr upcoming releases calendar.

    Query Parameters:
    - start_date (str): Start date in ISO 8601 format (YYYY-MM-DD)
    - end_date (str): End date in ISO 8601 format (YYYY-MM-DD)

    Returns:
        list: Calendar events for upcoming releases

    Example:
        GET /api/v1/proxy/radarr/calendar?start_date=2026-03-01&end_date=2026-03-31

    Raises:
        HTTPException: If Radarr is unreachable or returns an error
    """
    try:
        return await radarr.get_calendar(start_date=start_date, end_date=end_date)
    except Exception as e:
        logger.error(f"Radarr calendar request failed: {str(e)}")
        raise


@router.post("/radarr/movies")
async def radarr_add_movie(
    tmdb_id: int,
    title: str,
    quality_profile_id: int,
    root_folder_path: str,
    monitored: bool = True,
    radarr: RadarrClient = Depends(get_radarr_client),
) -> dict:
    """
    Add a new movie to Radarr.

    Request Body:
        {
            "tmdb_id": 550,
            "title": "Fight Club",
            "quality_profile_id": 1,
            "root_folder_path": "/movies",
            "monitored": true
        }

    Returns:
        dict: Created movie object with Radarr ID and metadata

    Raises:
        HTTPException: If movie already exists or Radarr is unreachable
    """
    try:
        return await radarr.add_movie(
            tmdb_id=tmdb_id,
            title=title,
            quality_profile_id=quality_profile_id,
            root_folder_path=root_folder_path,
            monitored=monitored,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Radarr add movie failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add movie: {str(e)}",
        )


@router.delete("/radarr/movies/{movie_id}")
async def radarr_delete_movie(
    movie_id: int,
    delete_files: bool = Query(False, description="Also delete downloaded files"),
    radarr: RadarrClient = Depends(get_radarr_client),
) -> JSONResponse:
    """
    Remove a movie from Radarr.

    Parameters:
        movie_id (int): Radarr movie ID
        delete_files (bool): If true, also delete downloaded files

    Returns:
        JSONResponse: Success confirmation

    Raises:
        HTTPException: If movie not found or Radarr is unreachable
    """
    try:
        await radarr.delete_movie(movie_id=movie_id, delete_files=delete_files)
        return JSONResponse(
            {"status": "success", "message": f"Movie {movie_id} deleted"},
            status_code=204,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Radarr delete movie failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete movie: {str(e)}",
        )
