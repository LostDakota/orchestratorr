"""
Universal search router for *arr services.

Aggregates search results from Radarr (movies) and Sonarr (TV shows)
using parallel async requests (asyncio.gather).

All routes are under /api/v1/search.
"""

import asyncio
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.clients.radarr import RadarrClient
from backend.clients.sonarr import SonarrClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/search", tags=["search"])


# ============================================================================
# Schemas
# ============================================================================


class SearchResult:
    """Universal search result combining data from multiple *arr services."""

    def __init__(
        self,
        title: str,
        year: Optional[int] = None,
        overview: Optional[str] = None,
        source_service: str = "unknown",
        source_type: str = "unknown",  # "movie" or "tv"
        remote_id: Optional[int] = None,
        tmdb_id: Optional[int] = None,
        imdb_id: Optional[str] = None,
        poster_url: Optional[str] = None,
        status: str = "missing",  # "missing", "downloading", "in_library"
        quality_profile_id: Optional[int] = None,
        in_library: bool = False,
    ):
        """
        Initialize a universal search result.

        Args:
            title: Movie/show title
            year: Release year
            overview: Plot summary
            source_service: Which service found this (radarr, sonarr)
            source_type: Type of content (movie, tv)
            remote_id: ID from the source service
            tmdb_id: TMDB database ID
            imdb_id: IMDb ID
            poster_url: Poster image URL
            status: Current status in library
            quality_profile_id: Associated quality profile
            in_library: Whether already in library
        """
        self.title = title
        self.year = year
        self.overview = overview or ""
        self.source_service = source_service
        self.source_type = source_type
        self.remote_id = remote_id
        self.tmdb_id = tmdb_id
        self.imdb_id = imdb_id
        self.poster_url = poster_url
        self.status = status
        self.quality_profile_id = quality_profile_id
        self.in_library = in_library

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "year": self.year,
            "overview": self.overview[:200] if self.overview else "",  # Truncate for API
            "source_service": self.source_service,
            "source_type": self.source_type,
            "remote_id": self.remote_id,
            "tmdb_id": self.tmdb_id,
            "imdb_id": self.imdb_id,
            "poster_url": self.poster_url,
            "status": self.status,
            "in_library": self.in_library,
        }


# ============================================================================
# Dependencies
# ============================================================================


def get_radarr_client() -> RadarrClient:
    """Dependency injection for RadarrClient."""
    import os

    radarr_url = os.getenv("RADARR_URL")
    radarr_key = os.getenv("RADARR_API_KEY")

    if not radarr_url or not radarr_key:
        raise HTTPException(status_code=503, detail="Radarr not configured")

    return RadarrClient(base_url=radarr_url, api_key=radarr_key)


def get_sonarr_client() -> SonarrClient:
    """Dependency injection for SonarrClient."""
    import os

    sonarr_url = os.getenv("SONARR_URL")
    sonarr_key = os.getenv("SONARR_API_KEY")

    if not sonarr_url or not sonarr_key:
        # Sonarr is optional; return None if not configured
        return None

    return SonarrClient(base_url=sonarr_url, api_key=sonarr_key)


# ============================================================================
# Search Handlers
# ============================================================================


async def search_radarr(client: RadarrClient, query: str) -> List[SearchResult]:
    """
    Search Radarr for movies.

    Args:
        client: RadarrClient instance
        query: Search query string

    Returns:
        List of SearchResult objects from Radarr
    """
    try:
        logger.debug(f"Radarr search for: {query}")
        movies = await client.search_movies(query)

        results = []
        for movie in movies:
            poster_url = None
            if "images" in movie and isinstance(movie["images"], list):
                for img in movie["images"]:
                    if img.get("coverType") == "poster" and img.get("url"):
                        poster_url = img["url"]
                        break

            result = SearchResult(
                title=movie.get("title", "Unknown"),
                year=movie.get("year"),
                overview=movie.get("overview"),
                source_service="radarr",
                source_type="movie",
                remote_id=movie.get("id"),
                tmdb_id=movie.get("tmdbId"),
                imdb_id=movie.get("imdbId"),
                poster_url=poster_url,
                status="missing",  # Default; would need to check if in library
                in_library=False,  # Would need to check against library
            )
            results.append(result)

        logger.debug(f"Found {len(results)} movies from Radarr")
        return results
    except Exception as e:
        logger.error(f"Radarr search failed: {str(e)}")
        return []


async def search_sonarr(client: Optional[SonarrClient], query: str) -> List[SearchResult]:
    """
    Search Sonarr for TV shows.

    Args:
        client: SonarrClient instance (can be None if not configured)
        query: Search query string

    Returns:
        List of SearchResult objects from Sonarr
    """
    try:
        if not client:
            logger.debug("Sonarr not configured")
            return []

        logger.debug(f"Sonarr search for: {query}")
        series_list = await client.search_series(query)

        results = []
        for series in series_list:
            poster_url = None
            if "images" in series and isinstance(series["images"], list):
                for img in series["images"]:
                    if img.get("coverType") == "poster" and img.get("url"):
                        poster_url = img["url"]
                        break

            result = SearchResult(
                title=series.get("title", "Unknown"),
                year=series.get("year"),
                overview=series.get("overview"),
                source_service="sonarr",
                source_type="tv",
                remote_id=series.get("id"),
                tmdb_id=series.get("tmdbId"),
                imdb_id=series.get("imdbId"),
                poster_url=poster_url,
                status="missing",  # Default; would need to check if in library
                in_library=False,  # Would need to check against library
            )
            results.append(result)

        logger.debug(f"Found {len(results)} series from Sonarr")
        return results
    except Exception as e:
        logger.error(f"Sonarr search failed: {str(e)}")
        return []


async def search_lidarr(query: str) -> List[SearchResult]:
    """
    Search Lidarr for music.

    Args:
        query: Search query string

    Returns:
        List of SearchResult objects from Lidarr
    """
    try:
        # TODO: Implement Lidarr search when LidarrClient is available
        logger.debug(f"Lidarr search for: {query}")
        results = []
        return results
    except Exception as e:
        logger.error(f"Lidarr search failed: {str(e)}")
        return []


# ============================================================================
# Routes
# ============================================================================


@router.get("/")
async def universal_search(
    q: str = Query(..., min_length=2, description="Search query"),
    radarr: RadarrClient = Depends(get_radarr_client),
    sonarr: Optional[SonarrClient] = Depends(get_sonarr_client),
    limit: int = Query(20, ge=1, le=100, description="Max results per service"),
) -> dict:
    """
    Universal search across all *arr services.

    Simultaneously queries Radarr (movies) and Sonarr (TV shows) for matching content.
    Results are normalized into a unified format and sorted by relevance/year.

    Query Parameters:
    - q (str, required): Search query (minimum 2 characters)
    - limit (int, optional): Maximum results per service (default 20, max 100)

    Returns:
        dict: Aggregated search results grouped by source service
        {
            "query": "matrix",
            "total": 5,
            "results": [
                {
                    "title": "The Matrix",
                    "year": 1999,
                    "source_service": "radarr",
                    "source_type": "movie",
                    ...
                },
                ...
            ],
            "timestamp": "2026-03-09T00:31:00Z"
        }

    Raises:
        HTTPException: If search query is invalid or services are unavailable

    Example:
        GET /api/v1/search?q=matrix&limit=10
    """
    if not q or len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")

    # Execute searches in parallel
    radarr_results, sonarr_results, lidarr_results = await asyncio.gather(
        search_radarr(radarr, q),
        search_sonarr(sonarr, q),
        search_lidarr(q),
        return_exceptions=True,
    )

    # Handle exceptions
    if isinstance(radarr_results, Exception):
        logger.error(f"Radarr search error: {radarr_results}")
        radarr_results = []

    if isinstance(sonarr_results, Exception):
        logger.error(f"Sonarr search error: {sonarr_results}")
        sonarr_results = []

    if isinstance(lidarr_results, Exception):
        logger.error(f"Lidarr search error: {lidarr_results}")
        lidarr_results = []

    # Combine all results
    all_results = (
        radarr_results[:limit] + sonarr_results[:limit] + lidarr_results[:limit]
    )

    # Sort by year (descending, newer first) then by title
    all_results.sort(key=lambda x: (-x.year if x.year else 0, x.title))

    from datetime import datetime, timezone

    return {
        "query": q,
        "total": len(all_results),
        "results": [r.to_dict() for r in all_results],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/movies")
async def search_movies(
    q: str = Query(..., min_length=2, description="Search query"),
    radarr: RadarrClient = Depends(get_radarr_client),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
) -> dict:
    """
    Search Radarr specifically for movies.

    Query Parameters:
    - q (str, required): Search query (minimum 2 characters)
    - limit (int, optional): Maximum results (default 20, max 100)

    Returns:
        dict: Movie search results from Radarr

    Example:
        GET /api/v1/search/movies?q=inception&limit=10
    """
    if not q or len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")

    results = await search_radarr(radarr, q)
    results = results[:limit]

    from datetime import datetime, timezone

    return {
        "query": q,
        "service": "radarr",
        "source_type": "movie",
        "total": len(results),
        "results": [r.to_dict() for r in results],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/tv")
async def search_tv(
    q: str = Query(..., min_length=2, description="Search query"),
    sonarr: Optional[SonarrClient] = Depends(get_sonarr_client),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
) -> dict:
    """
    Search Sonarr specifically for TV shows.

    Query Parameters:
    - q (str, required): Search query (minimum 2 characters)
    - limit (int, optional): Maximum results (default 20, max 100)

    Returns:
        dict: TV show search results from Sonarr

    Example:
        GET /api/v1/search/tv?q=breaking+bad&limit=10
    """
    if not q or len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")

    results = await search_sonarr(sonarr, q)
    results = results[:limit]

    from datetime import datetime, timezone

    return {
        "query": q,
        "service": "sonarr",
        "source_type": "tv",
        "total": len(results),
        "results": [r.to_dict() for r in results],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/music")
async def search_music(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
) -> dict:
    """
    Search Lidarr specifically for music.

    Query Parameters:
    - q (str, required): Search query (minimum 2 characters)
    - limit (int, optional): Maximum results (default 20, max 100)

    Returns:
        dict: Music search results from Lidarr

    Example:
        GET /api/v1/search/music?q=pink+floyd&limit=10
    """
    if not q or len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")

    results = await search_lidarr(q)
    results = results[:limit]

    from datetime import datetime, timezone

    return {
        "query": q,
        "service": "lidarr",
        "source_type": "music",
        "total": len(results),
        "results": [r.to_dict() for r in results],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
