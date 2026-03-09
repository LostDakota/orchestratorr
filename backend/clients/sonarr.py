"""
Sonarr API client for TV series library management.

Provides asynchronous methods for interacting with Sonarr v3 API endpoints,
including system status, series library management, and search operations.
"""

from typing import Any, Optional

import httpx

from .base import BaseArrClient


class SonarrClient(BaseArrClient):
    """
    Asynchronous client for Sonarr API v3.

    Handles all interactions with Sonarr, including system health checks,
    series library queries, and command execution.

    Inherits from BaseArrClient and maintains the same async/error handling patterns.
    """

    async def get_status(self) -> dict[str, Any]:
        """
        Fetch Sonarr system status and version information.

        Returns:
            dict: System status response from Sonarr, including:
                - version: Sonarr version string
                - osVersion: Operating system information
                - authentication: Authentication mode
                - branch: Git branch

        Raises:
            HTTPException: If the request fails or Sonarr returns an error

        Example:
            status = await client.get_status()
            print(f"Sonarr v{status['version']}")
        """
        response = await self.get("/api/v3/system/status")
        return response.json()

    async def get_series(
        self,
        series_id: Optional[int] = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """
        Fetch series from the Sonarr library.

        Retrieves either the full series collection or a specific series by ID.

        Args:
            series_id (int, optional): If provided, fetch only this specific series.
                                      If None, return the entire library.

        Returns:
            dict or list: If series_id is provided, returns a single series object.
                         Otherwise returns a list of series objects.
                         Each series includes:
                         - id: Sonarr internal series ID
                         - title: Series title
                         - tvdbId: TVDB database ID
                         - status: Current status (Continuing, Ended, etc.)
                         - monitored: Whether the series is monitored

        Raises:
            HTTPException: If the request fails or series_id doesn't exist

        Example:
            # Get entire library
            series = await client.get_series()
            print(f"Found {len(series)} series")

            # Get specific series
            show = await client.get_series(series_id=123)
            print(f"Series: {show['title']}")
        """
        if series_id is not None:
            response = await self.get(f"/api/v3/series/{series_id}")
            return response.json()
        else:
            response = await self.get("/api/v3/series")
            return response.json()

    async def search_series(self, query: str) -> list[dict[str, Any]]:
        """
        Search for TV series using TVDB/TMDB lookup.

        Uses the /api/v3/series/lookup endpoint to search for series by title.

        Args:
            query (str): Search query (series title)

        Returns:
            list: List of matching series from TVDB/TMDB, including:
                - title: Series title
                - tvdbId: TVDB database ID
                - tmdbId: TMDB database ID
                - overview: Plot summary
                - images: Poster URLs
                - status: Current status (Continuing, Ended, etc.)

        Raises:
            HTTPException: If the request fails

        Example:
            results = await client.search_series("Breaking Bad")
            for series in results:
                print(f"{series['title']}")
        """
        params = {"term": query}
        response = await self.get("/api/v3/series/lookup", params=params)
        return response.json()

    async def command_search(self, series_ids: list[int]) -> dict[str, Any]:
        """
        Trigger a search for missing episodes.

        Args:
            series_ids (list[int]): List of Sonarr series IDs to search for

        Returns:
            dict: Command response from Sonarr with command ID and status

        Raises:
            HTTPException: If the request fails

        Example:
            result = await client.command_search([123, 456])
            print(f"Search queued with command ID: {result['id']}")
        """
        if not series_ids:
            raise ValueError("series_ids cannot be empty")

        payload = {
            "name": "SeriesSearch",
            "seriesIds": series_ids,
        }

        response = await self.post("/api/v3/command", data=payload)
        return response.json()

    async def add_series(
        self,
        tvdb_id: int,
        title: str,
        quality_profile_id: int,
        root_folder_path: str,
        monitored: bool = True,
    ) -> dict[str, Any]:
        """
        Add a new series to the Sonarr library.

        Args:
            tvdb_id (int): The TVDB ID of the series to add
            title (str): Series title
            quality_profile_id (int): Sonarr quality profile ID
            root_folder_path (str): Root folder path for the series
            monitored (bool): Whether to monitor this series

        Returns:
            dict: Created series object with ID and metadata

        Raises:
            HTTPException: If the request fails or series already exists

        Example:
            series = await client.add_series(
                tvdb_id=81189,
                title="Breaking Bad",
                quality_profile_id=1,
                root_folder_path="/tv"
            )
            print(f"Added series with Sonarr ID: {series['id']}")
        """
        payload = {
            "tvdbId": tvdb_id,
            "title": title,
            "qualityProfileId": quality_profile_id,
            "rootFolderPath": root_folder_path,
            "monitored": monitored,
        }

        response = await self.post("/api/v3/series", data=payload)
        return response.json()

    async def delete_series(
        self,
        series_id: int,
        delete_files: bool = False,
    ) -> None:
        """
        Remove a series from the Sonarr library.

        Args:
            series_id (int): Sonarr series ID to delete
            delete_files (bool): If True, also delete the downloaded files

        Raises:
            HTTPException: If the request fails or series not found

        Example:
            await client.delete_series(123, delete_files=True)
        """
        params = {"deleteFiles": str(delete_files).lower()}
        await self.delete(f"/api/v3/series/{series_id}", params=params)
