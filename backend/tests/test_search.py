"""
Unit tests for the universal search router and search functions.

Tests coverage:
- SearchResult schema and serialization
- Radarr movie search
- Sonarr series search
- Parallel async search aggregation
- Error handling and graceful failures
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException

from backend.routes.search import (
    SearchResult,
    search_radarr,
    search_sonarr,
    search_lidarr,
)
from backend.clients.radarr import RadarrClient
from backend.clients.sonarr import SonarrClient


# ============================================================================
# Tests for SearchResult Schema
# ============================================================================


class TestSearchResult:
    """Tests for SearchResult data model."""

    def test_search_result_initialization(self):
        """Test SearchResult object creation and initialization."""
        result = SearchResult(
            title="The Matrix",
            year=1999,
            overview="A hacker learns the truth about reality.",
            source_service="radarr",
            source_type="movie",
            remote_id=123,
            tmdb_id=603,
            imdb_id="tt0133093",
            poster_url="https://example.com/poster.jpg",
            status="missing",
            in_library=False,
        )

        assert result.title == "The Matrix"
        assert result.year == 1999
        assert result.source_service == "radarr"
        assert result.source_type == "movie"
        assert result.remote_id == 123
        assert result.status == "missing"
        assert result.in_library is False

    def test_search_result_to_dict(self):
        """Test SearchResult serialization to dictionary."""
        result = SearchResult(
            title="Breaking Bad",
            year=2008,
            overview="A chemistry teacher turns to cooking meth.",
            source_service="sonarr",
            source_type="tv",
            remote_id=456,
            tmdb_id=1396,
            poster_url="https://example.com/poster.jpg",
            in_library=True,
        )

        data = result.to_dict()

        assert data["title"] == "Breaking Bad"
        assert data["year"] == 2008
        assert data["source_type"] == "tv"
        assert data["in_library"] is True
        assert isinstance(data["overview"], str)
        assert data["overview"]  # Non-empty

    def test_search_result_overview_truncation(self):
        """Test that overview is truncated to 200 chars in serialization."""
        long_overview = "x" * 500  # Create a 500-char string
        result = SearchResult(
            title="Test",
            overview=long_overview,
            source_service="radarr",
            source_type="movie",
        )

        data = result.to_dict()
        assert len(data["overview"]) == 200

    def test_search_result_optional_fields(self):
        """Test SearchResult with minimal required fields."""
        result = SearchResult(title="Minimal Movie")

        assert result.title == "Minimal Movie"
        assert result.year is None
        assert result.overview == ""
        assert result.source_service == "unknown"
        assert result.remote_id is None

        data = result.to_dict()
        assert data["title"] == "Minimal Movie"


# ============================================================================
# Tests for Radarr Search
# ============================================================================


@pytest.mark.asyncio
async def test_search_radarr_success():
    """Test successful Radarr movie search."""
    mock_client = AsyncMock(spec=RadarrClient)
    mock_client.search_movies.return_value = [
        {
            "id": 1,
            "title": "The Matrix",
            "year": 1999,
            "tmdbId": 603,
            "imdbId": "tt0133093",
            "overview": "A hacker learns the truth about reality.",
            "images": [
                {
                    "coverType": "poster",
                    "url": "https://example.com/matrix-poster.jpg",
                }
            ],
        }
    ]

    results = await search_radarr(mock_client, "matrix")

    assert len(results) == 1
    assert results[0].title == "The Matrix"
    assert results[0].source_type == "movie"
    assert results[0].source_service == "radarr"
    assert results[0].year == 1999


@pytest.mark.asyncio
async def test_search_radarr_empty_results():
    """Test Radarr search with no results."""
    mock_client = AsyncMock(spec=RadarrClient)
    mock_client.search_movies.return_value = []

    results = await search_radarr(mock_client, "nonexistent")

    assert len(results) == 0


@pytest.mark.asyncio
async def test_search_radarr_handles_missing_poster():
    """Test Radarr search handles movies without poster images."""
    mock_client = AsyncMock(spec=RadarrClient)
    mock_client.search_movies.return_value = [
        {
            "id": 1,
            "title": "No Poster Movie",
            "year": 2023,
            "tmdbId": 999,
            "images": [],  # No images
        }
    ]

    results = await search_radarr(mock_client, "no poster")

    assert len(results) == 1
    assert results[0].poster_url is None


@pytest.mark.asyncio
async def test_search_radarr_api_error():
    """Test Radarr search handles API errors gracefully."""
    mock_client = AsyncMock(spec=RadarrClient)
    mock_client.search_movies.side_effect = Exception("API Error")

    results = await search_radarr(mock_client, "error")

    assert len(results) == 0  # Returns empty list on error


# ============================================================================
# Tests for Sonarr Search
# ============================================================================


@pytest.mark.asyncio
async def test_search_sonarr_success():
    """Test successful Sonarr series search."""
    mock_client = AsyncMock(spec=SonarrClient)
    mock_client.search_series.return_value = [
        {
            "id": 1,
            "title": "Breaking Bad",
            "year": 2008,
            "tvdbId": 81189,
            "tmdbId": 1396,
            "overview": "A chemistry teacher turns to cooking meth.",
            "images": [
                {
                    "coverType": "poster",
                    "url": "https://example.com/breaking-bad-poster.jpg",
                }
            ],
        }
    ]

    results = await search_sonarr(mock_client, "breaking bad")

    assert len(results) == 1
    assert results[0].title == "Breaking Bad"
    assert results[0].source_type == "tv"
    assert results[0].source_service == "sonarr"
    assert results[0].year == 2008


@pytest.mark.asyncio
async def test_search_sonarr_not_configured():
    """Test Sonarr search when client is None."""
    results = await search_sonarr(None, "test")

    assert len(results) == 0  # Returns empty list if not configured


@pytest.mark.asyncio
async def test_search_sonarr_api_error():
    """Test Sonarr search handles API errors gracefully."""
    mock_client = AsyncMock(spec=SonarrClient)
    mock_client.search_series.side_effect = Exception("API Error")

    results = await search_sonarr(mock_client, "error")

    assert len(results) == 0  # Returns empty list on error


# ============================================================================
# Tests for Parallel Search (asyncio.gather)
# ============================================================================


@pytest.mark.asyncio
async def test_parallel_search_all_services():
    """Test that search functions can be executed in parallel."""
    mock_radarr = AsyncMock(spec=RadarrClient)
    mock_radarr.search_movies.return_value = [
        {
            "id": 1,
            "title": "The Matrix",
            "year": 1999,
            "tmdbId": 603,
            "images": [],
        }
    ]

    mock_sonarr = AsyncMock(spec=SonarrClient)
    mock_sonarr.search_series.return_value = [
        {
            "id": 1,
            "title": "Breaking Bad",
            "year": 2008,
            "tvdbId": 81189,
            "images": [],
        }
    ]

    # Execute searches in parallel
    radarr_results, sonarr_results = await asyncio.gather(
        search_radarr(mock_radarr, "test"),
        search_sonarr(mock_sonarr, "test"),
        return_exceptions=True,
    )

    assert len(radarr_results) == 1
    assert radarr_results[0].source_type == "movie"
    assert len(sonarr_results) == 1
    assert sonarr_results[0].source_type == "tv"


@pytest.mark.asyncio
async def test_parallel_search_with_failure():
    """Test parallel search handles one failure without blocking others."""
    mock_radarr = AsyncMock(spec=RadarrClient)
    mock_radarr.search_movies.side_effect = Exception("Radarr Down")

    mock_sonarr = AsyncMock(spec=SonarrClient)
    mock_sonarr.search_series.return_value = [
        {"id": 1, "title": "Test Show", "images": []}
    ]

    radarr_results, sonarr_results = await asyncio.gather(
        search_radarr(mock_radarr, "test"),
        search_sonarr(mock_sonarr, "test"),
        return_exceptions=True,
    )

    # Radarr failed but Sonarr succeeded
    assert len(radarr_results) == 0
    assert len(sonarr_results) == 1


# ============================================================================
# Tests for Search Result Sorting
# ============================================================================


def test_search_results_sorting():
    """Test that search results are sorted by year (descending) then title."""
    results = [
        SearchResult(title="Old Movie", year=1990, source_type="movie"),
        SearchResult(title="New Movie", year=2023, source_type="movie"),
        SearchResult(title="Middle Movie", year=2000, source_type="movie"),
    ]

    # Sort like the API does
    results.sort(key=lambda x: (-x.year if x.year else 0, x.title))

    assert results[0].title == "New Movie"  # 2023
    assert results[1].title == "Middle Movie"  # 2000
    assert results[2].title == "Old Movie"  # 1990


def test_search_results_sorting_with_none_year():
    """Test sorting handles movies with None year."""
    results = [
        SearchResult(title="Unknown Year", year=None, source_type="movie"),
        SearchResult(title="2023 Movie", year=2023, source_type="movie"),
    ]

    results.sort(key=lambda x: (-x.year if x.year else 0, x.title))

    assert results[0].title == "2023 Movie"
    assert results[1].title == "Unknown Year"


# ============================================================================
# Tests for Lidarr Search (Placeholder)
# ============================================================================


@pytest.mark.asyncio
async def test_search_lidarr_not_implemented():
    """Test Lidarr search currently returns empty (TODO)."""
    results = await search_lidarr("test")

    # Currently not implemented, should return empty list
    assert len(results) == 0
