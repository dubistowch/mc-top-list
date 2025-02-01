"""API 密鑰管理工具"""

import os
from typing import Dict, Optional
from pathlib import Path

from dotenv import load_dotenv

from scraper.utils.logger import setup_logger
from scraper.config import get_config

class APIKeyManager:
    """API 密鑰管理器"""
    
    def __init__(self, env_path: Optional[Path] = None):
        """
        初始化管理器
        
        Args:
            env_path: .env 檔案路徑，預設為專案根目錄的 .env
        """
        self.logger = setup_logger()
        self.config = get_config()
        
        # 如果沒有指定 .env 路徑，則嘗試在專案根目錄尋找
        if not env_path:
            project_root = Path.cwd()
            env_path = project_root / ".env"
        
        # 載入 .env 檔案
        if env_path.exists():
            load_dotenv(env_path)
            self.logger.debug(f"已載入環境變數檔案: {env_path}")
        else:
            self.logger.warning(f"找不到環境變數檔案: {env_path}")
        
        self._load_keys()
    
    def _load_keys(self) -> None:
        """從環境變數載入 API 密鑰"""
        self.keys = {}
        
        # 從設定檔取得平台列表
        platforms = self.config.get("platforms", {}).keys()
        
        for platform in platforms:
            env_key = os.getenv(f"{platform.upper()}_API_KEY")
            if env_key:
                self.keys[platform] = env_key
                self.logger.debug(f"從環境變數載入 {platform} API 密鑰")
            else:
                self.logger.warning(f"找不到 {platform} 的 API 密鑰")
    
    def get_key(self, platform: str) -> Optional[str]:
        """
        取得指定平台的 API 密鑰
        
        Args:
            platform: 平台名稱
            
        Returns:
            API 密鑰，如果找不到則回傳 None
        """
        return self.keys.get(platform) 