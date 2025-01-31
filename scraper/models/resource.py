"""Resource model module."""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Literal, Union
from datetime import datetime
from enum import Enum

ResourceType = Literal["mod", "plugin", "modpack", "resource_pack"]

class ResourceCategory(str, Enum):
    """Resource category enumeration."""
    NEW = "new"
    POPULAR = "popular"
    ALL = "all"

@dataclass(frozen=True)
class VersionInfo:
    """Version information."""
    version: str
    game_version: List[str]
    download_url: str
    dependencies: List[str]

@dataclass(frozen=True)
class Statistics:
    """統計信息"""
    downloads: int = 0
    rating: float = 0.0
    votes: int = 0

@dataclass(frozen=True)
class Source:
    """來源信息"""
    platform: str
    url: str
    external_id: str

@dataclass
class Resource:
    """
    Normalized resource model representing a Minecraft resource
    
    Attributes:
        id: Unique identifier
        name: Resource name
        description: Resource description
        author: Resource author
        downloads: Download count
        resource_type: Type of resource (mod, plugin, etc.)
        platform: Source platform
        created_at: Creation timestamp
        updated_at: Last update timestamp
        versions: List of supported game versions
        categories: Resource categories/tags
        website_url: Resource homepage URL
        source_url: Source code URL
        license: Resource license
    """
    id: str
    name: str
    description: str
    author: str
    downloads: int
    resource_type: str
    platform: str
    created_at: datetime
    updated_at: datetime
    versions: List[str]
    categories: List[str]
    website_url: str
    source_url: Optional[str] = None
    license: Optional[str] = None

    def to_dict(self) -> dict:
        """轉換為符合 schema 的字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "author": self.author,
            "downloads": self.downloads,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "resource_type": self.resource_type
        } 