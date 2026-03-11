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
from backend.clients.sonarr import SonarrClient
from backend.clients.lidarr import LidarrClient
from backend.clients.prowlarr import ProwlarrClient
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


def get_sonarr_client() -> Optional[SonarrClient]:
    """
    Dependency injection for SonarrClient.

    Reads configuration from environment variables (via settings) and instantiates
    a SonarrClient with the appropriate base URL and API key.

    Returns:
        SonarrClient: Configured async client for Sonarr API, or None if not configured
    """
    if not settings.sonarr_url or not settings.sonarr_api_key:
        logger.debug("Sonarr not configured (SONARR_URL or SONARR_API_KEY missing)")
        return None

    return SonarrClient(base_url=settings.sonarr_url, api_key=settings.sonarr_api_key)


def get_lidarr_client() -> Optional[LidarrClient]:
    """
    Dependency injection for LidarrClient.

    Reads configuration from environment variables (via settings) and instantiates
    a LidarrClient with the appropriate base URL and API key.

    Returns:
        LidarrClient: Configured async client for Lidarr API, or None if not configured
    """
    if not settings.lidarr_url or not settings.lidarr_api_key:
        logger.debug("Lidarr not configured (LIDARR_URL or LIDARR_API_KEY missing)")
        return None

    return LidarrClient(base_url=settings.lidarr_url, api_key=settings.lidarr_api_key)


def get_prowlarr_client() -> Optional[ProwlarrClient]:
    """
    Dependency injection for ProwlarrClient.

    Reads configuration from environment variables (via settings) and instantiates
    a ProwlarrClient with the appropriate base URL and API key.

    Returns:
        ProwlarrClient: Configured async client for Prowlarr API, or None if not configured
    """
    if not settings.prowlarr_url or not settings.prowlarr_api_key:
        logger.debug("Prowlarr not configured (PROWLARR_URL or PROWLARR_API_KEY missing)")
        return None

    return ProwlarrClient(base_url=settings.prowlarr_url, api_key=settings.prowlarr_api_key)


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


# ============================================================================
# Sonarr Routes
# ============================================================================


@router.get("/sonarr/status")
async def get_sonarr_status(
    sonarr: Optional[SonarrClient] = Depends(get_sonarr_client),
) -> dict:
    """
    Get Sonarr system status and version information.

    Returns:
        dict: Sonarr status response (see SonarrClient.get_status())

    Raises:
        HTTPException: If Sonarr is unreachable or returns an error
    """
    if not sonarr:
        raise HTTPException(status_code=503, detail="Sonarr not configured")
    try:
        return await sonarr.get_status()
    except Exception as e:
        logger.error(f"Sonarr status request failed: {str(e)}")
        raise


@router.get("/sonarr/series")
async def get_sonarr_series(
    sonarr: Optional[SonarrClient] = Depends(get_sonarr_client),
    search: Optional[str] = Query(None, description="Search term for series title"),
    monitored: Optional[bool] = Query(None, description="Filter by monitored status"),
    status: Optional[str] = Query(
        None, description="Filter by status (Continuing, Ended, etc.)"
    ),
) -> list | dict:
    """
    Get Sonarr series library with optional filtering.

    Query Parameters:
    - search (str): Filter series by title (case-insensitive substring match)
    - monitored (bool): Filter by monitored status (true/false)
    - status (str): Filter by status (Continuing, Ended, etc.)

    Returns:
        list: List of series matching the filters

    Example:
        GET /api/v1/proxy/sonarr/series?monitored=true&status=Continuing

    Raises:
        HTTPException: If Sonarr is unreachable or returns an error
    """
    if not sonarr:
        raise HTTPException(status_code=503, detail="Sonarr not configured")
    try:
        series = await sonarr.get_series()

        # If no filters, return all series
        if not any([search, monitored is not None, status]):
            return series

        # Apply filters
        filtered = series
        if search:
            search_lower = search.lower()
            filtered = [s for s in filtered if search_lower in s.get("title", "").lower()]

        if monitored is not None:
            filtered = [s for s in filtered if s.get("monitored") == monitored]

        if status:
            filtered = [s for s in filtered if s.get("status") == status]

        return filtered

    except Exception as e:
        logger.error(f"Sonarr series list request failed: {str(e)}")
        raise


@router.get("/sonarr/series/{series_id}")
async def get_sonarr_series_by_id(
    series_id: int,
    sonarr: Optional[SonarrClient] = Depends(get_sonarr_client),
) -> dict:
    """
    Get a specific Sonarr series by ID.

    Parameters:
        series_id (int): Sonarr internal series ID

    Returns:
        dict: Series object with full metadata

    Raises:
        HTTPException: If series not found or Sonarr is unreachable
    """
    if not sonarr:
        raise HTTPException(status_code=503, detail="Sonarr not configured")
    try:
        return await sonarr.get_series(series_id=series_id)
    except Exception as e:
        logger.error(f"Sonarr series detail request failed: {str(e)}")
        raise


# ============================================================================
# Lidarr Routes
# ============================================================================


@router.get("/lidarr/status")
async def get_lidarr_status(
    lidarr: Optional[LidarrClient] = Depends(get_lidarr_client),
) -> dict:
    """
    Get Lidarr system status and version information.

    Returns:
        dict: Lidarr status response (see LidarrClient.get_status())

    Raises:
        HTTPException: If Lidarr is unreachable or returns an error
    """
    if not lidarr:
        raise HTTPException(status_code=503, detail="Lidarr not configured")
    try:
        return await lidarr.get_status()
    except Exception as e:
        logger.error(f"Lidarr status request failed: {str(e)}")
        raise


@router.get("/lidarr/artists")
async def get_lidarr_artists(
    lidarr: Optional[LidarrClient] = Depends(get_lidarr_client),
    search: Optional[str] = Query(None, description="Search term for artist name"),
    monitored: Optional[bool] = Query(None, description="Filter by monitored status"),
) -> list | dict:
    """
    Get Lidarr artist library with optional filtering.

    Query Parameters:
    - search (str): Filter artists by name (case-insensitive substring match)
    - monitored (bool): Filter by monitored status (true/false)

    Returns:
        list: List of artists matching the filters

    Example:
        GET /api/v1/proxy/lidarr/artists?monitored=true

    Raises:
        HTTPException: If Lidarr is unreachable or returns an error
    """
    if not lidarr:
        raise HTTPException(status_code=503, detail="Lidarr not configured")
    try:
        artists = await lidarr.get_artists()

        # If no filters, return all artists
        if not any([search, monitored is not None]):
            return artists

        # Apply filters
        filtered = artists
        if search:
            search_lower = search.lower()
            filtered = [a for a in filtered if search_lower in a.get("artistName", "").lower()]

        if monitored is not None:
            filtered = [a for a in filtered if a.get("monitored") == monitored]

        return filtered

    except Exception as e:
        logger.error(f"Lidarr artists list request failed: {str(e)}")
        raise


@router.get("/lidarr/artists/{artist_id}")
async def get_lidarr_artist_by_id(
    artist_id: int,
    lidarr: Optional[LidarrClient] = Depends(get_lidarr_client),
) -> dict:
    """
    Get a specific Lidarr artist by ID.

    Parameters:
        artist_id (int): Lidarr internal artist ID

    Returns:
        dict: Artist object with full metadata

    Raises:
        HTTPException: If artist not found or Lidarr is unreachable
    """
    if not lidarr:
        raise HTTPException(status_code=503, detail="Lidarr not configured")
    try:
        return await lidarr.get_artists(artist_id=artist_id)
    except Exception as e:
        logger.error(f"Lidarr artist detail request failed: {str(e)}")
        raise


# ============================================================================
# Prowlarr Routes
# ============================================================================


@router.get("/prowlarr/status")
async def get_prowlarr_status(
    prowlarr: Optional[ProwlarrClient] = Depends(get_prowlarr_client),
) -> dict:
    """
    Get Prowlarr system status and version information.

    Returns:
        dict: Prowlarr status response (see ProwlarrClient.get_status())

    Raises:
        HTTPException: If Prowlarr is unreachable or returns an error
    """
    if not prowlarr:
        raise HTTPException(status_code=503, detail="Prowlarr not configured")
    try:
        return await prowlarr.get_status()
    except Exception as e:
        logger.error(f"Prowlarr status request failed: {str(e)}")
        raise


@router.get("/prowlarr/indexers")
async def get_prowlarr_indexers(
    prowlarr: Optional[ProwlarrClient] = Depends(get_prowlarr_client),
    search: Optional[str] = Query(None, description="Search term for indexer name"),
    enabled: Optional[bool] = Query(None, description="Filter by enabled status"),
) -> list | dict:
    """
    Get Prowlarr indexers with optional filtering.

    Query Parameters:
    - search (str): Filter indexers by name (case-insensitive substring match)
    - enabled (bool): Filter by enabled status (true/false)

    Returns:
        list: List of indexers matching the filters

    Example:
        GET /api/v1/proxy/prowlarr/indexers?enabled=true

    Raises:
        HTTPException: If Prowlarr is unreachable or returns an error
    """
    if not prowlarr:
        raise HTTPException(status_code=503, detail="Prowlarr not configured")
    try:
        indexers = await prowlarr.get_indexers()

        # If no filters, return all indexers
        if not any([search, enabled is not None]):
            return indexers

        # Apply filters
        filtered = indexers
        if search:
            search_lower = search.lower()
            filtered = [i for i in filtered if search_lower in i.get("name", "").lower()]

        if enabled is not None:
            filtered = [i for i in filtered if i.get("enabled") == enabled]

        return filtered

    except Exception as e:
        logger.error(f"Prowlarr indexers list request failed: {str(e)}")
        raise


@router.get("/prowlarr/indexers/{indexer_id}")
async def get_prowlarr_indexer_by_id(
    indexer_id: int,
    prowlarr: Optional[ProwlarrClient] = Depends(get_prowlarr_client),
) -> dict:
    """
    Get a specific Prowlarr indexer by ID.

    Parameters:
        indexer_id (int): Prowlarr internal indexer ID

    Returns:
        dict: Indexer object with full metadata

    Raises:
        HTTPException: If indexer not found or Prowlarr is unreachable
    """
    if not prowlarr:
        raise HTTPException(status_code=503, detail="Prowlarr not configured")
    try:
        return await prowlarr.get_indexers(indexer_id=indexer_id)
    except Exception as e:
        logger.error(f"Prowlarr indexer detail request failed: {str(e)}")
        raise


@router.post("/sonarr/series")
async def sonarr_add_series(
    tvdb_id: int,
    title: str,
    quality_profile_id: int,
    root_folder_path: str,
    monitored: bool = True,
    sonarr: Optional[SonarrClient] = Depends(get_sonarr_client),
) -> dict:
    """
    Add a new TV series to Sonarr.

    Request Body:
        {
            "tvdb_id": 81189,
            "title": "Breaking Bad",
            "quality_profile_id": 1,
            "root_folder_path": "/tv",
            "monitored": true
        }

    Returns:
        dict: Created series object with Sonarr ID and metadata

    Raises:
        HTTPException: If series already exists or Sonarr is unreachable
    """
    if not sonarr:
        raise HTTPException(status_code=503, detail="Sonarr not configured")
    try:
        return await sonarr.add_series(
            tvdb_id=tvdb_id,
            title=title,
            quality_profile_id=quality_profile_id,
            root_folder_path=root_folder_path,
            monitored=monitored,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sonarr add series failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add series: {str(e)}",
        )


@router.post("/lidarr/artists")
async def lidarr_add_artist(
    foreign_artist_id: str,
    artist_name: str,
    quality_profile_id: int,
    root_folder_path: str,
    monitored: bool = True,
    lidarr: Optional[LidarrClient] = Depends(get_lidarr_client),
) -> dict:
    """
    Add a new music artist to Lidarr.

    Request Body:
        {
            "foreign_artist_id": "uuid",
            "artist_name": "Radiohead",
            "quality_profile_id": 1,
            "root_folder_path": "/music",
            "monitored": true
        }

    Returns:
        dict: Created artist object with Lidarr ID and metadata

    Raises:
        HTTPException: If artist already exists or Lidarr is unreachable
    """
    if not lidarr:
        raise HTTPException(status_code=503, detail="Lidarr not configured")
    try:
        return await lidarr.add_artist(
            foreign_artist_id=foreign_artist_id,
            artist_name=artist_name,
            quality_profile_id=quality_profile_id,
            root_folder_path=root_folder_path,
            monitored=monitored,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lidarr add artist failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add artist: {str(e)}",
        )
