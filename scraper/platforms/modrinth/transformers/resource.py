"""Modrinth resource transformer implementation."""

from typing import Dict, Tuple
from datetime import datetime

from scraper.contracts.transformer import ResourceTransformerContract
from scraper.utils.logger import setup_logger


class ModrinthResourceTransformer(ResourceTransformerContract):
    """Modrinth resource transformer"""

    def __init__(self):
        """Initialize the transformer"""
        self.logger = setup_logger()

    def extract_downloads(self, resource_data: Dict) -> int:
        """Extract download count from resource data"""
        downloads = resource_data.get("downloads", 0)
        if downloads == 0:
            downloads = resource_data.get("stats", {}).get("downloads", 0)
        if downloads == 0:
            downloads = sum(
                version.get("downloads", 0)
                for version in resource_data.get("versions", [])
            )
        return downloads

    def extract_dates(self, resource_data: Dict) -> Tuple[str, str]:
        """Extract creation and update dates from resource data"""
        created_at = (
            resource_data.get("published")
            or resource_data.get("date_created")
            or resource_data.get("created")
            or datetime.now().isoformat()
        )
        updated_at = (
            resource_data.get("updated")
            or resource_data.get("date_modified")
            or resource_data.get("modified")
            or created_at
        )
        return created_at, updated_at

    def map_resource_type(self, resource_type: str) -> str:
        """Map platform-specific resource type to standard type"""
        type_map = {
            "mod": "mod",
            "modpack": "modpack",
            "shader": "mod",  # shader 類型映射為 mod
            "resourcepack": "resource_pack",
            "plugin": "plugin"
        }
        return type_map.get(resource_type, "mod")

    def get_resource_url(self, resource_id: str, author: str) -> str:
        """Generate resource URL"""
        return f"https://modrinth.com/mod/{resource_id}"

    def calculate_popularity(self, resource_data: Dict) -> float:
        """Calculate resource popularity score"""
        # Modrinth 的熱門度計算：
        # - 下載數的權重最高
        # - 評分也很重要
        # - 關注數提供額外加分
        downloads = self.extract_downloads(resource_data)
        score = resource_data.get("score", 0.0)
        follows = resource_data.get("follows", 0)
        
        # 將下載數標準化（每 1000 下載為 1 分）
        download_score = downloads / 1000
        
        # 評分範圍是 0-5，乘以 1000 使其權重與下載數相當
        rating_score = score * 1000
        
        # 關注數的權重較小
        follow_score = follows * 10
        
        return download_score + rating_score + follow_score

    def transform_resource(self, resource_data: Dict) -> Dict:
        """Transform platform-specific resource data to standard format"""
        created_at, updated_at = self.extract_dates(resource_data)
        resource_id = resource_data.get("project_id", "unknown")
        author = resource_data.get("author", "Unknown")
        
        return {
            "id": resource_id,
            "name": resource_data.get("title", "Unknown"),
            "description": resource_data.get("description", ""),
            "author": author,
            "downloads": self.extract_downloads(resource_data),
            "created_at": created_at,
            "updated_at": updated_at,
            "resource_type": self.map_resource_type(
                resource_data.get("project_type", "mod")
            ),
            "version": resource_data.get("latest_version", ["latest"])[0],
            "game_version": resource_data.get("game_versions", ["unknown"]),
            "download_url": resource_data.get("files", [{}])[0].get("url", ""),
            "rating": resource_data.get("score", 0.0),
            "votes": resource_data.get("follows", 0),
            "category": "popular",  # 目前固定使用 popular 類別
            "url": self.get_resource_url(resource_id, author),
            "popularity": self.calculate_popularity(resource_data)
        } 