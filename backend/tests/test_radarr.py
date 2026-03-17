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
from backend.schemas import (
    RadarrMovie,
    RadarrSystemStatus,
    RadarrCommand,
    RadarrCalendarEvent,
)


# Test data helpers
def get_mock_system_status():
    return {
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


def get_mock_movie(movie_id=1, title="The Matrix", year=1999):
    return {
        "id": movie_id,
        "title": title,
        "year": year,
        "tmdbId": 603,
        "imdbId": "tt0133093",
        "status": "Downloaded",
        "monitored": True,
        "hasFile": True,
    }


def get_mock_command(command_id=42, name="MoviesSearch"):
    return {
        "id": command_id,
        "name": name,
        "status": "pending",
        "queued": datetime.now().isoformat(),
        "duration": 5000,
    }


def get_mock_calendar_event(event_id=10):
    return {
        "id": event_id,
        "title": "Upcoming Movie",
        "year": 2026,
        "monitored": True,
        "status": "Announced",
    }


class TestRadarrClientInit:
    def test_init_stores_credentials(self):
        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="test-api-key",
            timeout=15.0,
        )
        assert client.base_url == "http://localhost:7878"
        assert client.api_key == "test-api-key"
        assert client.timeout == 15.0

    def test_init_strips_trailing_slash(self):
        client = RadarrClient(
            base_url="http://localhost:7878/",
            api_key="key",
        )
        assert client.base_url == "http://localhost:7878"

    def test_init_default_timeout(self):
        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="key",
        )
        assert client.timeout == 10.0


@pytest.mark.asyncio
class TestRadarrClientContextManager:
    async def test_context_manager(self):
        async with RadarrClient(
            base_url="http://localhost:7878",
            api_key="key",
        ) as client:
            assert client is not None
            assert client.api_key == "key"

    async def test_close_method(self):
        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="key",
        )
        await client._get_client()
        assert client._client is not None
        await client.close()
        assert client._client is None


@pytest.mark.asyncio
class TestRadarrClientGetStatus:
    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_get_status_success(self, mock_client_class):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = get_mock_system_status()

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="test-key",
        )
        client._client = mock_client

        result = await client.get_status()

        assert isinstance(result, RadarrSystemStatus)
        assert result.appName == "Radarr"
        assert result.version == "4.7.0.7191"
        assert result.isDocker is False

    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_get_status_api_error(self, mock_client_class):
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
    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_get_all_movies(self, mock_client_class):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            get_mock_movie(1, "The Matrix", 1999),
            get_mock_movie(2, "Inception", 2010),
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
        assert isinstance(result[0], RadarrMovie)
        assert result[0].title == "The Matrix"
        assert result[1].title == "Inception"

    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_get_single_movie(self, mock_client_class):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = get_mock_movie(1, "The Matrix", 1999)

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="test-key",
        )
        client._client = mock_client

        result = await client.get_movies(movie_id=1)

        assert isinstance(result, RadarrMovie)
        assert result.id == 1
        assert result.title == "The Matrix"

    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_get_empty_library(self, mock_client_class):
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
    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_command_search_success(self, mock_client_class):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = get_mock_command(42, "MoviesSearch")

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="test-key",
        )
        client._client = mock_client

        result = await client.command_search([1, 2, 3])

        assert isinstance(result, RadarrCommand)
        assert result.id == 42
        assert result.name == "MoviesSearch"
        assert result.status == "pending"

    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_command_search_empty_list_raises(self, mock_client_class):
        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="test-key",
        )

        with pytest.raises(ValueError) as exc_info:
            await client.command_search([])

        assert "cannot be empty" in str(exc_info.value)


@pytest.mark.asyncio
class TestRadarrClientCommandRefresh:
    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_command_refresh_all(self, mock_client_class):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = get_mock_command(43, "RefreshMovie")

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="test-key",
        )
        client._client = mock_client

        result = await client.command_refresh()

        assert isinstance(result, RadarrCommand)
        assert result.id == 43
        assert result.name == "RefreshMovie"

    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_command_refresh_single_movie(self, mock_client_class):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = get_mock_command(44, "RefreshMovie")

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = RadarrClient(
            base_url="http://localhost:7878",
            api_key="test-key",
        )
        client._client = mock_client

        result = await client.command_refresh(movie_id=5)

        assert isinstance(result, RadarrCommand)
        assert result.id == 44


@pytest.mark.asyncio
class TestRadarrClientGetCalendar:
    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_get_calendar_success(self, mock_client_class):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [get_mock_calendar_event(10)]

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
        assert isinstance(result[0], RadarrCalendarEvent)
        assert result[0].title == "Upcoming Movie"


@pytest.mark.asyncio
class TestRadarrClientAddMovie:
    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_add_movie_success(self, mock_client_class):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = get_mock_movie(100, "Fight Club", 1999)

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

        assert isinstance(result, RadarrMovie)
        assert result.id == 100
        assert result.title == "Fight Club"


@pytest.mark.asyncio
class TestRadarrClientDeleteMovie:
    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_delete_movie_success(self, mock_client_class):
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

        await client.delete_movie(movie_id=1, delete_files=False)

        call_args = mock_client.request.call_args
        assert call_args[0][0] == "DELETE"


@pytest.mark.asyncio
class TestRadarrClientErrorHandling:
    @patch("backend.clients.base.httpx.AsyncClient")
    async def test_connection_error_handling(self, mock_client_class):
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


class TestPydanticSchemas:
    def test_radarr_movie_schema_valid(self):
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
        status = RadarrSystemStatus(**get_mock_system_status())
        assert status.appName == "Radarr"
        assert status.isLinux is True

    def test_radarr_command_schema(self):
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
