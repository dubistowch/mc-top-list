"""HTML 生成器"""

import os
from pathlib import Path
from typing import Dict, Any
import structlog
from jinja2 import Environment, FileSystemLoader
from ..config import get_config

logger = structlog.get_logger(__name__)

class HtmlGenerator:
    """HTML 生成器"""
    
    def __init__(self, base_dir: Path = None):
        """
        初始化生成器
        
        Args:
            base_dir: 基礎目錄
        """
        self.base_dir = base_dir or Path.cwd()
        self.config = get_config()
        
        # 設定 Jinja2 環境
        template_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True
        )
    
    def generate(self, timestamp: str) -> None:
        """
        生成 HTML 檔案
        
        Args:
            timestamp: 時間戳記
        """
        try:
            # 準備模板資料
            template_data = {
                "platforms": {
                    name: {
                        "label": config.get("label", name.title()),
                        "color": config.get("color", "#666666")
                    }
                    for name, config in self.config.get("platforms", {}).items()
                },
                "resource_types": self.config.get("resource_types", {})
            }
            
            # 取得模板
            template = self.env.get_template("index.html.j2")
            
            # 生成 HTML
            html_content = template.render(**template_data)
            
            # 建立輸出目錄
            output_dir = self.base_dir / "data" / "aggregated" / timestamp
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 寫入 HTML 檔案
            output_file = output_dir / "index.html"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            logger.info("html_generated", 
                       timestamp=timestamp,
                       output_file=str(output_file))
            
        except Exception as e:
            logger.error("html_generation_failed", error=str(e))
            raise 