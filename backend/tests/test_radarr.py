"""
Unit tests for RadarrClient service module.

Tests cover all public methods, error handling, async context manager,
and Pydantic schema validation.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

import httpx
from fastapi import HTTPException

from backend.clients.radarr import RadarrClient
from backend.schemas.radarr import (
    RadarrMovie,
    RadarrSystemStatus,
    RadarrCommand,
    RadarrCalendarEvent,
)


class TestRadarrClientInit:
    """Tests for RadarrClient initialization."""

    def test_init_stores_credentials(self):
        """Test that __init__ properly stores base_url and api_key."""
        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="test-api-key",
            timeout=15.0,
        )
        assert client.base_url == "http://localhost:7878"
        assert client.api_key == "test-api-key"
        assert client.timeout == 15.0

    def test_init_strips_trailing_slash(self):
        """Test that base_url trailing slash is removed."""
        client = RadarrClient(
            base_url="http://localhost:7878/",
            api_key="key",
        )
        assert client.base_url == "http://localhost:7878"

    def test_init_default_timeout(self):
        """Test that default timeout is 10 seconds."""
        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="key",
        )
        assert client.timeout == 10.0


@pytest.mark.asyncio
class TestRadarrClientContextManager:
    """Tests for async context manager support."""

    async def test_context_manager(self):
        """Test that context manager properly initializes and closes."""
        async with RadarrClient(
            base_url="http://localhost:7878",
            api_key="key",
        ) as client:
            assert client is not None
            assert client.api_key == "key"

    async def test_close_method(self):
        """Test that close() method closes the AsyncClient."""
        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="key",
        )
        # Create a client
        await client._get_client()
        assert client._client is not None
        
        # Close it
        await client.close()
        assert client._client is None


@pytest.mark.asyncio
class TestRadarrClientGetStatus:
    """Tests for get_status() method."""

    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_get_status_success(self, mock_client_class):
        """Test successful system status retrieval."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "appName": "Radarr",
            "version": "4.7.0.7191",
            "osVersion": "Linux x86_64",
            "isLinux": True,
            "isWindows": False,
            "isOsx": False,
            "isDocker": False,
            "branch": "master",
            "authentication": "basic",
            "databaseType": "sqlite",
        }

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="test-key",
        )
        client._client = mock_client

        result = await client.get_status()

        assert result["appName"] == "Radarr"
        assert result["version"] == "4.7.0.7191"
        assert result["isDocker"] is False

    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_get_status_api_error(self, mock_client_class):
        """Test error handling when API returns error."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Unauthorized"}

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="bad-key",
        )
        client._client = mock_client

        with pytest.raises(HTTPException) as exc_info:
            await client.get_status()

        assert exc_info.value.status_code == 401


@pytest.mark.asyncio
class TestRadarrClientGetMovies:
    """Tests for get_movies() method."""

    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_get_all_movies(self, mock_client_class):
        """Test retrieving entire movie library."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": 1,
                "title": "The Matrix",
                "year": 1999,
                "tmdbId": 603,
                "imdbId": "tt0133093",
                "status": "Downloaded",
                "monitored": True,
                "hasFile": True,
            },
            {
                "id": 2,
                "title": "Inception",
                "year": 2010,
                "tmdbId": 27205,
                "imdbId": "tt1375666",
                "status": "Downloaded",
                "monitored": True,
                "hasFile": True,
            },
        ]

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="test-key",
        )
        client._client = mock_client

        result = await client.get_movies()

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["title"] == "The Matrix"
        assert result[1]["title"] == "Inception"

    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_get_single_movie(self, mock_client_class):
        """Test retrieving a specific movie by ID."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1,
            "title": "The Matrix",
            "year": 1999,
            "tmdbId": 603,
            "imdbId": "tt0133093",
            "status": "Downloaded",
            "monitored": True,
            "hasFile": True,
        }

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="test-key",
        )
        client._client = mock_client

        result = await client.get_movies(movie_id=1)

        assert isinstance(result, dict)
        assert result["id"] == 1
        assert result["title"] == "The Matrix"

    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_get_empty_library(self, mock_client_class):
        """Test handling of empty library."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="test-key",
        )
        client._client = mock_client

        result = await client.get_movies()

        assert isinstance(result, list)
        assert len(result) == 0


@pytest.mark.asyncio
class TestRadarrClientCommandSearch:
    """Tests for command_search() method."""

    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_command_search_success(self, mock_client_class):
        """Test successful movie search command."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 42,
            "name": "MoviesSearch",
            "status": "pending",
            "queued": "2026-03-09T00:00:00Z",
            "duration": 5000,
        }

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="test-key",
        )
        client._client = mock_client

        result = await client.command_search([1, 2, 3])

        assert result["id"] == 42
        assert result["name"] == "MoviesSearch"
        assert result["status"] == "pending"

        # Verify the POST request was made with correct payload
        call_args = mock_client.request.call_args
        assert call_args[0][0] == "POST"
        assert "/api/v3/command" in call_args[0][1]

    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_command_search_empty_list_raises(self, mock_client_class):
        """Test that empty movie_ids list raises ValueError."""
        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="test-key",
        )

        with pytest.raises(ValueError) as exc_info:
            await client.command_search([])

        assert "cannot be empty" in str(exc_info.value)


@pytest.mark.asyncio
class TestRadarrClientCommandRefresh:
    """Tests for command_refresh() method."""

    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_command_refresh_all(self, mock_client_class):
        """Test refresh all movies command."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 43,
            "name": "RefreshMovie",
            "status": "pending",
        }

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="test-key",
        )
        client._client = mock_client

        result = await client.command_refresh()

        assert result["id"] == 43
        assert result["name"] == "RefreshMovie"

    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_command_refresh_single_movie(self, mock_client_class):
        """Test refresh specific movie command."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 44,
            "name": "RefreshMovie",
            "status": "pending",
        }

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="test-key",
        )
        client._client = mock_client

        result = await client.command_refresh(movie_id=5)

        assert result["id"] == 44


@pytest.mark.asyncio
class TestRadarrClientGetCalendar:
    """Tests for get_calendar() method."""

    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_get_calendar_success(self, mock_client_class):
        """Test retrieving calendar events."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": 10,
                "title": "Upcoming Movie",
                "year": 2026,
                "monitored": True,
                "status": "Announced",
                "inCinemas": "2026-03-15T00:00:00Z",
            }
        ]

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="test-key",
        )
        client._client = mock_client

        result = await client.get_calendar(
            start_date="2026-03-01",
            end_date="2026-03-31",
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["title"] == "Upcoming Movie"


@pytest.mark.asyncio
class TestRadarrClientAddMovie:
    """Tests for add_movie() method."""

    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_add_movie_success(self, mock_client_class):
        """Test adding a new movie to library."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 100,
            "title": "Fight Club",
            "year": 1999,
            "tmdbId": 550,
            "imdbId": "tt0137523",
            "status": "Missing",
            "monitored": True,
            "hasFile": False,
        }

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="test-key",
        )
        client._client = mock_client

        result = await client.add_movie(
            tmdb_id=550,
            title="Fight Club",
            quality_profile_id=1,
            root_folder_path="/movies",
        )

        assert result["id"] == 100
        assert result["title"] == "Fight Club"
        assert result["tmdbId"] == 550


@pytest.mark.asyncio
class TestRadarrClientDeleteMovie:
    """Tests for delete_movie() method."""

    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_delete_movie_success(self, mock_client_class):
        """Test deleting a movie from library."""
        mock_response = MagicMock()
        mock_response.status_code = 204

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="test-key",
        )
        client._client = mock_client

        # Should not raise
        await client.delete_movie(movie_id=1, delete_files=False)

        # Verify the DELETE request was made
        call_args = mock_client.request.call_args
        assert call_args[0][0] == "DELETE"

    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_delete_movie_with_files(self, mock_client_class):
        """Test deleting a movie and its files."""
        mock_response = MagicMock()
        mock_response.status_code = 204

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="test-key",
        )
        client._client = mock_client

        await client.delete_movie(movie_id=1, delete_files=True)

        # Verify params were passed
        call_args = mock_client.request.call_args
        assert "deleteFiles" in str(call_args)


@pytest.mark.asyncio
class TestRadarrClientErrorHandling:
    """Tests for error handling and exception mapping."""

    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_connection_error_handling(self, mock_client_class):
        """Test that connection errors are mapped to HTTPException."""
        mock_client = AsyncMock()
        mock_client.request.side_effect = httpx.RequestError("Connection refused")
        mock_client_class.return_value = mock_client

        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="test-key",
        )
        client._client = mock_client

        with pytest.raises(HTTPException) as exc_info:
            await client.get_status()

        assert exc_info.value.status_code == 503
        assert "Failed to connect" in exc_info.value.detail

    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_server_error_handling(self, mock_client_class):
        """Test that 5xx errors are properly handled."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal Server Error"}

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="test-key",
        )
        client._client = mock_client

        with pytest.raises(HTTPException) as exc_info:
            await client.get_status()

        assert exc_info.value.status_code == 500


class TestPydarrSchemas:
    """Tests for Pydantic schema validation."""

    def test_radarr_movie_schema_valid(self):
        """Test RadarrMovie schema with valid data."""
        movie_data = {
            "id": 1,
            "title": "The Matrix",
            "year": 1999,
            "tmdbId": 603,
            "status": "Downloaded",
            "monitored": True,
            "ratings": [],
            "images": [],
        }

        movie = RadarrMovie(**movie_data)
        assert movie.id == 1
        assert movie.title == "The Matrix"
        assert movie.year == 1999

    def test_radarr_system_status_schema(self):
        """Test RadarrSystemStatus schema."""
        status_data = {
            "appName": "Radarr",
            "version": "4.7.0.7191",
            "os": "Linux",
            "osVersion": "Linux x86_64",
            "isLinux": True,
            "isWindows": False,
            "isOsx": False,
            "isDocker": False,
            "isDebug": False,
            "isProduction": True,
            "isAdmin": True,
            "isUserInteractive": True,
            "branch": "master",
            "authentication": "basic",
            "databaseType": "sqlite",
        }

        status = RadarrSystemStatus(**status_data)
        assert status.appName == "Radarr"
        assert status.isLinux is True

    def test_radarr_command_schema(self):
        """Test RadarrCommand schema."""
        command_data = {
            "id": 42,
            "name": "MoviesSearch",
            "status": "pending",
            "queued": datetime.now(),
            "priority": "normal",
        }

        command = RadarrCommand(**command_data)
        assert command.id == 42
        assert command.name == "MoviesSearch"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
