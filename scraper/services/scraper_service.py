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
        self.client_factory = ClientFactory()
        self._register_clients()
        self._init_transformers()
        self._init_storage(storage_dir or Path("data"))
        
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
        
    def _init_storage(self, base_dir: Path) -> None:
        """
        Initialize storage service
        
        Args:
            base_dir: Base directory for data storage
        """
        try:
            raw_dir = base_dir / "raw"
            processed_dir = base_dir / "processed"
            
            self.raw_storage = JsonStorage(raw_dir)
            self.processed_storage = JsonStorage(processed_dir)
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
        raw_results: Dict[str, Dict] = {}
        processed_results: Dict[str, List[Resource]] = {}
        
        platforms = [
            Platform(name="modrinth", batch_size=100),
            Platform(name="hangar", batch_size=50)
        ]
        
        try:
            for platform in platforms:
                # Fetch and store raw data
                raw_data = await self.fetch_resources(platform.name)
                raw_results[platform.name] = raw_data
                
                # Process and store transformed data
                resources = await self.process_platform(platform)
                if resources:
                    processed_results[platform.name] = resources
            
            # Save both raw and processed data
            await self.raw_storage.save_raw_data(raw_results, timestamp)
            await self.processed_storage.save_processed_data(processed_results, timestamp)
            
            logger.info("scraping_completed", platform_count=len(platforms))
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