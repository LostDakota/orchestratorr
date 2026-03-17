"""
Sonarr API client for TV series library management.

Provides asynchronous methods for interacting with Sonarr v3 API endpoints,
including system status, series library management, and search operations.
"""

from typing import Any, Optional, List

from backend.schemas import (
    DiskSpace,
    SonarrCalendarEvent,
    SonarrCommand,
    SonarrSeries,
    SonarrSystemStatus,
)

from .base import BaseArrClient


class SonarrClient(BaseArrClient):
    """
    Asynchronous client for Sonarr API v3.

    Handles all interactions with Sonarr, including system health checks,
    series library queries, and command execution.

    Inherits from BaseArrClient and maintains the same async/error handling patterns.
    """

    async def get_status(self) -> SonarrSystemStatus:
        """
        Fetch Sonarr system status and version information.

        Returns:
            SonarrSystemStatus: System status response from Sonarr

        Raises:
            HTTPException: If the request fails or Sonarr returns an error
        """
        response = await self.get("/api/v3/system/status")
        return SonarrSystemStatus(**response.json())

    async def get_series(
        self,
        series_id: Optional[int] = None,
    ) -> SonarrSeries | list[SonarrSeries]:
        """
        Fetch series from the Sonarr library.

        Args:
            series_id (int, optional): If provided, fetch only this specific series.
                                      If None, return the entire library.

        Returns:
            SonarrSeries or list[SonarrSeries]: Series from Sonarr

        Raises:
            HTTPException: If the request fails or series_id doesn't exist
        """
        if series_id is not None:
            response = await self.get(f"/api/v3/series/{series_id}")
            return SonarrSeries(**response.json())
        else:
            response = await self.get("/api/v3/series")
            data = response.json()
            return [SonarrSeries(**item) for item in data]

    async def search_series(self, query: str) -> list[SonarrSeries]:
        """
        Search for TV series using TVDB/TMDB lookup.

        Args:
            query (str): Search query (series title)

        Returns:
            list[SonarrSeries]: List of matching series from TVDB/TMDB

        Raises:
            HTTPException: If the request fails
        """
        params = {"term": query}
        response = await self.get("/api/v3/series/lookup", params=params)
        data = response.json()
        return [SonarrSeries(**item) for item in data]

    async def command_search(self, series_ids: list[int]) -> SonarrCommand:
        """
        Trigger a search for missing episodes.

        Args:
            series_ids (list[int]): List of Sonarr series IDs to search for

        Returns:
            SonarrCommand: Command response from Sonarr

        Raises:
            HTTPException: If the request fails
            ValueError: If series_ids is empty
        """
        if not series_ids:
            raise ValueError("series_ids cannot be empty")

        payload = {
            "name": "SeriesSearch",
            "seriesIds": series_ids,
        }

        response = await self.post("/api/v3/command", data=payload)
        return SonarrCommand(**response.json())

    async def add_series(
        self,
        tvdb_id: int,
        title: str,
        quality_profile_id: int,
        root_folder_path: str,
        monitored: bool = True,
    ) -> SonarrSeries:
        """
        Add a new series to the Sonarr library.

        Args:
            tvdb_id (int): The TVDB ID of the series to add
            title (str): Series title
            quality_profile_id (int): Sonarr quality profile ID
            root_folder_path (str): Root folder path for the series
            monitored (bool): Whether to monitor this series

        Returns:
            SonarrSeries: Created series object with ID and metadata

        Raises:
            HTTPException: If the request fails or series already exists
        """
        payload = {
            "tvdbId": tvdb_id,
            "title": title,
            "qualityProfileId": quality_profile_id,
            "rootFolderPath": root_folder_path,
            "monitored": monitored,
        }

        response = await self.post("/api/v3/series", data=payload)
        return SonarrSeries(**response.json())

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
        """
        params = {"deleteFiles": str(delete_files).lower()}
        await self.delete(f"/api/v3/series/{series_id}", params=params)

    async def get_disk_space(self) -> List[DiskSpace]:
        """Fetch disk space information from Sonarr."""
        response = await self.get("/api/v3/diskspace")
        data = response.json()
        return [DiskSpace(**item) for item in data]

    async def get_calendar(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[SonarrCalendarEvent]:
        """
        Fetch upcoming episodes from the calendar.

        Args:
            start_date (str, optional): Start date (ISO 8601 format: YYYY-MM-DD)
            end_date (str, optional): End date (ISO 8601 format: YYYY-MM-DD)

        Returns:
            list[SonarrCalendarEvent]: Calendar events

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
        return [SonarrCalendarEvent(**item) for item in data]
