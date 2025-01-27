"""
Handles fetching resources from different platforms.
"""

from typing import Dict, List, Tuple

from scraper.contracts.api_client import APIClientContract
from scraper.contracts.transformer import TransformerContract
from scraper.models.resource import ResourceCategory
from scraper.platforms.modrinth import ModrinthClient
from scraper.platforms.hangar import HangarClient
from scraper.platforms.hangar.transformers import HangarPluginTransformer
from scraper.platforms.modrinth.transformers import (
    ModrinthModTransformer,
    ModrinthModpackTransformer,
    ModrinthResourcePackTransformer
)
from scraper.utils.api_key_manager import APIKeyManager
from scraper.utils.logger import setup_logger


class ResourceFetcher:
    """Handles fetching resources from different platforms"""

    def __init__(self):
        """Initialize the resource fetcher"""
        self.logger = setup_logger()
        self.key_manager = APIKeyManager()
        self.clients = self._create_clients()

    def _create_clients(self) -> List[Tuple[APIClientContract, TransformerContract]]:
        """Create API clients and their corresponding transformers"""
        modrinth_client = ModrinthClient(self.key_manager.get_key("modrinth"))
        hangar_client = HangarClient(self.key_manager.get_key("hangar"))

        return [
            (modrinth_client, ModrinthModTransformer()),
            (modrinth_client, ModrinthModpackTransformer()),
            (modrinth_client, ModrinthResourcePackTransformer()),
            (hangar_client, HangarPluginTransformer())
        ]

    async def fetch_all_resources(self) -> Dict[str, Dict]:
        """
        Fetch raw resources from all platforms
        
        Returns:
            Dict mapping platform names to their raw API responses
        """
        results: Dict[str, Dict] = {}
        
        # Track unique clients to avoid duplicate calls
        processed_clients = set()
        
        for client, _ in self.clients:
            platform = client.platform_name
            
            # Skip if we've already processed this client
            if client in processed_clients:
                continue
                
            processed_clients.add(client)
            
            try:
                raw_data = await client.fetch_resources()
                results[platform] = raw_data
                self.logger.info(f"Fetched raw data from {platform}")
            except Exception as e:
                self.logger.error(f"Error fetching from {platform}: {e}")
                raise

        return results 

    async def cleanup(self):
        """Clean up resources and close client connections"""
        # Track unique clients to avoid duplicate cleanup
        processed_clients = set()
        
        for client, _ in self.clients:
            if client in processed_clients:
                continue
                
            processed_clients.add(client)
            
            try:
                await client.close()
                self.logger.info(f"Closed connection for {client.platform_name}")
            except Exception as e:
                self.logger.error(f"Error closing connection for {client.platform_name}: {e}")
                raise 