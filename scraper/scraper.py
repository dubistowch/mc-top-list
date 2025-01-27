"""
Minecraft Resource Scraper

A tool for fetching and aggregating Minecraft resources from various platforms.
Supports Hangar (plugins) and Modrinth (mods, modpacks, resource packs).

Usage:
    python -m scraper.scraper
"""

import asyncio

from scraper.core.resource_fetcher import ResourceFetcher
from scraper.core.resource_normalizer import ResourceNormalizer
from scraper.core.resource_aggregator import ResourceAggregator
from scraper.persistence.result_persistence import ResultPersistence
from scraper.utils.logger import setup_logger
from scraper.utils.paths import ensure_directories


class ResourceScraper:
    """Main scraper orchestrator"""

    def __init__(self):
        """Initialize the scraper components"""
        ensure_directories()
        self.logger = setup_logger()
        
        # Initialize components
        self.fetcher = ResourceFetcher()
        self.normalizer = ResourceNormalizer()
        self.aggregator = ResourceAggregator()
        self.persistence = ResultPersistence()

    async def cleanup(self):
        """Clean up resources"""
        try:
            await self.fetcher.cleanup()
            self.logger.info("Resources cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            raise

    async def run(self):
        """Run the complete scraping process"""
        try:
            # Fetch raw data
            self.logger.info("Starting resource fetch")
            raw_results = await self.fetcher.fetch_all_resources()
            
            # Save raw API responses
            self.logger.info("Saving raw API responses")
            await self.persistence.save_raw_results(raw_results)
            
            # Extract resources from raw responses for normalization
            self.logger.info("Extracting resources for normalization")
            resources_for_normalization = {}
            for platform, raw_data in raw_results.items():
                if platform == "modrinth":
                    resources_for_normalization[platform] = raw_data["hits"]
                elif platform == "hangar":
                    resources_for_normalization[platform] = raw_data["result"]
            
            # Normalize results
            self.logger.info("Normalizing results")
            normalized_results = self.normalizer.normalize_results(resources_for_normalization)
            await self.persistence.save_normalized_results(normalized_results)
            
            # Aggregate results
            self.logger.info("Aggregating results")
            aggregated_results = self.aggregator.aggregate_results(normalized_results)
            await self.persistence.save_aggregated_results(aggregated_results)
            
            self.logger.info("Scraping completed successfully")
            return raw_results
            
        except Exception as e:
            self.logger.error(f"Scraping failed: {e}")
            raise
        finally:
            await self.cleanup()


async def main():
    """Main entry point"""
    scraper = ResourceScraper()
    try:
        await scraper.run()
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 