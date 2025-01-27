"""Minecraft 資源爬蟲主程序"""

import asyncio
import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import jsonschema

from api_clients.modrinth import ModrinthClient
from models.resource import Resource, ResourceCategory
from utils.api_key_manager import APIKeyManager
from utils.logger import setup_logger

class ResourceScraper:
    """資源爬蟲器"""
    
    def __init__(self):
        """初始化爬蟲器"""
        self.logger = setup_logger()
        self.key_manager = APIKeyManager()
        self.data_dir = Path("data")
        self.raw_dir = self.data_dir / "raw"
        self.aggregated_dir = self.data_dir / "aggregated"
        self.schema_dir = self.data_dir / "schema"
        self.clients: List[ModrinthClient] = []
        
        # Create necessary directories
        for directory in [self.raw_dir, self.aggregated_dir, self.schema_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            
        # Load schema
        schema_file = self.schema_dir / "resource.json"
        with open(schema_file, "r", encoding="utf-8") as f:
            self.schema = json.load(f)
    
    async def run(self):
        """執行爬蟲"""
        self.logger.info("開始執行爬蟲")
        try:
            self.clients = self._create_clients()
            raw_results = await self._fetch_all_resources(self.clients)
            await self._save_raw_results(raw_results)
            aggregated_results = self._aggregate_results(raw_results)
            await self._save_aggregated_results(aggregated_results)
            self.logger.info("爬蟲執行完成")
        except Exception as e:
            self.logger.error(f"執行失敗: {str(e)}")
            raise
        finally:
            await self._cleanup()
    
    async def _cleanup(self):
        """清理資源"""
        for client in self.clients:
            await client.close()
    
    def _create_clients(self) -> List[ModrinthClient]:
        """創建 API 客戶端"""
        return [
            ModrinthClient(api_key=self.key_manager.get_key("modrinth")),
            # 未來可添加其他平台的客戶端
        ]
    
    async def _fetch_all_resources(
        self, clients: List[ModrinthClient]
    ) -> Dict[str, Dict[ResourceCategory, List[Resource]]]:
        """獲取所有資源"""
        categories: List[ResourceCategory] = ["new", "popular", "all"]
        results: Dict[str, Dict[ResourceCategory, List[Resource]]] = {}
        
        for client in clients:
            client_name = client.__class__.__name__.lower().replace("client", "")
            results[client_name] = {category: [] for category in categories}
            
            for category in categories:
                try:
                    resources = await client.fetch_resources(category)
                    results[client_name][category] = resources
                    self.logger.info(
                        f"從 {client_name} 獲取 {category} 資源: {len(resources)} 個"
                    )
                except Exception as e:
                    self.logger.error(
                        f"從 {client_name} 獲取 {category} 資源失敗: {str(e)}"
                    )
        
        return results
    
    async def _save_raw_results(
        self, results: Dict[str, Dict[ResourceCategory, List[Resource]]]
    ) -> None:
        """保存原始結果"""
        for site_name, categories in results.items():
            output_file = self.raw_dir / f"{site_name}.json"
            data = {
                "site": site_name,
                "last_updated": datetime.now().isoformat(),
                "categories": {
                    category: {
                        "total": len(resources),
                        "items": [r.to_dict() for r in resources]
                    }
                    for category, resources in categories.items()
                }
            }
            
            # Validate against schema
            try:
                jsonschema.validate(instance=data, schema=self.schema)
            except jsonschema.exceptions.ValidationError as e:
                self.logger.error(f"資料驗證失敗: {str(e)}")
                raise
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            self.logger.info(f"保存 {site_name} 原始資料完成")

    def _aggregate_results(
        self, raw_results: Dict[str, Dict[ResourceCategory, List[Resource]]]
    ) -> Dict[str, Dict[ResourceCategory, List[Resource]]]:
        """整合所有來源的資料"""
        # 使用與原始資料相同的格式，但合併所有來源
        aggregated = {
            "modrinth": {  # 暫時使用 modrinth 作為整合資料的站點名稱
                category: [] for category in ["new", "popular", "all"]
            }
        }
        
        for site_data in raw_results.values():
            for category, resources in site_data.items():
                aggregated["modrinth"][category].extend(resources)
        
        return aggregated

    async def _save_aggregated_results(
        self, results: Dict[str, Dict[ResourceCategory, List[Resource]]]
    ) -> None:
        """保存整合後的結果"""
        for site_name, categories in results.items():
            output_file = self.aggregated_dir / f"{site_name}_resources.json"
            data = {
                "site": site_name,
                "last_updated": datetime.now().isoformat(),
                "categories": {
                    category: {
                        "total": len(resources),
                        "items": [r.to_dict() for r in resources]
                    }
                    for category, resources in categories.items()
                }
            }
            
            # Validate against schema
            try:
                jsonschema.validate(instance=data, schema=self.schema)
            except jsonschema.exceptions.ValidationError as e:
                self.logger.error(f"資料驗證失敗: {str(e)}")
                raise
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            self.logger.info(f"保存整合後的 {site_name} 資源完成")

async def main():
    """主程序入口"""
    scraper = ResourceScraper()
    await scraper.run()

if __name__ == "__main__":
    asyncio.run(main())
