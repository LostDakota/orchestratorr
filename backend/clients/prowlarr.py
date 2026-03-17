"""
Prowlarr API client for indexer management.

Provides asynchronous methods for interacting with Prowlarr v1 API endpoints,
including system status and indexer management.
"""

from typing import Any, Optional

from backend.schemas import (
    ProwlarrIndexer,
    ProwlarrSearchResult,
    ProwlarrSystemStatus,
)

from .base import BaseArrClient


class ProwlarrClient(BaseArrClient):
    """
    Asynchronous client for Prowlarr API v1.

    Handles all interactions with Prowlarr, including system health checks,
    indexer queries, and search operations.

    Inherits from BaseArrClient and maintains the same async/error handling patterns.
    """

    async def get_status(self) -> ProwlarrSystemStatus:
        """
        Fetch Prowlarr system status and version information.

        Returns:
            ProwlarrSystemStatus: System status response from Prowlarr

        Raises:
            HTTPException: If the request fails or Prowlarr returns an error
        """
        response = await self.get("/api/v1/system/status")
        return ProwlarrSystemStatus(**response.json())

    async def get_indexers(
        self,
        indexer_id: Optional[int] = None,
    ) -> ProwlarrIndexer | list[ProwlarrIndexer]:
        """
        Fetch indexers from Prowlarr.

        Args:
            indexer_id (int, optional): If provided, fetch only this specific indexer.
                                       If None, return the entire list.

        Returns:
            ProwlarrIndexer or list[ProwlarrIndexer]: Indexer(s) from Prowlarr

        Raises:
            HTTPException: If the request fails or indexer_id doesn't exist
        """
        if indexer_id is not None:
            response = await self.get(f"/api/v1/indexer/{indexer_id}")
            return ProwlarrIndexer(**response.json())
        else:
            response = await self.get("/api/v1/indexer")
            data = response.json()
            return [ProwlarrIndexer(**item) for item in data]

    async def search(
        self,
        query: str,
        categories: Optional[list[int]] = None,
        type: str = "search",
    ) -> list[ProwlarrSearchResult]:
        """
        Search across all configured indexers.

        Args:
            query (str): Search query string
            categories (list[int], optional): Category IDs to filter by
            type (str): Search type ("search", "tv-search", "movie-search", "music-search")

        Returns:
            list[ProwlarrSearchResult]: Search results from indexers

        Raises:
            HTTPException: If the request fails
        """
        params = {"query": query, "type": type}
        if categories:
            params["categories"] = ",".join(map(str, categories))

        response = await self.get("/api/v1/search", params=params)
        data = response.json()
        return [ProwlarrSearchResult(**item) for item in data]
