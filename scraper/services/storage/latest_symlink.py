"""Latest symlink management"""

import os
from pathlib import Path
import structlog
from ...config import get_config

logger = structlog.get_logger(__name__)

def update_latest_symlink() -> None:
    """Update the 'latest' symlink to point to the most recent data directory"""
    try:
        config = get_config()
        base_dir = Path.cwd()
        
        # 尋找最新的時間戳記目錄
        aggregated_dir = base_dir / "data" / "aggregated"
        if not aggregated_dir.exists():
            logger.warning("aggregated_dir_not_found", path=str(aggregated_dir))
            return
            
        timestamp_dirs = [d for d in aggregated_dir.iterdir() if d.is_dir() and not d.is_symlink()]
        if not timestamp_dirs:
            logger.warning("no_timestamp_dirs_found", path=str(aggregated_dir))
            return
            
        latest_dir = max(timestamp_dirs, key=lambda x: x.name)
        
        # 更新 latest 連結
        latest_link = aggregated_dir / "latest"
        if latest_link.exists():
            if latest_link.is_symlink():
                latest_link.unlink()
            else:
                logger.warning("latest_link_exists_not_symlink", path=str(latest_link))
                return
        latest_link.symlink_to(latest_dir.name, target_is_directory=True)
        
        # 建立或更新 public 目錄
        public_dir = base_dir / "public"
        if not public_dir.exists():
            public_dir.mkdir(parents=True)
        
        # 建立從 public 到 data/aggregated/latest 的連結
        for item in latest_dir.iterdir():
            public_link = public_dir / item.name
            if public_link.exists():
                if public_link.is_symlink():
                    public_link.unlink()
                else:
                    logger.warning("public_link_exists_not_symlink", path=str(public_link))
                    continue
            
            # 建立相對路徑的連結
            relative_path = os.path.relpath(item, public_dir)
            public_link.symlink_to(relative_path)
            
        logger.info("latest_symlinks_updated")
        
    except Exception as e:
        logger.error("failed_to_update_latest_symlink", error=str(e))
        raise 