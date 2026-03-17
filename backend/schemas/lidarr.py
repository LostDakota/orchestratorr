"""
Pydantic schemas for Lidarr API responses.

These schemas define the structure of Lidarr API responses and are used to:
- Validate incoming data from Lidarr
- Serialize responses back to the frontend
- Filter out unnecessary fields from massive Lidarr JSON payloads
- Provide type safety and IDE autocomplete
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LidarrImage(BaseModel):
    """Image metadata (poster, fanart, banner, etc.)."""

    url: str
    altText: str = ""
    coverType: str  # poster, fanart, banner, etc.

    class Config:
        extra = "ignore"


class LidarrRating(BaseModel):
    """Rating information from multiple sources."""

    votes: int
    value: float

    class Config:
        extra = "ignore"


class LidarrAlbum(BaseModel):
    """Album information for an artist."""

    id: Optional[int] = None
    title: str
    foreignAlbumId: str
    monitored: bool
    albumType: str
    releaseDate: Optional[str] = None

    class Config:
        extra = "ignore"


class LidarrArtist(BaseModel):
    """
    Condensed Lidarr artist object.

    Extracted fields from the full Lidarr API response, optimized for
    the frontend dashboard and library view.
    """

    id: Optional[int] = None
    artistName: str = Field(description="Artist name")
    sortName: str = Field(default="", description="Name for sorting")
    foreignArtistId: str = Field(description="MusicBrainz ID")
    tmdbId: Optional[int] = Field(default=None)
    status: str = Field(description="Status: Active, Disbanded, etc.")
    monitored: bool = Field(description="Is this artist monitored for updates")
    overview: str = Field(default="", description="Artist biography")
    ratings: Optional[LidarrRating] = None
    images: list[LidarrImage] = Field(default_factory=list)
    qualityProfileId: int = Field(default=0)
    rootFolderPath: Optional[str] = Field(default=None)
    albumCount: int = Field(default=0)

    class Config:
        extra = "ignore"


class LidarrSystemStatus(BaseModel):
    """System status response from Lidarr."""

    appName: str = Field(description="Always 'Lidarr'")
    version: str = Field(description="Lidarr version number")
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


class LidarrCommand(BaseModel):
    """Lidarr command response (search, refresh, etc.)."""

    id: int = Field(description="Command ID for tracking")
    name: str = Field(description="Command name (ArtistSearch, RefreshArtist, etc.)")
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
