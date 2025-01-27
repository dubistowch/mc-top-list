"""Hangar resource transformer implementation."""

from typing import Dict, Tuple
from datetime import datetime

from scraper.contracts.transformer import ResourceTransformerContract
from scraper.utils.logger import setup_logger


class HangarResourceTransformer(ResourceTransformerContract):
    """Hangar resource transformer"""

    def __init__(self):
        """Initialize the transformer"""
        self.logger = setup_logger()

    def extract_downloads(self, resource_data: Dict) -> int:
        """Extract download count from resource data"""
        return resource_data.get("stats", {}).get("downloads", 0)

    def extract_dates(self, resource_data: Dict) -> Tuple[str, str]:
        """Extract creation and update dates from resource data"""
        created_at = resource_data.get("createdAt", datetime.now().isoformat())
        updated_at = resource_data.get("lastUpdated", created_at)
        return created_at, updated_at

    def map_resource_type(self, resource_type: str) -> str:
        """Map platform-specific resource type to standard type"""
        return "plugin"  # Hangar 平台只有 plugin 類型

    def get_resource_url(self, resource_id: str, author: str) -> str:
        """Generate resource URL"""
        return f"https://hangar.papermc.io/{author}/{resource_id}"

    def calculate_popularity(self, resource_data: Dict) -> float:
        """Calculate resource popularity score"""
        # Hangar 的熱門度計算：
        # - 下載數的權重最高
        # - 最近的下載數提供額外加分
        # - 星星數和關注者數也很重要
        # - 最近的瀏覽數提供少量加分
        stats = resource_data.get("stats", {})
        downloads = stats.get("downloads", 0)
        recent_downloads = stats.get("recentDownloads", 0)
        stars = stats.get("stars", 0)
        watchers = stats.get("watchers", 0)
        recent_views = stats.get("recentViews", 0)
        
        # 將下載數標準化（每 1000 下載為 1 分）
        download_score = downloads / 1000
        
        # 最近下載數的權重較高（每 100 下載為 1 分）
        recent_download_score = recent_downloads / 100
        
        # 星星數和關注者數的權重相同（每個值 100 分）
        engagement_score = (stars + watchers) * 100
        
        # 最近瀏覽數的權重較小（每 1000 瀏覽為 1 分）
        recent_view_score = recent_views / 1000
        
        return download_score + recent_download_score + engagement_score + recent_view_score

    def transform_resource(self, resource_data: Dict) -> Dict:
        """Transform platform-specific resource data to standard format"""
        created_at, updated_at = self.extract_dates(resource_data)
        resource_id = str(resource_data.get("id", "unknown"))
        author = resource_data.get("namespace", {}).get("owner", "Unknown")
        
        return {
            "id": resource_id,
            "name": resource_data.get("name", "Unknown"),
            "description": resource_data.get("description", ""),
            "author": author,
            "downloads": self.extract_downloads(resource_data),
            "created_at": created_at,
            "updated_at": updated_at,
            "resource_type": self.map_resource_type(""),
            "version": "latest",  # Hangar 的版本資訊需要另外獲取
            "game_version": ["unknown"],  # Hangar 的遊戲版本資訊需要另外獲取
            "download_url": f"https://hangar.papermc.io/projects/{resource_id}/versions/latest/download",
            "rating": resource_data.get("stats", {}).get("stars", 0.0),
            "votes": resource_data.get("stats", {}).get("watchers", 0),
            "category": "popular",  # 目前固定使用 popular 類別
            "url": self.get_resource_url(resource_id, author),
            "popularity": self.calculate_popularity(resource_data)
        } 