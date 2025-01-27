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
    """Base resource model."""
    id: str
    name: str
    type: ResourceType
    version: VersionInfo
    sources: List[Source]
    description: str = ""
    authors: List[str] = field(default_factory=list)
    stats: Statistics = field(default_factory=Statistics)
    created_at: Optional[Union[str, datetime]] = None
    updated_at: Optional[Union[str, datetime]] = None
    category: ResourceCategory = ResourceCategory.ALL
    versions: List[VersionInfo] = field(default_factory=list)
    popularity: float = 0.0  # 熱門度分數，由各平台自行計算
    
    def to_dict(self) -> dict:
        """轉換為符合 schema 的字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "author": self.authors[0] if self.authors else "",  # 使用第一個作者
            "downloads": self.stats.downloads,
            "created_at": (
                self.created_at.isoformat() if isinstance(self.created_at, datetime)
                else self.created_at if self.created_at
                else datetime.now().isoformat()
            ),
            "updated_at": (
                self.updated_at.isoformat() if isinstance(self.updated_at, datetime)
                else self.updated_at if self.updated_at
                else datetime.now().isoformat()
            ),
            "resource_type": self.type
        } 