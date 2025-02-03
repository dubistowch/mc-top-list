"""
JSON file storage implementation
"""

import json
import logging
from typing import Dict, List, Any, Union
from datetime import datetime, timedelta
from pathlib import Path

from .base import BaseStorage
from ...models.resource import Resource
from ...config import get_config

logger = logging.getLogger(__name__)

class JsonStorage(BaseStorage):
    """Storage implementation using JSON files"""
    
    def __init__(self, base_dir: Path = None):
        """
        Initialize storage with base directory
        
        Args:
            base_dir: Base directory for data storage
        """
        super().__init__(base_dir)
        self.config = get_config()
    
    async def save_raw_data(self, data: Dict[str, Any], timestamp: datetime) -> None:
        """
        Save raw API response data as JSON
        
        Args:
            data: Raw data from API
            timestamp: Data collection timestamp
        """
        try:
            # Create timestamp directory
            timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
            timestamp_dir = self.base_dir / "data" / "raw" / timestamp_str
            timestamp_dir.mkdir(parents=True, exist_ok=True)
            
            # Get platforms that support multiple resource types
            multi_type_platforms = [
                platform for platform, config in self.config.get("platforms", {}).items()
                if "resource_types" in config
            ]
            
            for platform, platform_data in data.items():
                if platform in multi_type_platforms:
                    # For platforms that support multiple resource types
                    for resource_type, type_data in platform_data.items():
                        file_path = timestamp_dir / f"{platform}_{resource_type}_raw.json"
                        logger.info("Saving raw data for %s %s to %s", platform, resource_type, file_path)
                        with open(file_path, "w", encoding="utf-8") as f:
                            json.dump(type_data, f, indent=2, ensure_ascii=False)
                else:
                    # For platforms with single resource type (like Hangar)
                    # Extract the result data and save it with the resource type
                    if platform == "hangar":
                        result_data = platform_data.get("result", [])
                        file_path = timestamp_dir / f"{platform}_plugin_raw.json"
                        logger.info("Saving raw data for %s to %s", platform, file_path)
                        with open(file_path, "w", encoding="utf-8") as f:
                            json.dump({"result": result_data}, f, indent=2, ensure_ascii=False)
                    else:
                        # For other single type platforms
                        file_path = timestamp_dir / f"{platform}_raw.json"
                        logger.info("Saving raw data for %s to %s", platform, file_path)
                        with open(file_path, "w", encoding="utf-8") as f:
                            json.dump(platform_data, f, indent=2, ensure_ascii=False)
                    
        except Exception as e:
            logger.error("Failed to save raw data: %s", str(e))
            raise
    
    async def save_processed_data(self, resources: Dict[str, List[Resource]], timestamp: datetime) -> None:
        """
        Save processed resource data as JSON
        
        Args:
            resources: Processed resources by platform
            timestamp: Data collection timestamp
        """
        try:
            # Create timestamp directory
            timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
            timestamp_dir = self.base_dir / "data" / "processed" / timestamp_str
            timestamp_dir.mkdir(parents=True, exist_ok=True)
            
            for platform, platform_resources in resources.items():
                file_path = timestamp_dir / f"{platform}_processed.json"
                
                # Group resources by type
                grouped_resources = {}
                for resource in platform_resources:
                    resource_dict = resource.to_dict()
                    resource_type = resource_dict.pop("resource_type")  # 移除並取得 resource_type
                    if resource_type not in grouped_resources:
                        grouped_resources[resource_type] = []
                    grouped_resources[resource_type].append(resource_dict)
                
                logger.info("Saving processed data for %s to %s", platform, file_path)
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "timestamp": timestamp.isoformat(),
                        "platform": platform,
                        "resources": grouped_resources
                    }, f, indent=2, ensure_ascii=False)
                    
        except Exception as e:
            logger.error("Failed to save processed data: %s", str(e))
            raise
    
    def _parse_resource(self, data: Dict) -> Resource:
        """
        Parse resource data from JSON.
        
        Args:
            data: Raw resource data
            
        Returns:
            Resource object
        """
        # Convert datetime strings to datetime objects
        if "created_at" in data:
            data["created_at"] = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        if "updated_at" in data:
            data["updated_at"] = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
            
        return Resource(**data)
    
    def load_processed_data(self, timestamp: str, platform: str) -> List[Resource]:
        """
        Load processed data for a platform.
        
        Args:
            timestamp: Data timestamp
            platform: Platform name
            
        Returns:
            List of Resource objects
        """
        file_path = self.base_dir / "data" / "processed" / timestamp / f"{platform}_processed.json"
        if not file_path.exists():
            return []
            
        with open(file_path) as f:
            data = json.load(f)
            resources = []
            for resource_type, type_resources in data.get("resources", {}).items():
                for resource in type_resources:
                    # 加回 resource_type
                    resource["resource_type"] = resource_type
                    resources.append(self._parse_resource(resource))
            return resources
    
    def save_aggregated_data(self, timestamp: str, data: Dict) -> None:
        """
        Save aggregated data.
        
        Args:
            timestamp: Data timestamp
            data: Aggregated data to save
        """
        # Create directory if not exists
        output_dir = self.base_dir / "data" / "aggregated" / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save aggregated data
        output_file = output_dir / "aggregated.json"
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2, default=str)
    
    async def save_daily_stats(self, stats: Dict[str, Any], date: datetime) -> None:
        """
        Save daily resource statistics
        
        Args:
            stats: Daily resource statistics
            date: Statistics date
        """
        try:
            # 建立日期目錄結構
            history_dir = self.base_dir / "data" / "history" / str(date.year) / f"{date.month:02d}"
            history_dir.mkdir(parents=True, exist_ok=True)
            
            # 儲存每日統計
            daily_file = history_dir / f"{date.day:02d}.json"
            with open(daily_file, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            
            # 更新最新快照
            latest_file = self.base_dir / "data" / "history" / "latest.json"
            with open(latest_file, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error("Failed to save daily stats: %s", str(e))
            raise
            
    async def save_weekly_stats(self, stats: Dict[str, Any], date: datetime) -> None:
        """
        Save weekly resource statistics
        
        Args:
            stats: Weekly resource statistics
            date: Statistics date
        """
        try:
            # 建立週統計目錄
            week_number = date.isocalendar()[1]
            weekly_dir = self.base_dir / "data" / "history" / str(date.year) / "weekly"
            weekly_dir.mkdir(parents=True, exist_ok=True)
            
            # 儲存週統計
            weekly_file = weekly_dir / f"{week_number:02d}.json"
            with open(weekly_file, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error("Failed to save weekly stats: %s", str(e))
            raise
            
    def get_daily_stats(self, date: datetime) -> Dict[str, Any]:
        """
        Get daily resource statistics
        
        Args:
            date: Statistics date
            
        Returns:
            Daily resource statistics
        """
        try:
            daily_file = (self.base_dir / "data" / "history" / 
                         str(date.year) / f"{date.month:02d}" / f"{date.day:02d}.json")
            
            if not daily_file.exists():
                return {}
                
            with open(daily_file, "r", encoding="utf-8") as f:
                return json.load(f)
                
        except Exception as e:
            logger.error("Failed to get daily stats: %s", str(e))
            return {}
            
    def get_weekly_stats(self, date: datetime) -> Dict[str, Any]:
        """
        Get weekly resource statistics
        
        Args:
            date: Any date in the target week
            
        Returns:
            Weekly resource statistics
        """
        try:
            week_number = date.isocalendar()[1]
            weekly_file = (self.base_dir / "data" / "history" / 
                          str(date.year) / "weekly" / f"{week_number:02d}.json")
            
            if not weekly_file.exists():
                return {}
                
            with open(weekly_file, "r", encoding="utf-8") as f:
                return json.load(f)
                
        except Exception as e:
            logger.error("Failed to get weekly stats: %s", str(e))
            return {}
            
    def cleanup_old_data(self, months: int = 3) -> None:
        """
        Clean up old history data
        
        Args:
            months: Number of months to keep
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=months * 30)
            history_dir = self.base_dir / "data" / "history"
            
            if not history_dir.exists():
                return
                
            for year_dir in history_dir.iterdir():
                if not year_dir.is_dir() or year_dir.name == "latest":
                    continue
                    
                year = int(year_dir.name)
                for month_dir in year_dir.iterdir():
                    if not month_dir.is_dir() or month_dir.name == "weekly":
                        continue
                        
                    month = int(month_dir.name)
                    dir_date = datetime(year, month, 1)
                    
                    if dir_date < cutoff_date:
                        logger.info("Cleaning up old data: %s", month_dir)
                        for file in month_dir.iterdir():
                            file.unlink()
                        month_dir.rmdir()
                        
                if not any(year_dir.iterdir()):
                    year_dir.rmdir()
                    
        except Exception as e:
            logger.error("Failed to clean up old data: %s", str(e))
            
    def verify_data_integrity(self) -> bool:
        """
        Verify data integrity
        
        Returns:
            True if data is valid, False otherwise
        """
        try:
            history_dir = self.base_dir / "data" / "history"
            latest_file = history_dir / "latest.json"
            
            # 檢查最新快照
            if not latest_file.exists():
                logger.error("Latest snapshot not found")
                return False
                
            # 讀取並驗證最新快照
            with open(latest_file, "r", encoding="utf-8") as f:
                latest_data = json.load(f)
                
            if "resource_stats" not in latest_data:
                logger.error("Invalid latest snapshot format")
                return False
                
            # 驗證資源統計資料
            for resource_id, stats in latest_data["resource_stats"].items():
                if "daily_stats" not in stats or "metadata" not in stats:
                    logger.error("Invalid resource stats format: %s", resource_id)
                    return False
                    
            return True
            
        except Exception as e:
            logger.error("Data integrity check failed: %s", str(e))
            return False 