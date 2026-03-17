"""
Pydantic schemas for Sonarr API responses.

These schemas define the structure of Sonarr API responses and are used to:
- Validate incoming data from Sonarr
- Serialize responses back to the frontend
- Filter out unnecessary fields from massive Sonarr JSON payloads
- Provide type safety and IDE autocomplete
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SonarrImage(BaseModel):
    """Image metadata (poster, fanart, banner, etc.)."""

    url: str
    altText: str = ""
    coverType: str  # poster, fanart, banner, etc.

    class Config:
        extra = "ignore"


class SonarrRating(BaseModel):
    """Rating information from multiple sources."""

    votes: int
    value: float

    class Config:
        extra = "ignore"


class SonarrSeries(BaseModel):
    """
    Condensed Sonarr series object.

    Extracted fields from the full Sonarr API response, optimized for
    the frontend dashboard and library view.
    """

    id: Optional[int] = None
    title: str = Field(description="Series title")
    sortTitle: str = Field(default="", description="Title for sorting")
    year: int = Field(description="First air year")
    tvdbId: int = Field(description="TVDB database ID")
    tmdbId: Optional[int] = Field(default=None, description="TMDB ID")
    imdbId: Optional[str] = Field(default=None, description="IMDb ID")
    status: str = Field(description="Status: Continuing, Ended, Upcoming")
    monitored: bool = Field(description="Is this series monitored for updates")
    runtime: int = Field(default=0, description="Episode runtime in minutes")
    overview: str = Field(default="", description="Series synopsis")
    ratings: Optional[SonarrRating] = None
    images: list[SonarrImage] = Field(default_factory=list)
    qualityProfileId: int = Field(default=0)
    rootFolderPath: Optional[str] = Field(default=None)
    seasonCount: int = Field(default=0)
    episodeCount: int = Field(default=0)
    episodeFileCount: int = Field(default=0)
    nextAiring: Optional[datetime] = Field(default=None)
    previousAiring: Optional[datetime] = Field(default=None)

    class Config:
        extra = "ignore"


class SonarrSystemStatus(BaseModel):
    """System status response from Sonarr."""

    appName: str = Field(description="Always 'Sonarr'")
    version: str = Field(description="Sonarr version number")
    osName: str = Field(description="Operating system name")
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


class SonarrCommand(BaseModel):
    """Sonarr command response (search, refresh, etc.)."""

    id: int = Field(description="Command ID for tracking")
    name: str = Field(description="Command name (SeriesSearch, RefreshSeries, etc.)")
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


class SonarrCalendarEvent(BaseModel):
    """Calendar event from Sonarr's upcoming episodes."""

    id: int
    seriesId: int
    episodeNumber: int
    seasonNumber: int
    title: str
    airDate: Optional[str] = None
    airDateUtc: Optional[datetime] = None
    monitored: bool
    status: str
    images: list[SonarrImage] = Field(default_factory=list)

    class Config:
        extra = "ignore"
