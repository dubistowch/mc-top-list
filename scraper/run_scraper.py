"""Minecraft 資源爬蟲主程序"""

import asyncio
import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

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
        self.data_dir.mkdir(exist_ok=True)
    
    async def run(self):
        """執行爬蟲"""
        self.logger.info("開始執行爬蟲")
        try:
            clients = self._create_clients()
            results = await self._fetch_all_resources(clients)
            await self._save_results(results)
            self.logger.info("爬蟲執行完成")
        except Exception as e:
            self.logger.error(f"執行失敗: {str(e)}")
            raise
    
    def _create_clients(self) -> List[ModrinthClient]:
        """創建 API 客戶端"""
        return [
            ModrinthClient(api_key=self.key_manager.get_key("modrinth")),
            # 未來可添加其他平台的客戶端
        ]
    
    async def _fetch_all_resources(
        self, clients: List[ModrinthClient]
    ) -> Dict[ResourceCategory, List[Resource]]:
        """獲取所有資源"""
        categories: List[ResourceCategory] = ["new", "popular", "all"]
        results: Dict[ResourceCategory, List[Resource]] = {
            category: [] for category in categories
        }
        
        for client in clients:
            client_name = client.__class__.__name__
            for category in categories:
                try:
                    resources = await client.fetch_resources(category)
                    results[category].extend(resources)
                    self.logger.info(
                        f"從 {client_name} 獲取 {category} 資源: {len(resources)} 個"
                    )
                except Exception as e:
                    self.logger.error(
                        f"從 {client_name} 獲取 {category} 資源失敗: {str(e)}"
                    )
        
        return results
    
    async def _save_results(
        self, results: Dict[ResourceCategory, List[Resource]]
    ) -> None:
        """保存結果"""
        for category, resources in results.items():
            if not resources:
                continue
                
            output_file = self.data_dir / f"minecraft_{category}_resources.json"
            data = {
                "total": len(resources),
                "category": category,
                "last_updated": datetime.now().isoformat(),
                "items": [asdict(r) for r in resources]
            }
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            self.logger.info(f"保存 {category} 類別資源: {len(resources)} 個")

async def main():
    """主程序入口"""
    scraper = ResourceScraper()
    await scraper.run()

if __name__ == "__main__":
    asyncio.run(main())
