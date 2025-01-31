"""API 密鑰管理工具"""

import os
from typing import Dict, Optional
from pathlib import Path

from dotenv import load_dotenv

from scraper.utils.logger import setup_logger

class APIKeyManager:
    """API 密鑰管理器"""
    
    def __init__(self, env_path: Optional[Path] = None):
        """
        初始化管理器
        
        Args:
            env_path: .env 檔案路徑，預設為專案根目錄的 .env
        """
        self.logger = setup_logger()
        
        # 如果沒有指定 .env 路徑，則嘗試在專案根目錄尋找
        if not env_path:
            env_path = Path(__file__).parent.parent.parent / ".env"
        
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
        platforms = ["modrinth", "hangar"]
        
        for platform in platforms:
            env_key = os.getenv(f"{platform.upper()}_API_KEY")
            if env_key:
                self.keys[platform] = env_key
                self.logger.debug(f"從環境變數載入 {platform} API 密鑰")
            else:
                self.logger.warning(f"找不到 {platform} 的 API 密鑰")
    
    def get_key(self, platform: str) -> Optional[str]:
        """
        獲取指定平台的 API 密鑰
        
        Args:
            platform: 平台名稱 (例如: "modrinth", "hangar")
            
        Returns:
            API 密鑰，如果找不到則返回 None
        """
        key = self.keys.get(platform)
        if not key:
            self.logger.warning(f"找不到平台的 API 密鑰: {platform}")
        return key 