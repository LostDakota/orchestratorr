"""
Pydantic schemas for Radarr API responses.

These schemas define the structure of Radarr API responses and are used to:
- Validate incoming data from Radarr
- Serialize responses back to the frontend
- Filter out unnecessary fields from massive Radarr JSON payloads
- Provide type safety and IDE autocomplete
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RadarrImage(BaseModel):
    """Image metadata (poster, fanart, banner, etc.)."""

    url: str
    altText: str = ""
    coverType: str  # poster, fanart, banner, etc.

    class Config:
        extra = "ignore"


class RadarrRating(BaseModel):
    """Rating information from multiple sources."""

    votes: int
    value: float
    type: str  # imdb, tmdb, metacritic, etc.

    class Config:
        extra = "ignore"


class RadarrMovie(BaseModel):
    """
    Condensed Radarr movie object.

    Extracted fields from the full Radarr API response, optimized for
    the frontend dashboard and library view.
    """

    id: int = Field(description="Radarr internal movie ID")
    title: str = Field(description="Movie title")
    sortTitle: str = Field(default="", description="Title for sorting")
    year: int = Field(description="Release year")
    tmdbId: int = Field(description="TMDB database ID")
    imdbId: Optional[str] = Field(default=None, description="IMDb ID")
    status: str = Field(description="Status: Missing, Downloaded, Announced")
    monitored: bool = Field(description="Is this movie monitored for updates")
    runtime: int = Field(default=0, description="Runtime in minutes")
    overview: str = Field(default="", description="Movie synopsis")
    ratings: list[RadarrRating] = Field(default_factory=list)
    images: list[RadarrImage] = Field(default_factory=list)
    qualityProfileId: int = Field(default=0)
    rootFolderPath: Optional[str] = Field(default=None)
    hasFile: bool = Field(default=False, description="Whether a copy is downloaded")
    inCinemas: Optional[str] = Field(default=None, description="Theater release date")
    physicalRelease: Optional[str] = Field(default=None, description="Physical release date")
    lastSearchTime: Optional[datetime] = Field(default=None)

    class Config:
        extra = "ignore"
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "The Matrix",
                "year": 1999,
                "tmdbId": 603,
                "imdbId": "tt0133093",
                "status": "Downloaded",
                "monitored": True,
                "runtime": 136,
                "ratings": [],
                "images": [],
                "hasFile": False
            }
        }


class RadarrSystemStatus(BaseModel):
    """System status response from Radarr."""

    appName: str = Field(description="Always 'Radarr'")
    version: str = Field(description="Radarr version number")
    os: str = Field(description="Operating system name")
    osVersion: str = Field(description="OS version details")
    isLinux: bool
    isWindows: bool
    isOsx: bool
    isDocker: bool
    isDebug: bool
    isProduction: bool
    isAdmin: bool
    isUserInteractive: bool
    branch: str = Field(description="Git branch: 'master' or 'develop'")
    authentication: str = Field(description="Authentication mode")
    databaseType: str = Field(description="Database type: sqlite, postgres, etc.")
    instanceName: Optional[str] = Field(default=None)

    class Config:
        extra = "ignore"


class RadarrCommand(BaseModel):
    """Radarr command response (search, refresh, etc.)."""

    id: int = Field(description="Command ID for tracking")
    name: str = Field(description="Command name (MoviesSearch, RefreshMovie, etc.)")
    commandName: Optional[str] = Field(default=None)
    status: str = Field(description="Status: pending, queued, started, completed, failed")
    queued: datetime = Field(description="When the command was queued")
    started: Optional[datetime] = Field(default=None)
    ended: Optional[datetime] = Field(default=None)
    duration: Optional[int] = Field(default=None, description="Duration in milliseconds")
    exception: Optional[str] = Field(default=None, description="Error message if failed")
    message: Optional[str] = Field(default=None)
    priority: str = Field(default="normal")
    sendUpdatesToClient: bool = Field(default=False)

    class Config:
        extra = "ignore"


class RadarrCalendarEvent(BaseModel):
    """Calendar event from Radarr's upcoming releases."""

    id: int
    title: str
    year: int
    monitored: bool
    status: str
    inCinemas: Optional[str] = None
    physicalRelease: Optional[str] = None
    images: list[RadarrImage] = Field(default_factory=list)
    ratings: list[RadarrRating] = Field(default_factory=list)

    class Config:
        extra = "ignore"
