"""Minecraft 資源模型定義"""

from dataclasses import dataclass, field
from typing import List, Optional, Literal
from datetime import datetime

ResourceType = Literal["mod", "plugin"]
ResourceCategory = Literal["new", "popular", "all"]

@dataclass(frozen=True)
class VersionInfo:
    """版本信息"""
    latest: str
    game_versions: List[str] = field(default_factory=list)

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
    """Minecraft 資源"""
    id: str
    name: str
    type: ResourceType
    version: VersionInfo
    sources: List[Source]
    description: str = ""
    authors: List[str] = field(default_factory=list)
    stats: Statistics = field(default_factory=Statistics)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    category: ResourceCategory = "all"
    
    def to_dict(self) -> dict:
        """轉換為符合 schema 的字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "author": self.authors[0] if self.authors else "",  # 使用第一個作者
            "downloads": self.stats.downloads,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        } 