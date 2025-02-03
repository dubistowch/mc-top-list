"""Resource growth tracking service."""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import structlog
from pathlib import Path

from ..models.resource import Resource
from ..services.storage.json_storage import JsonStorage

logger = structlog.get_logger(__name__)

class GrowthTracker:
    """Service for tracking resource growth."""
    
    def __init__(self, storage: JsonStorage):
        """
        Initialize growth tracker
        
        Args:
            storage: Storage service instance
        """
        self.storage = storage
        
    async def track_daily_stats(self, resources: Dict[str, List[Resource]]) -> None:
        """
        Track daily resource statistics
        
        Args:
            resources: Resources by platform
        """
        date = datetime.now()
        stats = self._prepare_daily_stats(resources)
        await self.storage.save_daily_stats(stats, date)
        
    async def generate_weekly_stats(self) -> None:
        """Generate weekly resource statistics"""
        date = datetime.now()
        stats = await self._aggregate_weekly_stats(date)
        await self.storage.save_weekly_stats(stats, date)
        
    def calculate_growth_rate(self, resource_id: str) -> float:
        """
        Calculate resource growth rate
        
        Args:
            resource_id: Resource identifier
            
        Returns:
            Growth rate as percentage
        """
        date = datetime.now()
        current_week = self._get_weekly_downloads(resource_id, date)
        last_week = self._get_weekly_downloads(resource_id, date - timedelta(days=7))
        
        if not last_week:
            return 0.0
            
        return (current_week - last_week) / last_week * 100
        
    def _prepare_daily_stats(self, resources: Dict[str, List[Resource]]) -> Dict[str, Any]:
        """
        Prepare daily statistics from resources
        
        Args:
            resources: Resources by platform
            
        Returns:
            Daily statistics
        """
        stats = {
            "resource_stats": {},
            "timestamp": datetime.now().isoformat()
        }
        
        for platform, platform_resources in resources.items():
            for resource in platform_resources:
                resource_id = resource.id
                if resource_id not in stats["resource_stats"]:
                    stats["resource_stats"][resource_id] = {
                        "daily_stats": [],
                        "metadata": {
                            "name": resource.name,
                            "author": resource.author
                        }
                    }
                
                # 更新每日統計
                daily_stat = {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "downloads": resource.downloads,
                    "platforms": {platform: resource.downloads}
                }
                stats["resource_stats"][resource_id]["daily_stats"].append(daily_stat)
        
        return stats
        
    async def _aggregate_weekly_stats(self, date: datetime) -> Dict[str, Any]:
        """
        Aggregate weekly statistics
        
        Args:
            date: Target date
            
        Returns:
            Weekly statistics
        """
        stats = {
            "resource_stats": {},
            "timestamp": date.isoformat(),
            "week_number": date.isocalendar()[1]
        }
        
        # 取得本週所有日期
        week_start = date - timedelta(days=date.weekday())
        for i in range(7):
            day = week_start + timedelta(days=i)
            daily_stats = self.storage.get_daily_stats(day)
            
            # 合併每日統計到週統計
            for resource_id, resource_stats in daily_stats.get("resource_stats", {}).items():
                if resource_id not in stats["resource_stats"]:
                    stats["resource_stats"][resource_id] = {
                        "daily_stats": [],
                        "metadata": resource_stats["metadata"],
                        "weekly_total": 0
                    }
                
                # 加入每日統計
                for daily_stat in resource_stats["daily_stats"]:
                    stats["resource_stats"][resource_id]["daily_stats"].append(daily_stat)
                    stats["resource_stats"][resource_id]["weekly_total"] += daily_stat["downloads"]
        
        return stats
        
    def _get_weekly_downloads(self, resource_id: str, date: datetime) -> int:
        """
        Get weekly downloads for a resource
        
        Args:
            resource_id: Resource identifier
            date: Target date
            
        Returns:
            Total weekly downloads
        """
        weekly_stats = self.storage.get_weekly_stats(date)
        resource_stats = weekly_stats.get("resource_stats", {}).get(resource_id, {})
        return resource_stats.get("weekly_total", 0) 