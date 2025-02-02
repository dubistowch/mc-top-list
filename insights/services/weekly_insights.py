"""Weekly insights generator service"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import structlog
from dataclasses import dataclass
from zoneinfo import ZoneInfo
from jinja2 import Environment, FileSystemLoader

logger = structlog.get_logger(__name__)

@dataclass
class ResourceGrowthData:
    """資源成長數據結構"""
    current_week_downloads: int
    last_week_downloads: int
    growth_rate: float
    daily_stats: List[Dict[str, int]]

@dataclass
class TrendingResource:
    """Trending resource data structure"""
    id: str
    name: str
    description: str
    author: str
    downloads: int
    resource_type: str
    platforms: List[Dict[str, Any]]
    growth_data: ResourceGrowthData
    created_at: datetime
    updated_at: datetime
    highlight_reasons: List[str]

@dataclass
class WeeklyReport:
    """Weekly report data structure"""
    timestamp: str
    trending: Dict[str, List[TrendingResource]]
    version_updates: Dict[str, Any]
    category_highlights: Dict[str, Any]
    platform_stats: Dict[str, Any]

class WeeklyInsightsGenerator:
    """Weekly insights generator"""
    
    def __init__(self, base_dir: Path = None):
        """Initialize the generator
        
        Args:
            base_dir: Base directory for data files
        """
        self.base_dir = base_dir or Path.cwd()
        self.logger = logger.bind(service="weekly_insights")
        self.timezone = ZoneInfo("Asia/Taipei")
        
        # 初始化 Jinja2 環境
        template_dir = self.base_dir / "insights" / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True
        )
        
        # 註冊自定義過濾器
        self.jinja_env.filters["resource_type_name"] = self._resource_type_name
        self.jinja_env.filters["format_growth_rate"] = self._format_growth_rate
    
    def _resource_type_name(self, value: str) -> str:
        """Convert resource type to Chinese name"""
        type_names = {
            "mod": "模組",
            "modpack": "整合包",
            "resourcepack": "資源包",
            "datapack": "資料包",
            "plugin": "插件",
            "pluginpack": "插件包"
        }
        return type_names.get(value, value)
    
    def _format_growth_rate(self, value: float) -> str:
        """Format growth rate"""
        if value > 0:
            return f"+{value:.1f}%"
        return f"{value:.1f}%"
    
    def _get_resource_growth_data(self, resource: Dict[str, Any]) -> ResourceGrowthData:
        """Get resource growth data"""
        # 從歷史資料目錄讀取數據
        history_dir = self.base_dir / "data" / "history"
        now = datetime.now(self.timezone)
        
        # 計算本週和上週的時間範圍
        week_start = now - timedelta(days=now.weekday())
        last_week_start = week_start - timedelta(days=7)
        
        # 讀取本週和上週的下載量
        current_week = 0
        last_week = 0
        daily_stats = []
        
        # 模擬每日統計數據（實際應從歷史資料讀取）
        for i in range(14):
            date = (now - timedelta(days=i))
            daily_downloads = resource.get("downloads", 0) // 30  # 模擬每日下載量
            
            if date >= week_start:
                current_week += daily_downloads
            elif date >= last_week_start:
                last_week += daily_downloads
            
            daily_stats.append({
                "date": date.strftime("%Y-%m-%d"),
                "downloads": daily_downloads
            })
        
        # 計算成長率
        growth_rate = 0.0
        if last_week > 0:
            growth_rate = (current_week - last_week) / last_week * 100
        
        return ResourceGrowthData(
            current_week_downloads=current_week,
            last_week_downloads=last_week,
            growth_rate=growth_rate,
            daily_stats=daily_stats
        )
    
    def _find_rising_stars(self, data: Dict[str, Any], days: int = 7) -> List[TrendingResource]:
        """Find resources with significant growth in the past week"""
        trending = []
        resources = data.get("resources", {}).get("resources", {})
        
        for resource_type, type_data in resources.items():
            all_resources = type_data.get("all", [])
            
            for resource in all_resources:
                # 計算成長數據
                growth_data = self._get_resource_growth_data(resource)
                
                # 計算評分
                score = 0
                reasons = []
                
                # 1. 更新時間評分
                updated_at = datetime.fromisoformat(resource["updated_at"]).replace(tzinfo=self.timezone)
                days_since_update = (datetime.now(self.timezone) - updated_at).days
                if days_since_update <= 7:
                    score += (7 - days_since_update) * 10
                    reasons.append(f"最近 {days_since_update} 天內更新")
                
                # 2. 下載趨勢評分
                if growth_data.growth_rate > 50:
                    score += 30
                    reasons.append(f"下載成長 {growth_data.growth_rate:.1f}%")
                
                # 3. 版本支援評分
                if "1.20.4" in resource.get("versions", []):
                    score += 30
                    reasons.append("支援最新版本")
                
                # 4. 社群參與度評分
                if len(resource.get("platforms", [])) > 1:
                    score += 20
                    reasons.append(f"在 {len(resource['platforms'])} 個平台發布")
                
                trending.append(
                    TrendingResource(
                        id=resource["id"],
                        name=resource["name"],
                        description=resource["description"],
                        author=resource["author"],
                        downloads=resource["downloads"],
                        resource_type=resource_type,
                        platforms=resource["platforms"],
                        growth_data=growth_data,
                        created_at=datetime.fromisoformat(resource["created_at"]),
                        updated_at=updated_at,
                        highlight_reasons=reasons
                    )
                )
        
        # 按評分排序
        trending.sort(key=lambda x: x.growth_data.growth_rate, reverse=True)
        return trending[:10]
    
    def _load_latest_data(self) -> Dict[str, Any]:
        """Load the latest aggregated data"""
        try:
            latest_dir = self.base_dir / "data" / "aggregated" / "latest"
            data_file = latest_dir / "aggregated.json"
            
            with open(data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error("failed_to_load_data", error=str(e))
            raise
    
    def _analyze_version_trends(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze version adoption trends
        
        Args:
            data: Aggregated data
            
        Returns:
            Version trend analysis
        """
        version_stats = {}
        resources = data.get("resources", {}).get("resources", {})
        
        for resource_type, type_data in resources.items():
            for resource in type_data.get("all", []):
                for version in resource.get("versions", []):
                    if version not in version_stats:
                        version_stats[version] = {
                            "count": 0,
                            "downloads": 0,
                            "resources": []
                        }
                    version_stats[version]["count"] += 1
                    version_stats[version]["downloads"] += resource["downloads"]
                    version_stats[version]["resources"].append(resource["name"])
        
        return {
            "version_distribution": version_stats,
            "popular_versions": sorted(
                version_stats.items(),
                key=lambda x: x[1]["downloads"],
                reverse=True
            )[:5]
        }
    
    def _get_category_highlights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate category highlights
        
        Args:
            data: Aggregated data
            
        Returns:
            Category highlights
        """
        highlights = {}
        resources = data.get("resources", {}).get("resources", {})
        
        for resource_type, type_data in resources.items():
            popular = type_data.get("popular", [])
            if popular:
                highlights[resource_type] = {
                    "top_resources": popular[:5],
                    "total_resources": len(type_data.get("all", [])),
                    "total_downloads": sum(r["downloads"] for r in type_data.get("all", []))
                }
        
        return highlights
    
    def _get_platform_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate platform statistics
        
        Args:
            data: Aggregated data
            
        Returns:
            Platform statistics
        """
        stats = {}
        resources = data.get("resources", {}).get("resources", {})
        
        for resource_type, type_data in resources.items():
            for resource in type_data.get("all", []):
                platform = resource["platform"]
                if platform not in stats:
                    stats[platform] = {
                        "total_resources": 0,
                        "total_downloads": 0,
                        "resource_types": {}
                    }
                
                stats[platform]["total_resources"] += 1
                stats[platform]["total_downloads"] += resource["downloads"]
                
                if resource_type not in stats[platform]["resource_types"]:
                    stats[platform]["resource_types"][resource_type] = 0
                stats[platform]["resource_types"][resource_type] += 1
        
        return stats
    
    def generate_weekly_report(self) -> WeeklyReport:
        """Generate weekly insights report
        
        Returns:
            Weekly report
        """
        try:
            data = self._load_latest_data()
            
            report = WeeklyReport(
                timestamp=datetime.now(self.timezone).isoformat(),
                trending={
                    "rising_stars": self._find_rising_stars(data),
                    "community_favorites": data.get("resources", {}).get("popular", [])[:10]
                },
                version_updates=self._analyze_version_trends(data),
                category_highlights=self._get_category_highlights(data),
                platform_stats=self._get_platform_stats(data)
            )
            
            # 儲存報告
            self._save_report(report)
            
            self.logger.info("weekly_report_generated",
                           timestamp=report.timestamp)
            
            return report
            
        except Exception as e:
            self.logger.error("failed_to_generate_report", error=str(e))
            raise
    
    def _save_report(self, report: WeeklyReport) -> None:
        """Save the weekly report
        
        Args:
            report: Weekly report to save
        """
        try:
            # 建立報告目錄
            reports_dir = self.base_dir / "data" / "reports"
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            # 使用時間戳記作為檔名
            timestamp = datetime.now(self.timezone).strftime("%Y%m%d_%H%M%S")
            report_file = reports_dir / f"weekly_report_{timestamp}.json"
            
            # 將報告轉換為 JSON 格式
            report_data = {
                "timestamp": report.timestamp,
                "trending": {
                    "rising_stars": [vars(r) for r in report.trending["rising_stars"]],
                    "community_favorites": report.trending["community_favorites"]
                },
                "version_updates": report.version_updates,
                "category_highlights": report.category_highlights,
                "platform_stats": report.platform_stats
            }
            
            # 儲存 JSON 報告
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            # 產生 HTML 報告
            self._generate_html_report(report)
            
            self.logger.info("report_saved",
                           file=str(report_file))
            
        except Exception as e:
            self.logger.error("failed_to_save_report", error=str(e))
            raise

    def _generate_html_report(self, report: WeeklyReport) -> None:
        """Generate HTML report using template
        
        Args:
            report: Weekly report data
        """
        try:
            # 載入模板
            template = self.jinja_env.get_template("weekly_report.html.j2")
            
            # 註冊時間格式化過濾器
            def strftime(value, format="%Y-%m-%d %H:%M:%S"):
                if isinstance(value, str):
                    try:
                        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
                    except ValueError:
                        return value
                return value.strftime(format)
            
            self.jinja_env.filters["strftime"] = strftime
            
            # 建立公開目錄
            public_dir = self.base_dir / "public"
            public_dir.mkdir(parents=True, exist_ok=True)
            
            # 產生 HTML 報告
            html_content = template.render(report=report)
            
            # 儲存 HTML 報告
            index_file = public_dir / "index.html"
            with open(index_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            self.logger.info("html_report_generated",
                           file=str(index_file))
            
        except Exception as e:
            self.logger.error("failed_to_generate_html", error=str(e))
            raise 