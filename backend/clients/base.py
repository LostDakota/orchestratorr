"""
Base asynchronous HTTP client for *arr API interactions.

This module provides the foundational client layer for communicating with
Radarr, Sonarr, Lidarr, Prowlarr, and other *arr services via their REST APIs.
All network calls are non-blocking and managed through httpx.AsyncClient.
"""

import logging
from typing import Any, Optional

import httpx
from fastapi import HTTPException

logger = logging.getLogger(__name__)

# Default timeout for all API requests (seconds)
DEFAULT_TIMEOUT = 10.0


class BaseArrClient:
    """
    Asynchronous HTTP client for *arr API interactions.

    This client handles all communication with *arr services, including:
    - Automatic API key injection via X-Api-Key header
    - Request/response error handling
    - Timeout management
    - FastAPI-compatible exception mapping

    Attributes:
        base_url (str): The base URL of the *arr service (e.g., http://localhost:7878)
        api_key (str): The API key for the *arr service
        timeout (float): Request timeout in seconds (default: 10.0)
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        """
        Initialize the BaseArrClient.

        Args:
            base_url (str): The base URL of the *arr service (without trailing slash)
            api_key (str): The API key for authentication
            timeout (float): Request timeout in seconds (default: 10.0)

        Example:
            client = BaseArrClient(
                base_url="http://localhost:7878",
                api_key="your-api-key-here"
            )
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """
        Lazily instantiate and return the AsyncClient.

        This ensures the client is only created when needed and can be
        properly closed via context manager or explicit cleanup.

        Returns:
            httpx.AsyncClient: The async HTTP client instance
        """
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def close(self) -> None:
        """
        Close the underlying AsyncClient connection pool.

        Call this when finished using the client, or use as a context manager.
        """
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit; closes the client."""
        await self.close()

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> httpx.Response:
        """
        Base request wrapper for all HTTP verbs.

        Handles:
        - URL construction (base_url + endpoint)
        - X-Api-Key header injection
        - Connection error handling
        - Timeout management

        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint (str): API endpoint path (e.g., "/api/v3/movie")
            **kwargs: Additional arguments to pass to httpx (headers, params, json, data, etc.)

        Returns:
            httpx.Response: The response object from the *arr service

        Raises:
            HTTPException: If the request fails or the service returns an error status
        """
        url = f"{self.base_url}{endpoint}"

        # Merge X-Api-Key into headers
        headers = kwargs.pop("headers", {})
        headers["X-Api-Key"] = self.api_key
        headers.setdefault("Content-Type", "application/json")

        try:
            client = await self._get_client()
            response = await client.request(
                method,
                url,
                headers=headers,
                **kwargs,
            )

            # Raise HTTPException for 4xx/5xx responses
            if response.status_code >= 400:
                try:
                    error_detail = response.json()
                except Exception:
                    error_detail = response.text

                logger.warning(
                    f"*arr API error: {method} {endpoint} -> {response.status_code}",
                    extra={"error": error_detail},
                )
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_detail,
                )

            return response

        except httpx.RequestError as e:
            logger.error(
                f"Request failed: {method} {url}",
                exc_info=e,
            )
            raise HTTPException(
                status_code=503,
                detail=f"Failed to connect to *arr service: {str(e)}",
            )

    async def get(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ) -> httpx.Response:
        """
        Perform a GET request to the *arr API.

        Args:
            endpoint (str): API endpoint path
            params (dict, optional): Query parameters
            **kwargs: Additional arguments to pass to the underlying request

        Returns:
            httpx.Response: The response from the *arr service
        """
        return await self._request("GET", endpoint, params=params, **kwargs)

    async def post(
        self,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        **kwargs,
    ) -> httpx.Response:
        """
        Perform a POST request to the *arr API.

        Args:
            endpoint (str): API endpoint path
            data (dict, optional): Request body (will be JSON-encoded)
            **kwargs: Additional arguments to pass to the underlying request

        Returns:
            httpx.Response: The response from the *arr service
        """
        return await self._request("POST", endpoint, json=data, **kwargs)

    async def put(
        self,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        **kwargs,
    ) -> httpx.Response:
        """
        Perform a PUT request to the *arr API.

        Args:
            endpoint (str): API endpoint path
            data (dict, optional): Request body (will be JSON-encoded)
            **kwargs: Additional arguments to pass to the underlying request

        Returns:
            httpx.Response: The response from the *arr service
        """
        return await self._request("PUT", endpoint, json=data, **kwargs)

    async def delete(
        self,
        endpoint: str,
        **kwargs,
    ) -> httpx.Response:
        """
        Perform a DELETE request to the *arr API.

        Args:
            endpoint (str): API endpoint path
            **kwargs: Additional arguments to pass to the underlying request

        Returns:
            httpx.Response: The response from the *arr service
        """
        return await self._request("DELETE", endpoint, **kwargs)
