import yaml
from pathlib import Path
from typing import Dict

class APIKeyManager:
    """API 密鑰管理器"""
    
    def __init__(self, config_path: str = "config/api_config.yml"):
        self.config_path = Path(config_path)
        self.keys = self._load_keys()
    
    def _load_keys(self) -> Dict[str, str]:
        """載入 API 密鑰"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"API 配置文件未找到: {self.config_path}")
        
        with open(self.config_path, encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get_key(self, platform: str) -> str:
        """獲取特定平台的 API 密鑰"""
        if platform not in self.keys:
            raise KeyError(f"找不到平台的 API 密鑰: {platform}")
        return self.keys[platform] 