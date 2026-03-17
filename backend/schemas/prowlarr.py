"""
Pydantic schemas for Prowlarr API responses.

These schemas define the structure of Prowlarr API responses and are used to:
- Validate incoming data from Prowlarr
- Serialize responses back to the frontend
- Filter out unnecessary fields from massive Prowlarr JSON payloads
- Provide type safety and IDE autocomplete
"""

from datetime import datetime
from typing import Optional

from typing import Any

from pydantic import BaseModel, Field


class ProwlarrField(BaseModel):
    """Configuration field for an indexer."""

    order: int
    name: str
    label: str
    value: Optional[Any] = None
    type: str
    helpText: str = ""

    class Config:
        extra = "ignore"


class ProwlarrIndexer(BaseModel):
    """
    Prowlarr indexer configuration.

    Represents a configured indexer in Prowlarr.
    """

    id: int = Field(description="Indexer ID")
    name: str = Field(description="Indexer name")
    protocol: str = Field(description="Protocol: torrent, usenet")
    enabled: bool = Field(description="Is indexer enabled")
    enableRss: bool = Field(default=True)
    enableSearch: bool = Field(default=True)
    priority: int = Field(default=25)
    fields: list[ProwlarrField] = Field(default_factory=list)

    class Config:
        extra = "ignore"


class ProwlarrSearchResult(BaseModel):
    """Search result from Prowlarr."""

    guid: str = Field(description="Unique identifier")
    title: str = Field(description="Result title")
    size: int = Field(description="File size in bytes")
    indexer: str = Field(description="Source indexer name")
    publishDate: Optional[datetime] = None
    categories: list[int] = Field(default_factory=list)
    downloadUrl: Optional[str] = None
    magnetUrl: Optional[str] = None

    class Config:
        extra = "ignore"


class ProwlarrSystemStatus(BaseModel):
    """System status response from Prowlarr."""

    appName: str = Field(description="Always 'Prowlarr'")
    version: str = Field(description="Prowlarr version number")
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
