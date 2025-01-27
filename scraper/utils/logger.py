"""日誌工具模組"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from pythonjsonlogger import jsonlogger

# 常量定義
DEFAULT_NAME = "minecraft_scraper"
MAX_BYTES = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5
LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(message)s"

class AsyncLogger:
    """異步日誌記錄器"""
    
    _instance: Optional[logging.Logger] = None
    
    @classmethod
    def get_logger(cls, name: str = DEFAULT_NAME) -> logging.Logger:
        """獲取日誌記錄器實例"""
        if cls._instance is None:
            cls._instance = cls._setup_logger(name)
        return cls._instance
    
    @classmethod
    def _setup_logger(cls, name: str) -> logging.Logger:
        """設置日誌記錄器"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        # 確保日誌目錄存在
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 添加處理器
        logger.addHandler(cls._create_file_handler(log_dir / f"{name}.log"))
        logger.addHandler(cls._create_console_handler())
        
        return logger
    
    @staticmethod
    def _create_file_handler(log_path: Path) -> RotatingFileHandler:
        """創建文件處理器"""
        handler = RotatingFileHandler(
            log_path,
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )
        handler.setFormatter(jsonlogger.JsonFormatter(LOG_FORMAT))
        return handler
    
    @staticmethod
    def _create_console_handler() -> logging.StreamHandler:
        """創建控制台處理器"""
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        return handler

def setup_logger(name: str = DEFAULT_NAME) -> logging.Logger:
    """獲取日誌記錄器的便捷函數"""
    return AsyncLogger.get_logger(name) 