"""
FastAPI route modules for orchestratorr backend.

Contains all API endpoint definitions organized by functionality.
"""

from .proxy import router as proxy_router
from .search import router as search_router

__all__ = ["proxy_router", "search_router"]
