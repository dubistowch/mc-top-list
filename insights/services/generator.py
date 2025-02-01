"""Weekly insights generator service"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import structlog
from jinja2 import Environment, FileSystemLoader, select_autoescape, PackageLoader
from .resource_matcher import ResourceMatcher

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
                # 計算資源分數
                score = 0
                
                # 1. 更新時間權重 (最近一週內更新的資源加分)
                updated_at = datetime.strptime(resource.get("updated_at", ""), "%Y-%m-%d %H:%M:%S")
                days_since_update = (now - updated_at).days
                if days_since_update <= 7:
                    score += (7 - days_since_update) * 10  # 越近期更新分數越高
                
                # 2. 下載趨勢權重 (一週內的下載增長)
                weekly_downloads = resource.get("weekly_downloads", 0)
                total_downloads = resource.get("downloads", 0)
                if total_downloads > 0:
                    weekly_growth_rate = weekly_downloads / total_downloads
                    score += weekly_growth_rate * 100  # 轉換為百分比後加入分數
                
                # 3. 版本支援權重 (支援最新版本的資源加分)
                supported_versions = resource.get("versions", [])
                if "1.20.4" in supported_versions:  # 支援最新版本
                    score += 30
                elif "1.20" in supported_versions:  # 支援主要版本
                    score += 20
                
                # 4. 社群參與度權重
                if resource.get("is_featured", False):  # 被平台推薦
                    score += 50
                
                # 建立候選資源
                candidates.append({
                    "name": resource.get("name", ""),
                    "description": resource.get("description", ""),
                    "author": resource.get("author", ""),
                    "downloads": resource.get("downloads", 0),
                    "weekly_downloads": weekly_downloads,
                    "platforms": resource.get("platforms", []),
                    "score": score,
                    "type": resource.get("type", ""),
                    "versions": supported_versions,
                    "updated_at": resource.get("updated_at", "")
                })
                
            except Exception as e:
                self.logger.warning("failed_to_process_resource",
                                  resource=resource.get("name", "unknown"),
                                  error=str(e))
                continue
        
        # 按分數排序並返回前 10 個
        candidates.sort(key=lambda x: x["score"], reverse=True)
        top_candidates = candidates[:10]
        
        # 記錄選擇原因
        for candidate in top_candidates:
            reasons = []
            if candidate.get("weekly_downloads", 0) > 1000:
                reasons.append(f"本週下載量達 {candidate['weekly_downloads']:,} 次")
            if "1.20.4" in candidate.get("versions", []):
                reasons.append("支援最新版本")
            if len(candidate.get("platforms", [])) > 1:
                reasons.append(f"在 {len(candidate['platforms'])} 個平台上架")
            
            candidate["highlight_reasons"] = reasons
        
        return top_candidates
    
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
            
    def generate_weekly(self) -> None:
        """Generate weekly report"""
        try:
            # 載入資料
            data = self._load_data()
            
            # 生成週報頁面
            weekly_template = self.jinja_env.get_template("weekly_report.html.j2")
            weekly_html = weekly_template.render(data=data)
            
            # 儲存週報頁面
            weekly_path = self.public_dir / "index.html"
            weekly_path.write_text(weekly_html)
            self.logger.info("weekly_page_generated")
            
            # 生成搜尋頁面
            search_template = self.jinja_env.get_template("search/search.html.j2")
            search_html = search_template.render(data=data)
            
            # 儲存搜尋頁面
            search_path = self.public_dir / "search.html"
            search_path.write_text(search_html)
            self.logger.info("search_page_generated")
            
            # 複製靜態檔案
            self._copy_static_files()
            self.logger.info("static_files_copied")
            
            # 建立符號連結
            self._create_symlinks()
            
            self.logger.info("generation_completed")
            
        except Exception as e:
            self.logger.error("failed_to_generate_weekly", error=str(e))
            raise
            
    def clean(self) -> None:
        """Clean up generated files"""
        try:
            # 移除 public 目錄
            if self.public_dir.exists():
                shutil.rmtree(self.public_dir)
            
            self.logger.info("cleanup_completed")
            
        except Exception as e:
            self.logger.error("cleanup_failed", error=str(e))
            raise 