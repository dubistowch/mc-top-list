"""
Minecraft Resource Scraper Service

Handles the core business logic for fetching and processing Minecraft resources
from various platforms.
"""

from typing import Dict, List, Optional, TypedDict
import asyncio
import structlog
from datetime import datetime
from pathlib import Path

from scraper.clients.client_factory import ClientFactory, BaseClient
from scraper.clients.modrinth import ModrinthClient
from scraper.clients.hangar import HangarClient
from scraper.models.resource import Resource
from scraper.models.platform import Platform
from scraper.services.transformers.modrinth import ModrinthTransformer
from scraper.services.transformers.hangar import HangarTransformer
from scraper.services.storage.json_storage import JsonStorage
from scraper.services.aggregator import ResourceAggregator

# Initialize structured logging
logger = structlog.get_logger(__name__)

class ResourceData(TypedDict):
    """Type definition for resource data"""
    raw: Dict
    processed: List[Resource]

class ScraperError(Exception):
    """Base exception for scraper service"""
    pass

class ResourceFetchError(ScraperError):
    """Error when fetching resources fails"""
    pass

class ResourceProcessingError(ScraperError):
    """Error when processing resources fails"""
    pass

class StorageError(ScraperError):
    """Error when storing data fails"""
    pass

class ScraperService:
    """Core service for resource scraping operations"""
    
    def __init__(self, storage_dir: Optional[Path] = None) -> None:
        """
        Initialize the scraper service
        
        Args:
            storage_dir: Base directory for data storage
        """
        self.base_dir = storage_dir or Path(__file__).parent.parent.parent
        self.client_factory = ClientFactory()
        self._register_clients()
        self._init_transformers()
        self._init_storage()
        
    def _register_clients(self) -> None:
        """Register platform-specific API clients"""
        self.client_factory.register("modrinth", ModrinthClient)
        self.client_factory.register("hangar", HangarClient)
        
    def _init_transformers(self) -> None:
        """Initialize platform-specific transformers"""
        self.transformers = {
            "modrinth": ModrinthTransformer(),
            "hangar": HangarTransformer()
        }
        
    def _init_storage(self) -> None:
        """Initialize storage service"""
        try:
            self.storage = JsonStorage(base_dir=self.base_dir)
            self.aggregator = ResourceAggregator(storage=self.storage)
        except Exception as e:
            raise StorageError(f"Failed to initialize storage: {str(e)}")
        
    async def fetch_resources(self, platform: str) -> Dict:
        """
        Fetch resources from specified platform
        
        Args:
            platform: Platform identifier (e.g., 'modrinth', 'hangar')
            
        Returns:
            Dict containing fetched resources
            
        Raises:
            ResourceFetchError: If fetching resources fails
        """
        try:
            client: BaseClient = self.client_factory.create(platform)
            logger.info("fetching_resources", platform=platform)
            return await client.fetch_resources()
        except Exception as e:
            logger.error("resource_fetch_failed", platform=platform, error=str(e))
            raise ResourceFetchError(f"Failed to fetch resources from {platform}: {str(e)}")

    async def process_platform(self, platform: Platform) -> Optional[List[Resource]]:
        """
        Process resources for a single platform
        
        Args:
            platform: Platform configuration object
            
        Returns:
            List of processed Resource objects
            
        Raises:
            ResourceProcessingError: If processing resources fails
        """
        try:
            raw_data = await self.fetch_resources(platform.name)
            transformer = self.transformers.get(platform.name)
            if not transformer:
                logger.error("no_transformer_found", platform=platform.name)
                raise ResourceProcessingError(f"No transformer found for platform: {platform.name}")
                
            resources = transformer.transform(raw_data)
            logger.info("platform_processing_success", 
                       platform=platform.name, 
                       resource_count=len(resources))
            return resources
        except ResourceFetchError as e:
            raise
        except Exception as e:
            logger.error("platform_processing_failed", 
                        platform=platform.name, 
                        error=str(e))
            raise ResourceProcessingError(f"Failed to process platform {platform.name}: {str(e)}")

    async def run(self) -> Dict[str, List[Resource]]:
        """
        Execute the complete scraping process
        
        Returns:
            Dict mapping platform names to lists of Resource objects
            
        Raises:
            ScraperError: If the scraping process fails
        """
        timestamp = datetime.now()
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        raw_results: Dict[str, Dict] = {}
        processed_results: Dict[str, List[Resource]] = {}
        
        platforms = [
            Platform(name="modrinth", batch_size=100),
            Platform(name="hangar", batch_size=50)
        ]
        
        try:
            # 抓取和處理資料
            for platform in platforms:
                # Fetch and store raw data
                raw_data = await self.fetch_resources(platform.name)
                raw_results[platform.name] = raw_data
                
                # Process and store transformed data
                resources = await self.process_platform(platform)
                if resources:
                    processed_results[platform.name] = resources
            
            # 儲存原始和處理後的資料
            await self.storage.save_raw_data(raw_results, timestamp)
            await self.storage.save_processed_data(processed_results, timestamp)
            
            # 執行資料聚合
            aggregated_result = self.aggregator.aggregate(timestamp_str)
            
            # 輸出聚合結果
            print("\n=== 聚合結果 ===")
            print(f"總資源數: {aggregated_result['metadata']['total_resources']}")
            print(f"平台: {aggregated_result['metadata']['platforms']}")
            
            print("\n資源統計:")
            for tab in aggregated_result['resources']['tabs']:
                res_type = tab['id']
                categories = aggregated_result['resources']['resources'].get(res_type, {})
                if categories:
                    print(f"\n{tab['label']}:")
                    for category, resources in categories.items():
                        print(f"  {category}: {len(resources)} 個資源")
            
            logger.info("scraping_completed", 
                       platform_count=len(platforms),
                       total_resources=aggregated_result['metadata']['total_resources'])
            
            return processed_results
            
        except (ResourceFetchError, ResourceProcessingError, StorageError) as e:
            raise
        except Exception as e:
            logger.error("scraping_process_failed", error=str(e))
            raise ScraperError(f"Scraping process failed: {str(e)}")

async def main() -> Dict[str, List[Resource]]:
    """
    Service entry point
    
    Returns:
        Dict mapping platform names to lists of Resource objects
        
    Raises:
        ScraperError: If service execution fails
    """
    service = ScraperService()
    try:
        return await service.run()
    except Exception as e:
        logger.error("service_execution_failed", error=str(e))
        raise

if __name__ == "__main__":
    asyncio.run(main()) 