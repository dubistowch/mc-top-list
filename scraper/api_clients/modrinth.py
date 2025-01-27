"""Modrinth API 客戶端實現"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta

from interfaces.api_client import APIClient
from models.resource import Resource, VersionInfo, Statistics, Source

PLATFORM = "modrinth"
BASE_URL = "https://api.modrinth.com/v2"
DEFAULT_LIMIT = 50

class ModrinthClient(APIClient[Dict]):
    """Modrinth API 客戶端"""
    
    def __init__(self, api_key: Optional[str] = None):
        """初始化 Modrinth 客戶端"""
        super().__init__()
        if api_key:
            self.headers["Authorization"] = api_key
    
    def _get_base_url(self) -> str:
        return BASE_URL
    
    async def fetch_resources(self, category: str = "all") -> List[Resource]:
        """獲取資源列表"""
        params = {
            "limit": DEFAULT_LIMIT,
            "index": "newest" if category == "new" else "downloads" if category == "popular" else "relevance"
        }
        data = await self._request("GET", "search", params=params)
        return [self._convert_to_resource(item, category) for item in data["hits"]]
    
    async def get_project(self, project_id: str) -> Resource:
        """獲取特定專案"""
        data = await self._request("GET", f"project/{project_id}")
        return self._convert_to_resource(data)
    
    async def fetch_new_resources(self, days: int = 7) -> List[Resource]:
        """獲取最近發布的資源"""
        params = self._create_time_range_params(days, "newest")
        data = await self._request("GET", "search", params=params)
        return [self._convert_to_resource(item, "new") for item in data["hits"]]
    
    async def fetch_popular_resources(self, days: int = 7) -> List[Resource]:
        """獲取最受歡迎的資源"""
        params = self._create_time_range_params(days, "downloads")
        data = await self._request("GET", "search", params=params)
        return [self._convert_to_resource(item, "popular") for item in data["hits"]]
    
    def _create_time_range_params(self, days: int, index: str) -> Dict:
        """創建時間範圍查詢參數"""
        timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
        return {
            "limit": DEFAULT_LIMIT,
            "index": index,
            "facets": f'[["created_timestamp>={timestamp}"]]'
        }
    
    def _convert_to_resource(self, data: Dict, category: str = "all") -> Resource:
        """轉換數據格式"""
        project_id = data["project_id"]
        return Resource(
            id=project_id,
            name=data["title"],
            type="mod" if data.get("project_type") == "mod" else "plugin",
            version=VersionInfo(
                latest=data.get("latest_version", "unknown"),
                game_versions=data.get("game_versions", [])
            ),
            sources=[Source(
                platform=PLATFORM,
                url=f"https://modrinth.com/project/{project_id}",
                external_id=project_id
            )],
            description=data.get("description", ""),
            authors=data.get("author", []),
            stats=Statistics(
                downloads=data.get("downloads", 0),
                rating=data.get("rating", 0.0),
                votes=data.get("number_of_votes", 0)
            ),
            category=category
        )
