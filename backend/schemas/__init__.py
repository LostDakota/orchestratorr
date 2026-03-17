"""
Pydantic schemas for *arr API responses.

Provides type-safe, validated schemas for serializing *arr API responses
to the Svelte frontend.
"""

from .radarr import (
    RadarrCalendarEvent,
    RadarrCommand,
    RadarrImage,
    RadarrMovie,
    RadarrRating,
    RadarrSystemStatus,
)
from .sonarr import (
    SonarrCalendarEvent,
    SonarrCommand,
    SonarrImage,
    SonarrRating,
    SonarrSeries,
    SonarrSystemStatus,
)
from .lidarr import (
    LidarrAlbum,
    LidarrArtist,
    LidarrCommand,
    LidarrImage,
    LidarrRating,
    LidarrSystemStatus,
)
from .prowlarr import (
    ProwlarrField,
    ProwlarrIndexer,
    ProwlarrSearchResult,
    ProwlarrSystemStatus,
)
from .disk_space import DiskSpace, ClientUsedSpace

__all__ = [
    # Radarr
    "RadarrMovie",
    "RadarrSystemStatus",
    "RadarrCommand",
    "RadarrCalendarEvent",
    "RadarrImage",
    "RadarrRating",
    # Sonarr
    "SonarrSeries",
    "SonarrSystemStatus",
    "SonarrCommand",
    "SonarrCalendarEvent",
    "SonarrImage",
    "SonarrRating",
    # Lidarr
    "LidarrArtist",
    "LidarrAlbum",
    "LidarrSystemStatus",
    "LidarrCommand",
    "LidarrImage",
    "LidarrRating",
    # Prowlarr
    "ProwlarrIndexer",
    "ProwlarrField",
    "ProwlarrSearchResult",
    "ProwlarrSystemStatus",
    # Common
    "DiskSpace",
    "ClientUsedSpace",
]
