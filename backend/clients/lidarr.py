"""
Lidarr API client for music library management.

Provides asynchronous methods for interacting with Lidarr v1 API endpoints,
including system status, artist library management, and search/command operations.
"""

from typing import Any, Optional, List

from backend.schemas import (
    DiskSpace,
    LidarrArtist,
    LidarrCommand,
    LidarrSystemStatus,
)

from .base import BaseArrClient


class LidarrClient(BaseArrClient):
    """
    Asynchronous client for Lidarr API v1.

    Handles all interactions with Lidarr, including system health checks,
    artist library queries, and command execution (search, refresh, etc.).

    Inherits from BaseArrClient and maintains the same async/error handling patterns.
    """

    async def get_status(self) -> LidarrSystemStatus:
        """
        Fetch Lidarr system status and version information.

        Returns:
            LidarrSystemStatus: System status response from Lidarr

        Raises:
            HTTPException: If the request fails or Lidarr returns an error
        """
        response = await self.get("/api/v1/system/status")
        return LidarrSystemStatus(**response.json())

    async def get_artists(
        self,
        artist_id: Optional[int] = None,
    ) -> LidarrArtist | list[LidarrArtist]:
        """
        Fetch artists from the Lidarr library.

        Args:
            artist_id (int, optional): If provided, fetch only this specific artist.
                                      If None, return the entire library.

        Returns:
            LidarrArtist or list[LidarrArtist]: Artist(s) from Lidarr

        Raises:
            HTTPException: If the request fails or artist_id doesn't exist
        """
        if artist_id is not None:
            response = await self.get(f"/api/v1/artist/{artist_id}")
            return LidarrArtist(**response.json())
        else:
            response = await self.get("/api/v1/artist")
            data = response.json()
            return [LidarrArtist(**item) for item in data]

    async def search_artists(self, query: str) -> list[LidarrArtist]:
        """
        Search for music artists using MusicBrainz lookup.

        Args:
            query (str): Search query (artist name)

        Returns:
            list[LidarrArtist]: List of matching artists from MusicBrainz

        Raises:
            HTTPException: If the request fails
        """
        params = {"term": query}
        response = await self.get("/api/v1/artist/lookup", params=params)
        data = response.json()
        return [LidarrArtist(**item) for item in data]

    async def command_search(self, artist_ids: list[int]) -> LidarrCommand:
        """
        Trigger a search for missing albums.

        Args:
            artist_ids (list[int]): List of Lidarr artist IDs to search for

        Returns:
            LidarrCommand: Command response from Lidarr

        Raises:
            HTTPException: If the request fails
            ValueError: If artist_ids is empty
        """
        if not artist_ids:
            raise ValueError("artist_ids cannot be empty")

        payload = {
            "name": "ArtistSearch",
            "artistIds": artist_ids,
        }

        response = await self.post("/api/v1/command", data=payload)
        return LidarrCommand(**response.json())

    async def add_artist(
        self,
        foreign_artist_id: str,
        artist_name: str,
        quality_profile_id: int,
        root_folder_path: str,
        monitored: bool = True,
    ) -> LidarrArtist:
        """
        Add a new artist to the Lidarr library.

        Args:
            foreign_artist_id (str): The MusicBrainz ID of the artist to add
            artist_name (str): Artist name
            quality_profile_id (int): Lidarr quality profile ID
            root_folder_path (str): Root folder path for the artist
            monitored (bool): Whether to monitor this artist

        Returns:
            LidarrArtist: Created artist object with ID and metadata

        Raises:
            HTTPException: If the request fails or artist already exists
        """
        payload = {
            "foreignArtistId": foreign_artist_id,
            "artistName": artist_name,
            "qualityProfileId": quality_profile_id,
            "rootFolderPath": root_folder_path,
            "monitored": monitored,
        }

        response = await self.post("/api/v1/artist", data=payload)
        return LidarrArtist(**response.json())

    async def delete_artist(
        self,
        artist_id: int,
        delete_files: bool = False,
    ) -> None:
        """
        Remove an artist from the Lidarr library.

        Args:
            artist_id (int): Lidarr artist ID to delete
            delete_files (bool): If True, also delete the downloaded files

        Raises:
            HTTPException: If the request fails or artist not found
        """
        params = {"deleteFiles": str(delete_files).lower()}
        await self.delete(f"/api/v1/artist/{artist_id}", params=params)

    async def get_disk_space(self) -> List[DiskSpace]:
        """Fetch disk space information from Lidarr."""
        response = await self.get("/api/v1/diskspace")
        data = response.json()
        return [DiskSpace(**item) for item in data]
