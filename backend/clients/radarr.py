"""
Radarr API client for movie library management.

Provides asynchronous methods for interacting with Radarr v3 API endpoints,
including system status, movie library management, and search/command operations.
"""

from typing import Any, Optional

import httpx

from .base import BaseArrClient


class RadarrClient(BaseArrClient):
    """
    Asynchronous client for Radarr API v3.

    Handles all interactions with Radarr, including system health checks,
    movie library queries, and command execution (search, refresh, etc.).

    Inherits from BaseArrClient and maintains the same async/error handling patterns.
    """

    async def get_status(self) -> dict[str, Any]:
        """
        Fetch Radarr system status and version information.

        This endpoint is used to verify connectivity and retrieve basic
        system metadata for display in the UI (version, OS, etc.).

        Returns:
            dict: System status response from Radarr, including:
                - version: Radarr version string
                - osVersion: Operating system information
                - isLinux, isWindows, isOsx: Boolean OS indicators
                - isDocker: Whether running in Docker
                - authentication: Authentication mode
                - branch: Git branch (usually 'master' or 'develop')

        Raises:
            HTTPException: If the request fails or Radarr returns an error

        Example:
            status = await client.get_status()
            print(f"Radarr v{status['version']}")
        """
        response = await self.get("/api/v3/system/status")
        return response.json()

    async def get_movies(
        self,
        movie_id: Optional[int] = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """
        Fetch movies from the Radarr library.

        Retrieves either the full movie collection or a specific movie by ID.
        Results include metadata like title, year, ratings, and monitored status.

        Args:
            movie_id (int, optional): If provided, fetch only this specific movie.
                                     If None, return the entire library.

        Returns:
            dict or list: If movie_id is provided, returns a single movie object.
                         Otherwise returns a list of movie objects.
                         Each movie includes:
                         - id: Radarr internal movie ID
                         - title: Movie title
                         - year: Release year
                         - tmdbId: TMDB database ID
                         - monitored: Whether the movie is monitored for updates
                         - status: Current status (Missing, Downloaded, Announced, etc.)
                         - ratings: Audience and critic ratings
                         - images: Poster and fanart URLs

        Raises:
            HTTPException: If the request fails or movie_id doesn't exist

        Example:
            # Get entire library
            movies = await client.get_movies()
            print(f"Found {len(movies)} movies")

            # Get specific movie
            movie = await client.get_movies(movie_id=123)
            print(f"Movie: {movie['title']} ({movie['year']})")
        """
        if movie_id is not None:
            response = await self.get(f"/api/v3/movie/{movie_id}")
            return response.json()
        else:
            response = await self.get("/api/v3/movie")
            return response.json()

    async def command_search(self, movie_ids: list[int]) -> dict[str, Any]:
        """
        Trigger a search for missing movies.

        Executes the MoviesSearch command on Radarr to initiate a search
        for missing movies in the specified list. This is typically used
        when a user manually triggers a search from the UI.

        Args:
            movie_ids (list[int]): List of Radarr movie IDs to search for

        Returns:
            dict: Command response from Radarr, including:
                - id: Command ID (can be used to track progress)
                - name: Command name ("MoviesSearch")
                - status: Initial status (usually 'pending' or 'queued')
                - queued: Timestamp when queued
                - duration: Estimated duration (ms)

        Raises:
            HTTPException: If the request fails or movie_ids are invalid

        Example:
            result = await client.command_search([123, 456])
            print(f"Search queued with command ID: {result['id']}")
        """
        if not movie_ids:
            raise ValueError("movie_ids cannot be empty")

        payload = {
            "name": "MoviesSearch",
            "movieIds": movie_ids,
        }

        response = await self.post("/api/v3/command", data=payload)
        return response.json()

    async def command_refresh(self, movie_id: Optional[int] = None) -> dict[str, Any]:
        """
        Refresh movie information from metadata sources.

        Triggers Radarr to refresh metadata for one or all movies from TMDB,
        IMDb, and other configured sources. Useful for updating ratings,
        descriptions, and other metadata.

        Args:
            movie_id (int, optional): Refresh specific movie. If None, refresh all.

        Returns:
            dict: Command response with command ID and status

        Raises:
            HTTPException: If the request fails

        Example:
            result = await client.command_refresh()  # Refresh all
            print(f"Refresh command queued: {result['id']}")
        """
        payload = {"name": "RefreshMovie"}
        if movie_id is not None:
            payload["movieIds"] = [movie_id]

        response = await self.post("/api/v3/command", data=payload)
        return response.json()

    async def get_calendar(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Fetch upcoming movie releases from the calendar.

        Returns a list of movies scheduled for release within the specified
        date range. Useful for displaying upcoming releases in a calendar view.

        Args:
            start_date (str, optional): Start date (ISO 8601 format: YYYY-MM-DD)
            end_date (str, optional): End date (ISO 8601 format: YYYY-MM-DD)

        Returns:
            list: Calendar events, each including:
                - id: Movie ID
                - title: Movie title
                - inCinemas: Release date in theaters
                - physicalRelease: Physical media release date
                - monitored: Whether monitored

        Raises:
            HTTPException: If the request fails

        Example:
            calendar = await client.get_calendar(
                start_date="2026-03-01",
                end_date="2026-03-31"
            )
            for event in calendar:
                print(f"{event['title']} releases {event['inCinemas']}")
        """
        params = {}
        if start_date:
            params["start"] = start_date
        if end_date:
            params["end"] = end_date

        response = await self.get("/api/v3/calendar", params=params)
        return response.json()

    async def add_movie(
        self,
        tmdb_id: int,
        title: str,
        quality_profile_id: int,
        root_folder_path: str,
        monitored: bool = True,
    ) -> dict[str, Any]:
        """
        Add a new movie to the Radarr library.

        Creates a new movie entry in Radarr and begins monitoring/searching
        based on the configured quality and root folder.

        Args:
            tmdb_id (int): The TMDB ID of the movie to add
            title (str): Movie title (for reference)
            quality_profile_id (int): Radarr quality profile ID
            root_folder_path (str): Root folder path for the movie
            monitored (bool): Whether to monitor and search for this movie

        Returns:
            dict: Created movie object with ID and metadata

        Raises:
            HTTPException: If the request fails or movie already exists

        Example:
            movie = await client.add_movie(
                tmdb_id=550,
                title="Fight Club",
                quality_profile_id=1,
                root_folder_path="/movies"
            )
            print(f"Added movie with Radarr ID: {movie['id']}")
        """
        payload = {
            "tmdbId": tmdb_id,
            "title": title,
            "qualityProfileId": quality_profile_id,
            "rootFolderPath": root_folder_path,
            "monitored": monitored,
        }

        response = await self.post("/api/v3/movie", data=payload)
        return response.json()

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

        Example:
            await client.delete_movie(123, delete_files=True)
        """
        params = {"deleteFiles": str(delete_files).lower()}
        await self.delete(f"/api/v3/movie/{movie_id}", params=params)
