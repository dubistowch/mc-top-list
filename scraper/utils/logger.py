"""日誌工具模組"""

import logging
from datetime import datetime

from scraper.utils.paths import LOGS_DIR

def setup_logger(name: str = "minecraft_scraper") -> logging.Logger:
    """設定日誌記錄器
    
    Args:
        name: 日誌記錄器名稱
        
    Returns:
        配置好的日誌記錄器
    """
    logger = logging.getLogger(name)
    
    # 如果已經配置過，直接返回
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.DEBUG)
    
    # 確保日誌目錄存在
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 檔案處理器
    log_file = LOGS_DIR / f"{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    
    # 控制台處理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 設定格式
    formatter = logging.Formatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加處理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger 