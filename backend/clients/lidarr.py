"""
Lidarr API client for music library management.

Provides asynchronous methods for interacting with Lidarr v1 API endpoints,
including system status, artist library management, and search/command operations.
"""

from typing import Any, Optional

import httpx

from .base import BaseArrClient


class LidarrClient(BaseArrClient):
    """
    Asynchronous client for Lidarr API v1.

    Handles all interactions with Lidarr, including system health checks,
    artist library queries, and command execution (search, refresh, etc.).

    Inherits from BaseArrClient and maintains the same async/error handling patterns.
    """

    async def get_status(self) -> dict[str, Any]:
        """
        Fetch Lidarr system status and version information.

        Returns:
            dict: System status response from Lidarr, including:
                - version: Lidarr version string
                - osVersion: Operating system information
                - authentication: Authentication mode
                - branch: Git branch

        Raises:
            HTTPException: If the request fails or Lidarr returns an error

        Example:
            status = await client.get_status()
            print(f"Lidarr v{status['version']}")
        """
        response = await self.get("/api/v1/system/status")
        return response.json()

    async def get_artists(
        self,
        artist_id: Optional[int] = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """
        Fetch artists from the Lidarr library.

        Retrieves either the full artist collection or a specific artist by ID.

        Args:
            artist_id (int, optional): If provided, fetch only this specific artist.
                                      If None, return the entire library.

        Returns:
            dict or list: If artist_id is provided, returns a single artist object.
                         Otherwise returns a list of artist objects.
                         Each artist includes:
                         - id: Lidarr internal artist ID
                         - artistName: Artist name
                         - foreignArtistId: MusicBrainz ID
                         - monitored: Whether the artist is monitored
                         - status: Current status (Continuing, Ended, etc.)

        Raises:
            HTTPException: If the request fails or artist_id doesn't exist

        Example:
            # Get entire library
            artists = await client.get_artists()
            print(f"Found {len(artists)} artists")

            # Get specific artist
            artist = await client.get_artists(artist_id=123)
            print(f"Artist: {artist['artistName']}")
        """
        if artist_id is not None:
            response = await self.get(f"/api/v1/artist/{artist_id}")
            return response.json()
        else:
            response = await self.get("/api/v1/artist")
            return response.json()

    async def search_artists(self, query: str) -> list[dict[str, Any]]:
        """
        Search for music artists using MusicBrainz lookup.

        Uses the /api/v1/artist/lookup endpoint to search for artists by name.

        Args:
            query (str): Search query (artist name)

        Returns:
            list: List of matching artists from MusicBrainz, including:
                - artistName: Artist name
                - foreignArtistId: MusicBrainz ID
                - overview: Biography summary
                - images: Artist image URLs
                - status: Current status (Active, Disbanded, etc.)

        Raises:
            HTTPException: If the request fails

        Example:
            results = await client.search_artists("Radiohead")
            for artist in results:
                print(f"{artist['artistName']}")
        """
        params = {"term": query}
        response = await self.get("/api/v1/artist/lookup", params=params)
        return response.json()

    async def command_search(self, artist_ids: list[int]) -> dict[str, Any]:
        """
        Trigger a search for missing albums.

        Args:
            artist_ids (list[int]): List of Lidarr artist IDs to search for

        Returns:
            dict: Command response from Lidarr with command ID and status

        Raises:
            HTTPException: If the request fails

        Example:
            result = await client.command_search([123, 456])
            print(f"Search queued with command ID: {result['id']}")
        """
        if not artist_ids:
            raise ValueError("artist_ids cannot be empty")

        payload = {
            "name": "ArtistSearch",
            "artistIds": artist_ids,
        }

        response = await self.post("/api/v1/command", data=payload)
        return response.json()

    async def add_artist(
        self,
        foreign_artist_id: str,
        artist_name: str,
        quality_profile_id: int,
        root_folder_path: str,
        monitored: bool = True,
    ) -> dict[str, Any]:
        """
        Add a new artist to the Lidarr library.

        Args:
            foreign_artist_id (str): The MusicBrainz ID of the artist to add
            artist_name (str): Artist name
            quality_profile_id (int): Lidarr quality profile ID
            root_folder_path (str): Root folder path for the artist
            monitored (bool): Whether to monitor this artist

        Returns:
            dict: Created artist object with ID and metadata

        Raises:
            HTTPException: If the request fails or artist already exists

        Example:
            artist = await client.add_artist(
                foreign_artist_id="uuid",
                artist_name="Radiohead",
                quality_profile_id=1,
                root_folder_path="/music"
            )
            print(f"Added artist with Lidarr ID: {artist['id']}")
        """
        payload = {
            "foreignArtistId": foreign_artist_id,
            "artistName": artist_name,
            "qualityProfileId": quality_profile_id,
            "rootFolderPath": root_folder_path,
            "monitored": monitored,
        }

        response = await self.post("/api/v1/artist", data=payload)
        return response.json()

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

        Example:
            await client.delete_artist(123, delete_files=True)
        """
        params = {"deleteFiles": str(delete_files).lower()}
        await self.delete(f"/api/v1/artist/{artist_id}", params=params)