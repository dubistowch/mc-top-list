"""Resource model module."""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Literal, Union, Dict, Any
from datetime import datetime
from enum import Enum

class ResourceType(str, Enum):
    """Resource type enumeration."""
    MOD = "mod"
    PLUGIN = "plugin"
    MODPACK = "modpack"
    RESOURCEPACK = "resourcepack"
    DATAPACK = "datapack"
    PLUGINPACK = "pluginpack"
    ADDON = "addon"

# For backwards compatibility
ResourceTypeLiteral = Literal["mod", "plugin", "modpack", "resourcepack", "datapack", "pluginpack", "addon"]

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
    platform: str = field(default="unknown")
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    versions: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    website_url: str = field(default="")
    source_url: Optional[str] = None
    license: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """轉換為符合 schema 的字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "author": self.author,
            "downloads": self.downloads,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "resource_type": self.resource_type,
            "platform": self.platform,
            "versions": self.versions,
            "categories": self.categories,
            "website_url": self.website_url,
            "source_url": self.source_url,
            "license": self.license
        } 