"""API 密鑰管理工具"""

import os
from typing import Dict, Optional

import yaml

from scraper.utils.logger import setup_logger
from scraper.utils.paths import API_CONFIG_PATH

class APIKeyManager:
    """API 密鑰管理器"""
    
    def __init__(self):
        """初始化管理器"""
        self.logger = setup_logger()
        self.config_path = API_CONFIG_PATH
        self._load_keys()
    
    def _load_keys(self) -> None:
        """從 config.yml 載入 API 密鑰"""
        self.keys = {}
        platforms = ["hangar", "modrinth"]
        
        if not self.config_path.exists():
            self.logger.warning(f"找不到配置檔案: {self.config_path}")
            return
            
        try:
            with open(self.config_path, encoding='utf-8') as f:
                config = yaml.safe_load(f)
                for platform in platforms:
                    if platform in config:
                        platform_config = config[platform]
                        if isinstance(platform_config, dict) and "api_key" in platform_config:
                            self.keys[platform] = platform_config["api_key"]
                            self.logger.debug(f"從配置檔案載入 {platform} API 密鑰")
                        else:
                            self.logger.warning(f"配置檔案中缺少 {platform} 的 api_key 設定")
                    else:
                        self.logger.warning(f"配置檔案中缺少 {platform} 的設定")
        except Exception as e:
            self.logger.warning(f"載入配置檔案失敗: {str(e)}")
    
    def get_key(self, platform: str) -> Optional[str]:
        """獲取指定平台的 API 密鑰"""
        key = self.keys.get(platform)
        if not key:
            self.logger.warning(f"找不到平台的 API 密鑰: {platform}")
        return key 