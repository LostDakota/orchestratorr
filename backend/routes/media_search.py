"""
Media Search and Addition Route

Provides a centralized API for searching media across different services
and preparing for addition to respective libraries.
"""

from fastapi import APIRouter, HTTPException, Query
import httpx
from typing import Optional

from backend.config import settings
from backend.routes import proxy

search_router = APIRouter(prefix="/api/v1/media", tags=["media_search"])

class MediaSearchClient:
    """
    Centralized media search client that can query multiple sources
    """
    
    @staticmethod
    async def search_tmdb_movies(query: str, page: int = 1) -> dict:
        """
        Search movies on TMDB
        
        Args:
            query (str): Search term
            page (int, optional): Page number. Defaults to 1.
        
        Returns:
            dict: Search results with movie details
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.themoviedb.org/3/search/movie",
                params={
                    "api_key": settings.tmdb_api_key,
                    "query": query,
                    "page": page,
                    "language": "en-US"
                }
            )
            response.raise_for_status()
            return response.json()

@search_router.get("/search")
async def unified_media_search(
    query: str = Query(..., min_length=2, max_length=100, description="Search query"),
    media_type: Optional[str] = Query(None, description="Type of media (movie, tv, music)"),
    page: int = Query(1, ge=1, description="Page number for results")
) -> dict:
    """
    Unified media search across multiple sources
    
    Supports searching:
    - Movies via TMDB
    
    Query Parameters:
    - query: Search term
    - media_type: Optional filter for media type
    - page: Result page number
    
    Returns:
        Unified search results with standardized format
    """
    try:
        if media_type is None or media_type == "movie":
            tmdb_results = await MediaSearchClient.search_tmdb_movies(query, page)
            return {
                "media_type": "movie",
                "total_pages": tmdb_results.get("total_pages", 0),
                "total_results": tmdb_results.get("total_results", 0),
                "results": [
                    {
                        "id": result.get("id"),
                        "title": result.get("title"),
                        "overview": result.get("overview"),
                        "poster_path": f"https://image.tmdb.org/t/p/w500{result.get('poster_path')}" if result.get('poster_path') else None,
                        "release_date": result.get("release_date"),
                        "vote_average": result.get("vote_average")
                    } for result in tmdb_results.get("results", [])
                ]
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid media type")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@search_router.post("/add")
async def add_media_to_library(
    media_type: str = Query(..., description="Type of media (movie, tv, music)"),
    external_id: int = Query(..., description="External service ID (TMDB, TVDB, etc)"),
    title: str = Query(..., description="Media title"),
    root_folder: Optional[str] = Query(None, description="Root folder for media"),
    quality_profile_id: Optional[int] = Query(None, description="Quality profile ID")
) -> dict:
    """
    Add media to appropriate library based on media type
    
    Supports adding:
    - Movies to Radarr
    
    Query Parameters:
    - media_type: Type of media
    - external_id: ID from external service (TMDB)
    - title: Media title
    - root_folder: Optional root folder path
    - quality_profile_id: Optional quality profile
    
    Returns:
        Result of media addition
    """
    try:
        if media_type == "movie":
            # Default quality profile and root folder if not provided
            root_folder = root_folder or "/movies"
            quality_profile_id = quality_profile_id or 1
            
            return await proxy.radarr_add_movie(
                tmdb_id=external_id,
                title=title,
                quality_profile_id=quality_profile_id,
                root_folder_path=root_folder
            )
        
        else:
            raise HTTPException(status_code=400, detail="Invalid media type")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add media: {str(e)}")