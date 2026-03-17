"""
Pydantic schemas for *arr API responses.

Provides type-safe, validated schemas for serializing *arr API responses
to the Svelte frontend.
"""

from .radarr import (
    RadarrCalendarEvent,
    RadarrCommand,
    RadarrMovie,
    RadarrSystemStatus,
)

from .disk_space import DiskSpace, ClientUsedSpace

__all__ = [
    "RadarrMovie",
    "RadarrSystemStatus",
    "RadarrCommand",
    "RadarrCalendarEvent",
    "DiskSpace",
    "ClientUsedSpace"
]
