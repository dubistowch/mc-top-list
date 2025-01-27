"""路徑管理工具"""

import os
from pathlib import Path

# 基礎目錄
SCRAPER_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE_DIR = SCRAPER_DIR.parent

# 資料目錄
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
NORMALIZED_DIR = DATA_DIR / "normalized"
AGGREGATED_DIR = DATA_DIR / "aggregated"
SCHEMA_DIR = DATA_DIR / "schema"

# 日誌目錄
LOGS_DIR = BASE_DIR / "logs"

# 配置目錄
CONFIG_DIR = SCRAPER_DIR / "config"
API_CONFIG_PATH = CONFIG_DIR / "api_config.yml"
ENV_FILE_PATH = SCRAPER_DIR / ".env"

def ensure_directories():
    """確保所有必要的目錄都存在"""
    directories = [
        DATA_DIR,
        RAW_DIR,
        NORMALIZED_DIR,
        AGGREGATED_DIR,
        SCHEMA_DIR,
        LOGS_DIR,
        CONFIG_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True) 