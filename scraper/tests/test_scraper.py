"""爬蟲測試"""

import asyncio
import json
import unittest
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from unittest.mock import MagicMock

import jsonschema

from scraper.models.resource import Resource, ResourceCategory, VersionInfo, Source, Statistics
from scraper.contracts.transformer import TransformerContract
from scraper.scraper import ResourceScraper

class MockTransformer(TransformerContract):
    """模擬轉換器"""
    
    def get_resource_type(self) -> str:
        """Get resource type."""
        return "mod"
    
    def transform(self, data: Dict) -> Dict:
        """Transform raw data to standard format."""
        return {
            "id": self._extract_id(data),
            "name": self._extract_name(data),
            "description": self._extract_description(data),
            "author": self._extract_author(data),
            "downloads": self._extract_downloads(data),
            "created_at": self._extract_created_at(data),
            "updated_at": self._extract_updated_at(data),
            "resource_type": self.get_resource_type(),
            "version": "1.0.0",
            "game_version": [],
            "download_url": "",
            "rating": 0.0,
            "votes": 0,
            "category": "popular",
            "url": f"https://example.com/{data['id']}",
            "popularity": 0.0
        }
    
    def transform_base_fields(self, data: Dict) -> Dict:
        """Transform base fields."""
        return self.transform(data)
    
    def _extract_id(self, data: Dict) -> str:
        """Extract resource ID."""
        return data.get("id", "unknown")
    
    def _extract_name(self, data: Dict) -> str:
        """Extract resource name."""
        return data.get("name", "Unknown")
    
    def _extract_description(self, data: Dict) -> str:
        """Extract resource description."""
        return data.get("description", "")
    
    def _extract_author(self, data: Dict) -> str:
        """Extract resource author."""
        return data.get("author", "Unknown")
    
    def _extract_downloads(self, data: Dict) -> int:
        """Extract resource downloads."""
        return data.get("downloads", 0)
    
    def _extract_created_at(self, data: Dict) -> str:
        """Extract resource creation date."""
        return data.get("created_at", datetime.now().isoformat())
    
    def _extract_updated_at(self, data: Dict) -> str:
        """Extract resource update date."""
        return data.get("updated_at", datetime.now().isoformat())

def async_test(func):
    """非同步測試裝飾器"""
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))
    return wrapper

class TestResourceScraper(unittest.TestCase):
    """資源爬蟲測試"""
    
    def setUp(self):
        """測試前準備"""
        self.scraper = ResourceScraper()
        self.test_data_dir = Path(__file__).parent / "data"
        self.test_data_dir.mkdir(parents=True, exist_ok=True)
        
        # 設定模擬客戶端和轉換器
        mock_client = MagicMock()
        mock_client.platform_name = "mock"
        self.scraper.fetcher.clients = [(mock_client, MockTransformer())]
    
    def tearDown(self):
        """測試後清理"""
        # 清理測試產生的檔案
        for file in self.test_data_dir.glob("*.json"):
            file.unlink()
    
    def test_schema_validation(self):
        """測試 schema 驗證"""
        # 準備測試資料
        test_data = {
            "id": "test/test",
            "name": "Test Resource",
            "description": "Test Description",
            "author": "Test Author",
            "downloads": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "resource_type": "mod",
            "category": "new"
        }
        
        # 驗證資料格式
        try:
            jsonschema.validate(instance=test_data, schema=self.scraper.normalizer.validator.schemas["resource"])
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"Schema 驗證失敗: {str(e)}")
    
    def test_normalize_results(self):
        """測試資料正規化"""
        # 準備測試資料
        raw_results = {
            "mock": {
                "hits": [{
                    "id": "test/test",
                    "name": "Test Resource",
                    "description": "Test Description",
                    "author": "Test Author",
                    "downloads": 0,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }]
            }
        }
        
        # 設定模擬轉換器
        mock_client = MagicMock()
        mock_client.platform_name = "mock"
        self.scraper.fetcher.clients = [(mock_client, MockTransformer())]
        
        # 執行正規化
        normalized = self.scraper.normalizer.normalize_results(raw_results)
        
        # 驗證結果
        self.assertIn("mock", normalized)
        self.assertIn("popular", normalized["mock"])
        for resource in normalized["mock"]["popular"]:
            self.assertIsInstance(resource, Resource)
    
    def test_aggregate_results(self):
        """測試資料整合"""
        # 準備測試資料
        normalized_results = {
            "platform1": {
                "popular": [Resource(
                    id="test1/test1",
                    name="Test Resource 1",
                    type="mod",
                    version=VersionInfo(
                        version="1.0.0",
                        game_version=[],
                        download_url="",
                        dependencies=[]
                    ),
                    sources=[Source(
                        platform="platform1",
                        url="https://example.com/test1",
                        external_id="test1"
                    )],
                    description="Test Description",
                    authors=["Test Author"],
                    stats=Statistics(downloads=100),
                    category=ResourceCategory.POPULAR,
                    popularity=100.0
                )]
            },
            "platform2": {
                "popular": [Resource(
                    id="test2/test2",
                    name="Test Resource 2",
                    type="mod",
                    version=VersionInfo(
                        version="1.0.0",
                        game_version=[],
                        download_url="",
                        dependencies=[]
                    ),
                    sources=[Source(
                        platform="platform2",
                        url="https://example.com/test2",
                        external_id="test2"
                    )],
                    description="Test Description",
                    authors=["Test Author"],
                    stats=Statistics(downloads=200),
                    category=ResourceCategory.POPULAR,
                    popularity=200.0
                )]
            }
        }
        
        # 執行整合
        aggregated = self.scraper.aggregator.aggregate_results(normalized_results)
        
        # 驗證結果
        self.assertIn("platform1", aggregated)
        self.assertIn("platform2", aggregated)
        self.assertEqual(len(aggregated["platform1"]["popular"]), 1)
        self.assertEqual(len(aggregated["platform2"]["popular"]), 1)

class TestResourceScraperAsync(unittest.TestCase):
    """資源爬蟲非同步測試"""
    
    def setUp(self):
        """測試前準備"""
        self.scraper = ResourceScraper()
        self.test_data_dir = Path(__file__).parent / "data"
        self.test_data_dir.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """測試後清理"""
        # 清理測試產生的檔案
        for file in self.test_data_dir.glob("*.json"):
            file.unlink()
    
    @async_test
    async def test_fetch_resources(self):
        """測試資源獲取"""
        # 建立客戶端
        mock_results = {
            "modrinth": {
                "hits": [],
                "total_hits": 0
            },
            "hangar": {
                "result": [],
                "pagination": {"count": 0}
            }
        }
        
        # 建立模擬的 fetcher
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_all_resources = MagicMock(return_value=mock_results)
        mock_fetcher.fetch_all_resources.return_value = asyncio.Future()
        mock_fetcher.fetch_all_resources.return_value.set_result(mock_results)
        
        mock_fetcher.cleanup = MagicMock()
        mock_fetcher.cleanup.return_value = asyncio.Future()
        mock_fetcher.cleanup.return_value.set_result(None)
        
        self.scraper.fetcher = mock_fetcher
        
        try:
            # 執行獲取
            results = await self.scraper.run()
            
            # 驗證結果
            self.assertIsInstance(results, dict)
            for platform, data in results.items():
                self.assertIsInstance(platform, str)
                self.assertIsInstance(data, dict)
                # 檢查 API 回應的基本結構
                if platform == "modrinth":
                    self.assertIn("hits", data)
                    self.assertIn("total_hits", data)
                    self.assertIsInstance(data["hits"], list)
                elif platform == "hangar":
                    self.assertIn("result", data)
                    self.assertIn("pagination", data)
                    self.assertIsInstance(data["result"], list)
        finally:
            # 確保清理資源
            await self.scraper.cleanup()

if __name__ == "__main__":
    unittest.main() 