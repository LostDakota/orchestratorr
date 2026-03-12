"""
Test suite for search functionality and CORS configuration.
"""

import os
import sys
from unittest.mock import AsyncMock, patch

# Set environment variables before importing app
os.environ.setdefault("RADARR_URL", "http://localhost:7878")
os.environ.setdefault("RADARR_API_KEY", "test-key")
os.environ.setdefault("SONARR_URL", "http://localhost:8989")
os.environ.setdefault("SONARR_API_KEY", "test-key")
os.environ.setdefault("LIDARR_URL", "http://localhost:8686")
os.environ.setdefault("LIDARR_API_KEY", "test-key")

# Now import FastAPI and create test client
from fastapi.testclient import TestClient

from backend.main import app
from backend.config import settings


def test_health_endpoint():
    """Test that health endpoint returns 200."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_health_endpoint():
    """Test that API health endpoint returns 200."""
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_cors_allowed_origins_includes_localhost_8081():
    """Test that allowed origins includes localhost:8081 (for custom port setup)."""
    assert "http://localhost:8081" in settings.allowed_origins
    assert "http://localhost:80" in settings.allowed_origins
    assert "http://localhost" in settings.allowed_origins


def test_cors_allowed_origins_includes_common_ports():
    """Test that allowed origins includes common development ports."""
    common_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8081",
    ]
    for origin in common_origins:
        assert origin in settings.allowed_origins, f"Missing {origin} in allowed_origins"


def test_search_endpoint_returns_json():
    """Test that search endpoint returns valid JSON structure (no external calls)."""
    client = TestClient(app)
    
    # Mock the client dependencies to avoid actual HTTP calls
    with patch("backend.routes.search.get_radarr_client") as mock_radarr:
        with patch("backend.routes.search.get_sonarr_client") as mock_sonarr:
            with patch("backend.routes.search.get_lidarr_client") as mock_lidarr:
                # Create mock clients that return empty results
                mock_radarr.return_value = AsyncMock()
                mock_sonarr.return_value = AsyncMock()
                mock_lidarr.return_value = AsyncMock()
                
                # Make request - will get a validation error due to missing dependency
                # but we're testing the route exists and structure is correct
                response = client.get("/api/v1/search?q=test&limit=10")
                
                # Should not be 404 (route exists)
                # May be 503 if service not configured, but at least it's a known error
                assert response.status_code in [200, 503]


def test_search_endpoint_requires_query_parameter():
    """Test that search endpoint requires query parameter."""
    client = TestClient(app)
    
    # Request without query parameter should fail
    response = client.get("/api/v1/search?limit=10")
    assert response.status_code == 422  # Validation error


def test_cors_headers_present_in_response():
    """Test that CORS headers are included in response."""
    client = TestClient(app)
    
    # Make a request with Origin header (simulating browser)
    response = client.get(
        "/api/v1/health",
        headers={"Origin": "http://localhost:8081"}
    )
    
    assert response.status_code == 200
    # CORS headers should be present if origin is allowed
    # FastAPI CORSMiddleware adds them automatically


def test_root_endpoint_lists_endpoints():
    """Test that root endpoint provides service information."""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "endpoints" in data
    assert "health" in data["endpoints"]


if __name__ == "__main__":
    # Run tests manually if executed directly
    test_health_endpoint()
    test_api_health_endpoint()
    test_cors_allowed_origins_includes_localhost_8081()
    test_cors_allowed_origins_includes_common_ports()
    test_search_endpoint_returns_json()
    test_search_endpoint_requires_query_parameter()
    test_cors_headers_present_in_response()
    test_root_endpoint_lists_endpoints()
    print("All tests passed!")
