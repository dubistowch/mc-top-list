"""
Handles persistence of resource data in different stages (raw, normalized, aggregated).
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from scraper.models.resource import Resource
from scraper.utils.logger import setup_logger
from scraper.utils.paths import RAW_DIR, NORMALIZED_DIR, AGGREGATED_DIR


class ResultPersistence:
    """Handles saving and loading of resource data"""

    def __init__(self):
        """Initialize the persistence handler"""
        self.logger = setup_logger()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.raw_dir = Path(RAW_DIR)
        self.normalized_dir = Path(NORMALIZED_DIR)
        self.aggregated_dir = Path(AGGREGATED_DIR)

    async def save_raw_results(
        self, results: Dict[str, Dict]
    ) -> None:
        """
        Save raw results from API calls, preserving the exact API response format
        
        Args:
            results: Raw API responses organized by platform
        """
        raw_dir = self.raw_dir / self.timestamp
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        for platform, raw_data in results.items():
            output_file = raw_dir / f"{platform}_raw.json"
            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(raw_data, f, indent=2, ensure_ascii=False)
                self.logger.info(f"Saved raw results for {platform}")
            except Exception as e:
                self.logger.error(f"Failed to save raw results for {platform}: {e}")
                raise

    async def save_normalized_results(
        self, results: Dict[str, Dict[str, List[Resource]]]
    ) -> None:
        """
        Save normalized results
        
        Args:
            results: Normalized results organized by platform and category
        """
        normalized_dir = self.normalized_dir / self.timestamp
        normalized_dir.mkdir(parents=True, exist_ok=True)
        
        for platform, categories in results.items():
            output_file = normalized_dir / f"{platform}_normalized.json"
            try:
                serialized = {
                    cat: [r.to_dict() for r in resources]
                    for cat, resources in categories.items()
                }
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(serialized, f, indent=2, ensure_ascii=False)
                self.logger.info(f"Saved normalized results for {platform}")
            except Exception as e:
                self.logger.error(f"Failed to save normalized results for {platform}: {e}")
                raise

    async def save_aggregated_results(
        self, results: Dict[str, Dict[str, List[Resource]]]
    ) -> None:
        """
        Save aggregated results
        
        Args:
            results: Aggregated results organized by platform and category
        """
        output_file = self.aggregated_dir / f"aggregated_{self.timestamp}.json"
        
        try:
            serialized = {
                platform: {
                    cat: [r.to_dict() for r in resources]
                    for cat, resources in categories.items()
                }
                for platform, categories in results.items()
            }
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(serialized, f, indent=2, ensure_ascii=False)
            self.logger.info("Saved aggregated results")
        except Exception as e:
            self.logger.error(f"Failed to save aggregated results: {e}")
            raise 