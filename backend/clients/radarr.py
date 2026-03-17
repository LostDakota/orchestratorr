"""
Radarr API client for movie library management.

Provides asynchronous methods for interacting with Radarr v3 API endpoints,
including system status, movie library management, and search/command operations.
"""

from typing import Any, Optional, List

from backend.schemas import (
    DiskSpace,
    RadarrCalendarEvent,
    RadarrCommand,
    RadarrMovie,
    RadarrSystemStatus,
)

from .base import BaseArrClient


class RadarrClient(BaseArrClient):
    """
    Asynchronous client for Radarr API v3.

    Handles all interactions with Radarr, including system health checks,
    movie library queries, and command execution (search, refresh, etc.).

    Inherits from BaseArrClient and maintains the same async/error handling patterns.
    """

    async def get_status(self) -> RadarrSystemStatus:
        """
        Fetch Radarr system status and version information.

        Returns:
            RadarrSystemStatus: System status response from Radarr

        Raises:
            HTTPException: If the request fails or Radarr returns an error
        """
        response = await self.get("/api/v3/system/status")
        return RadarrSystemStatus(**response.json())

    async def get_movies(
        self,
        movie_id: Optional[int] = None,
    ) -> RadarrMovie | list[RadarrMovie]:
        """
        Fetch movies from the Radarr library.

        Args:
            movie_id (int, optional): If provided, fetch only this specific movie.
                                     If None, return the entire library.

        Returns:
            RadarrMovie or list[RadarrMovie]: Movie(s) from Radarr

        Raises:
            HTTPException: If the request fails or movie_id doesn't exist
        """
        if movie_id is not None:
            response = await self.get(f"/api/v3/movie/{movie_id}")
            return RadarrMovie(**response.json())
        else:
            response = await self.get("/api/v3/movie")
            data = response.json()
            return [RadarrMovie(**item) for item in data]

    async def command_search(self, movie_ids: list[int]) -> RadarrCommand:
        """
        Trigger a search for missing movies.

        Args:
            movie_ids (list[int]): List of Radarr movie IDs to search for

        Returns:
            RadarrCommand: Command response from Radarr

        Raises:
            HTTPException: If the request fails or movie_ids are invalid
            ValueError: If movie_ids is empty
        """
        if not movie_ids:
            raise ValueError("movie_ids cannot be empty")

        payload = {
            "name": "MoviesSearch",
            "movieIds": movie_ids,
        }

        response = await self.post("/api/v3/command", data=payload)
        return RadarrCommand(**response.json())

    async def command_refresh(self, movie_id: Optional[int] = None) -> RadarrCommand:
        """
        Refresh movie information from metadata sources.

        Args:
            movie_id (int, optional): Refresh specific movie. If None, refresh all.

        Returns:
            RadarrCommand: Command response with command ID and status

        Raises:
            HTTPException: If the request fails
        """
        payload = {"name": "RefreshMovie"}
        if movie_id is not None:
            payload["movieIds"] = [movie_id]

        response = await self.post("/api/v3/command", data=payload)
        return RadarrCommand(**response.json())

    async def get_calendar(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[RadarrCalendarEvent]:
        """
        Fetch upcoming movie releases from the calendar.

        Args:
            start_date (str, optional): Start date (ISO 8601 format: YYYY-MM-DD)
            end_date (str, optional): End date (ISO 8601 format: YYYY-MM-DD)

        Returns:
            list[RadarrCalendarEvent]: Calendar events

        Raises:
            HTTPException: If the request fails
        """
        params = {}
        if start_date:
            params["start"] = start_date
        if end_date:
            params["end"] = end_date

        response = await self.get("/api/v3/calendar", params=params)
        data = response.json()
        return [RadarrCalendarEvent(**item) for item in data]

    async def add_movie(
        self,
        tmdb_id: int,
        title: str,
        quality_profile_id: int,
        root_folder_path: str,
        monitored: bool = True,
    ) -> RadarrMovie:
        """
        Add a new movie to the Radarr library.

        Args:
            tmdb_id (int): The TMDB ID of the movie to add
            title (str): Movie title (for reference)
            quality_profile_id (int): Radarr quality profile ID
            root_folder_path (str): Root folder path for the movie
            monitored (bool): Whether to monitor and search for this movie

        Returns:
            RadarrMovie: Created movie object with ID and metadata

        Raises:
            HTTPException: If the request fails or movie already exists
        """
        payload = {
            "tmdbId": tmdb_id,
            "title": title,
            "qualityProfileId": quality_profile_id,
            "rootFolderPath": root_folder_path,
            "monitored": monitored,
        }

        response = await self.post("/api/v3/movie", data=payload)
        return RadarrMovie(**response.json())

    async def delete_movie(
        self,
        movie_id: int,
        delete_files: bool = False,
    ) -> None:
        """
        Remove a movie from the Radarr library.

        Args:
            movie_id (int): Radarr movie ID to delete
            delete_files (bool): If True, also delete the downloaded files

        Raises:
            HTTPException: If the request fails or movie not found
        """
        params = {"deleteFiles": str(delete_files).lower()}
        await self.delete(f"/api/v3/movie/{movie_id}", params=params)

    async def search_movies(self, query: str) -> list[RadarrMovie]:
        """
        Search for movies using TMDB lookup.

        Args:
            query (str): Search query (movie title)

        Returns:
            list[RadarrMovie]: List of matching movies from TMDB

        Raises:
            HTTPException: If the request fails
        """
        params = {"term": query}
        response = await self.get("/api/v3/movie/lookup", params=params)
        data = response.json()
        return [RadarrMovie(**item) for item in data]

    async def snatched(self, movie_id: int) -> RadarrMovie:
        """Check if a movie has been snatched/downloaded."""
        response = await self.get(f"/api/v3/movie/{movie_id}")
        return RadarrMovie(**response.json())

    async def get_disk_space(self) -> List[DiskSpace]:
        """Fetch disk space information from Radarr."""
        response = await self.get("/api/v3/diskspace")
        data = response.json()
        return [DiskSpace(**item) for item in data]
