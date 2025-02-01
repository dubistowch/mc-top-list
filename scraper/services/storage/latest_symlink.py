"""Latest symlink management module."""

import os
from pathlib import Path
import structlog

logger = structlog.get_logger(__name__)

def update_latest_symlink() -> None:
    """Update the 'latest' symlink to point to the most recent data directory."""
    try:
        base_dir = Path(__file__).parent.parent.parent.parent
        data_dir = base_dir / "data"
        
        # 檢查並更新 raw 資料的 latest 連結
        raw_dir = data_dir / "raw"
        if raw_dir.exists():
            raw_timestamps = sorted([d.name for d in raw_dir.iterdir() if d.is_dir()])
            if raw_timestamps:
                latest_raw = raw_dir / "latest"
                if latest_raw.exists() or latest_raw.is_symlink():
                    latest_raw.unlink()
                # 使用相對路徑
                os.chdir(raw_dir)
                os.symlink(Path(raw_timestamps[-1]), Path("latest"))
        
        # 檢查並更新 processed 資料的 latest 連結
        processed_dir = data_dir / "processed"
        if processed_dir.exists():
            processed_timestamps = sorted([d.name for d in processed_dir.iterdir() if d.is_dir()])
            if processed_timestamps:
                latest_processed = processed_dir / "latest"
                if latest_processed.exists() or latest_processed.is_symlink():
                    latest_processed.unlink()
                # 使用相對路徑
                os.chdir(processed_dir)
                os.symlink(Path(processed_timestamps[-1]), Path("latest"))
        
        # 檢查並更新 aggregated 資料的 latest 連結
        aggregated_dir = data_dir / "aggregated"
        if aggregated_dir.exists():
            aggregated_timestamps = sorted([d.name for d in aggregated_dir.iterdir() if d.is_dir()])
            if aggregated_timestamps:
                latest_aggregated = aggregated_dir / "latest"
                if latest_aggregated.exists() or latest_aggregated.is_symlink():
                    latest_aggregated.unlink()
                # 使用相對路徑
                os.chdir(aggregated_dir)
                os.symlink(Path(aggregated_timestamps[-1]), Path("latest"))
                
        logger.info("latest_symlinks_updated")
        
    except Exception as e:
        logger.error("failed_to_update_latest_symlinks", error=str(e))
        raise 