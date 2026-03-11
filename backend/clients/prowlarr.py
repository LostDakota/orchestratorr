"""
Prowlarr API client for indexer management.

Provides asynchronous methods for interacting with Prowlarr v1 API endpoints,
including system status and indexer management.
"""

from typing import Any, Optional

import httpx

from .base import BaseArrClient


class ProwlarrClient(BaseArrClient):
    """
    Asynchronous client for Prowlarr API v1.

    Handles all interactions with Prowlarr, including system health checks,
    indexer queries, and search operations.

    Inherits from BaseArrClient and maintains the same async/error handling patterns.
    """

    async def get_status(self) -> dict[str, Any]:
        """
        Fetch Prowlarr system status and version information.

        Returns:
            dict: System status response from Prowlarr, including:
                - version: Prowlarr version string
                - appName: Application name ("Prowlarr")
                - branch: Git branch
                - isDocker: Whether running in Docker
                - authentication: Authentication mode

        Raises:
            HTTPException: If the request fails or Prowlarr returns an error

        Example:
            status = await client.get_status()
            print(f"Prowlarr v{status['version']}")
        """
        response = await self.get("/api/v1/system/status")
        return response.json()

    async def get_indexers(
        self,
        indexer_id: Optional[int] = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """
        Fetch indexers from Prowlarr.

        Retrieves either the full indexer list or a specific indexer by ID.

        Args:
            indexer_id (int, optional): If provided, fetch only this specific indexer.
                                       If None, return the entire list.

        Returns:
            dict or list: If indexer_id is provided, returns a single indexer object.
                         Otherwise returns a list of indexer objects.
                         Each indexer includes:
                         - id: Prowlarr internal indexer ID
                         - name: Indexer name
                         - protocol: Protocol (torrent, usenet)
                         - enabled: Whether indexer is enabled
                         - fields: Configuration fields

        Raises:
            HTTPException: If the request fails or indexer_id doesn't exist

        Example:
            # Get all indexers
            indexers = await client.get_indexers()
            print(f"Found {len(indexers)} indexers")

            # Get specific indexer
            indexer = await client.get_indexers(indexer_id=123)
            print(f"Indexer: {indexer['name']}")
        """
        if indexer_id is not None:
            response = await self.get(f"/api/v1/indexer/{indexer_id}")
            return response.json()
        else:
            response = await self.get("/api/v1/indexer")
            return response.json()

    async def search(
        self,
        query: str,
        categories: Optional[list[int]] = None,
        type: str = "search",
    ) -> list[dict[str, Any]]:
        """
        Search across all configured indexers.

        Uses the /api/v1/search endpoint to query indexers for content.

        Args:
            query (str): Search query string
            categories (list[int], optional): Category IDs to filter by
            type (str): Search type ("search", "tv-search", "movie-search", "music-search")

        Returns:
            list: Search results from indexers, including:
                - guid: Unique identifier
                - title: Result title
                - size: File size in bytes
                - indexer: Source indexer name
                - categories: List of category IDs

        Raises:
            HTTPException: If the request fails

        Example:
            results = await client.search("Ubuntu", categories=[2000])
            for result in results:
                print(f"{result['title']} ({result['indexer']})")
        """
        params = {"query": query, "type": type}
        if categories:
            params["categories"] = ",".join(map(str, categories))

        response = await self.get("/api/v1/search", params=params)
        return response.json()