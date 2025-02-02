"""Weekly insights generator service"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import structlog
from jinja2 import Environment, FileSystemLoader, select_autoescape, PackageLoader
from .resource_matcher import ResourceMatcher
import random
from dataclasses import dataclass

@dataclass
class ResourceGrowthData:
    """資源成長數據"""
    current_week_downloads: int
    last_week_downloads: int
    growth_rate: float
    daily_stats: list[int]

logger = structlog.get_logger(__name__)

def resource_type_name(value: str) -> str:
    """Convert resource type to Chinese name."""
    type_names = {
        "mod": "模組",
        "modpack": "整合包",
        "resourcepack": "資源包",
        "datapack": "資料包",
        "plugin": "插件",
        "pluginpack": "插件包"
    }
    return type_names.get(value, value)

def format_growth_rate(value: float) -> str:
    """Format growth rate as percentage with sign"""
    if value > 0:
        return f"+{value:.1f}%"
    return f"{value:.1f}%"

class WeeklyInsightsGenerator:
    """Weekly insights generator service"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.data_dir = base_dir / "data"
        self.public_dir = base_dir / "public"
        self.templates_dir = base_dir / "insights" / "templates"
        self.static_dir = base_dir / "insights" / "static"
        self.resource_matcher = ResourceMatcher()
        
        # 設定 Jinja2 環境
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=select_autoescape()
        )
        
        # 註冊過濾器
        self.jinja_env.filters["resource_type_name"] = resource_type_name
        self.jinja_env.filters["format_number"] = lambda n: "{:,}".format(n)
        self.jinja_env.filters["format_growth_rate"] = format_growth_rate
        
        self.logger = structlog.get_logger()
    
    def _merge_resources_by_type(self, resources_by_type: Dict[str, Dict[str, List[Dict[str, Any]]]]) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """Merge same resources across platforms for each resource type and category"""
        merged_resources = {}
        
        for resource_type, categories in resources_by_type.items():
            merged_resources[resource_type] = {}
            for category, resources in categories.items():
                merged_resources[resource_type][category] = self.resource_matcher.merge_resources(resources)
        
        return merged_resources
    
    def _load_data(self) -> dict:
        """Load data from aggregated.json"""
        try:
            # 載入最新的彙整資料
            latest_data = self.data_dir / "aggregated" / "latest" / "aggregated.json"
            with latest_data.open() as f:
                raw_data = json.load(f)
            
            # 合併相同資源
            raw_data["resources"]["resources"] = self._merge_resources_by_type(raw_data["resources"]["resources"])
            
            # 提取所有資源並標準化時間格式
            all_resources = []
            for resource_type, type_data in raw_data["resources"]["resources"].items():
                for category in ["popular", "trending", "updated", "new"]:
                    if category in type_data:
                        for resource in type_data[category]:
                            resource["type"] = resource_type
                            # 標準化時間格式
                            if "updated_at" in resource:
                                try:
                                    dt = datetime.fromisoformat(resource["updated_at"].replace("Z", "+00:00"))
                                    resource["updated_at"] = dt.strftime("%Y-%m-%d %H:%M:%S")
                                except ValueError:
                                    self.logger.warning("invalid_datetime_format", 
                                        resource=resource["name"],
                                        datetime=resource["updated_at"])
                            all_resources.append(resource)
            
            # 分析資料
            rising_stars = self._find_rising_stars(all_resources)
            version_updates = self._analyze_version_trends(all_resources)
            category_highlights = self._get_category_highlights(all_resources)
            platform_stats = self._get_platform_stats(all_resources)
            
            # 建立報告資料結構
            report = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "trending": {
                    "rising_stars": rising_stars
                },
                "version_updates": version_updates,
                "category_highlights": category_highlights,
                "platform_stats": platform_stats
            }
            
            # 建立資料結構
            data = {
                "report": report,
                "resources": raw_data,
                "platforms": {
                    "modrinth": {"label": "Modrinth", "color": "success"},
                    "hangar": {"label": "Hangar", "color": "primary"},
                    "polymart": {"label": "Polymart", "color": "info"}
                },
                "metadata": {
                    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "total_resources": raw_data["metadata"]["total_resources"]
                }
            }
            
            return data
            
        except Exception as e:
            self.logger.error("failed_to_load_data", error=str(e))
            raise
            
    def _find_rising_stars(self, data: list) -> list:
        """Find rising star resources based on multiple factors"""
        candidates = []
        now = datetime.now()
        
        for resource in data:
            try:
                # 計算成長數據
                growth_data = self._get_resource_growth_data(resource)
                
                # 計算資源分數
                score = 0
                reasons = []
                
                # 1. 更新時間權重 (最近一週內更新的資源加分)
                updated_at = datetime.strptime(resource.get("updated_at", ""), "%Y-%m-%d %H:%M:%S")
                days_since_update = (now - updated_at).days
                if days_since_update <= 7:
                    score += (7 - days_since_update) * 10  # 越近期更新分數越高
                    reasons.append(f"最近 {days_since_update} 天內更新")
                
                # 2. 下載趨勢權重
                if growth_data.growth_rate > 50:
                    score += 30
                    reasons.append(f"下載成長 {growth_data.growth_rate:.1f}%")
                
                # 3. 版本支援權重 (支援最新版本的資源加分)
                supported_versions = resource.get("versions", [])
                if "1.20.4" in supported_versions:  # 支援最新版本
                    score += 30
                    reasons.append("支援最新版本")
                elif "1.20" in supported_versions:  # 支援主要版本
                    score += 20
                
                # 4. 社群參與度權重
                platforms = resource.get("platforms", [])
                if len(platforms) > 1:
                    score += 20
                    reasons.append(f"在 {len(platforms)} 個平台發布")
                
                # 建立候選資源
                candidates.append({
                    "id": resource.get("id", ""),
                    "name": resource.get("name", ""),
                    "description": resource.get("description", ""),
                    "author": resource.get("author", ""),
                    "downloads": resource.get("downloads", 0),
                    "platforms": platforms,
                    "growth_data": {
                        "current_week_downloads": growth_data.current_week_downloads,
                        "last_week_downloads": growth_data.last_week_downloads,
                        "growth_rate": growth_data.growth_rate,
                        "daily_stats": growth_data.daily_stats
                    },
                    "type": resource.get("type", ""),
                    "versions": supported_versions,
                    "updated_at": resource.get("updated_at", ""),
                    "highlight_reasons": reasons
                })
                
            except Exception as e:
                self.logger.warning("failed_to_process_resource",
                                  resource=resource.get("name", "unknown"),
                                  error=str(e))
                continue
        
        # 按成長率排序
        candidates.sort(key=lambda x: x["growth_data"]["growth_rate"], reverse=True)
        return candidates[:10]
    
    def _analyze_version_trends(self, data: list) -> dict:
        """Analyze version trends"""
        version_stats = {}
        
        # 從資料中提取版本資訊
        for resource in data:
            for version in resource.get("versions", []):
                if version not in version_stats:
                    version_stats[version] = {"count": 0, "resources": []}
                version_stats[version]["count"] += 1
                version_stats[version]["resources"].append(resource["name"])
        
        # 按資源數量排序
        popular_versions = sorted(
            version_stats.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )
        
        return {
            "popular_versions": popular_versions[:5]
        }
    
    def _get_category_highlights(self, data: list) -> dict:
        """Get category highlights"""
        highlights = {}
        
        # 按類型分組資源
        for resource in data:
            category = resource.get("type", "其他")
            if category not in highlights:
                highlights[category] = {
                    "total_resources": 0,
                    "total_downloads": 0,
                    "top_resources": []
                }
            
            highlights[category]["total_resources"] += 1
            highlights[category]["total_downloads"] += resource.get("downloads", 0)
            highlights[category]["top_resources"].append(resource)
        
        # 為每個類型排序並只保留前 5 個資源
        for category in highlights:
            highlights[category]["top_resources"].sort(
                key=lambda x: x.get("downloads", 0),
                reverse=True
            )
            highlights[category]["top_resources"] = highlights[category]["top_resources"][:5]
        
        return highlights
    
    def _get_platform_stats(self, data: list) -> dict:
        """Get platform statistics"""
        stats = {}
        
        # 從資料中提取平台統計
        for resource in data:
            # 處理多平台資源
            for platform_info in resource.get("platforms", []):
                platform = platform_info["name"].lower()
                if platform not in stats:
                    stats[platform] = {
                        "total_resources": 0,
                        "total_downloads": 0,
                        "resource_types": {}
                    }
                
                stats[platform]["total_resources"] += 1
                stats[platform]["total_downloads"] += platform_info["downloads"]
                
                resource_type = resource.get("type", "其他")
                if resource_type not in stats[platform]["resource_types"]:
                    stats[platform]["resource_types"][resource_type] = 0
                stats[platform]["resource_types"][resource_type] += 1
        
        return stats
    
    def _copy_static_files(self) -> None:
        """Copy static files to public directory"""
        try:
            # 確保目標目錄存在
            for dir_name in ["css", "js", "img"]:
                target_dir = self.public_dir / dir_name
                target_dir.mkdir(exist_ok=True)
                
                # 複製檔案
                source_dir = self.static_dir / dir_name
                if source_dir.exists():
                    for file in source_dir.glob("*"):
                        if file.is_file():
                            shutil.copy2(file, target_dir / file.name)
                            
            self.logger.info("static_files_copied")
            
        except Exception as e:
            self.logger.error("failed_to_copy_static_files", error=str(e))
            raise
            
    def _create_symlinks(self) -> None:
        """Create necessary symlinks"""
        try:
            # 移除舊的符號連結
            for link in ["data/latest", "data/reports", "index.html", "aggregated.json"]:
                link_path = self.public_dir / link
                if link_path.is_symlink():
                    link_path.unlink()
            
            # 建立資料目錄
            data_dir = self.public_dir / "data"
            data_dir.mkdir(exist_ok=True)
            
            # 建立資料連結
            latest_link = data_dir / "latest"
            latest_link.symlink_to(self.data_dir / "aggregated" / "latest")
            
            # 建立報告連結
            reports_link = data_dir / "reports"
            reports_link.symlink_to(self.data_dir / "reports")
            
            self.logger.info("symlinks_created")
            
        except Exception as e:
            self.logger.error("failed_to_create_symlinks", error=str(e))
            raise
            
    def generate_weekly_report(self) -> None:
        """生成週報"""
        try:
            # 載入資料
            data = self._load_data()
            
            # 確保輸出目錄存在
            self.public_dir.mkdir(parents=True, exist_ok=True)
            
            # 渲染模板
            template = self.jinja_env.get_template("weekly_report.html.j2")
            html = template.render(data=data)
            
            # 寫入輸出檔案
            output_file = self.public_dir / "index.html"
            with output_file.open("w", encoding="utf-8") as f:
                f.write(html)
            
            # 複製靜態檔案
            if self.static_dir.exists():
                shutil.copytree(self.static_dir, self.public_dir / "static", dirs_exist_ok=True)
            
            self.logger.info("weekly_report_generated", output_file=str(output_file))
            
        except Exception as e:
            self.logger.error("failed_to_generate_weekly", error=str(e))
            raise
    
    def clean(self) -> None:
        """Clean up generated files"""
        try:
            if self.public_dir.exists():
                shutil.rmtree(self.public_dir)
            self.logger.info("cleaned_output_directory",
                           directory=str(self.public_dir))
        except Exception as e:
            self.logger.error("failed_to_clean",
                            error=str(e))
            raise

    def _get_resource_growth_data(self, resource: dict) -> ResourceGrowthData:
        """計算資源的成長數據"""
        # 從歷史資料目錄讀取數據
        history_dir = self.data_dir / "history"
        
        # 計算本週和上週的下載量
        current_week_downloads = resource.get("current_week_downloads", 0)
        last_week_downloads = resource.get("last_week_downloads", 0)
        
        # 計算成長率
        growth_rate = 0
        if last_week_downloads > 0:
            growth_rate = ((current_week_downloads - last_week_downloads) / last_week_downloads) * 100
            
        # 從歷史資料讀取每日統計
        daily_stats = resource.get("daily_stats", [0] * 14)  # 預設為 14 天的空數據
            
        return ResourceGrowthData(
            current_week_downloads=current_week_downloads,
            last_week_downloads=last_week_downloads,
            growth_rate=growth_rate,
            daily_stats=daily_stats
        )

    def _format_growth_rate(self, value: float) -> str:
        """格式化成長率"""
        if value > 0:
            return f"+{value:.1f}%"
        else:
            return f"{value:.1f}%" 