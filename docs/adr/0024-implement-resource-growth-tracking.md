# 24. 實作資源成長追蹤機制

Date: 2025-02-03

## Status

提議中 (Proposed)

## Context

根據 [ADR 0023](./0023-resource-growth-tracking.md) 的設計，我們需要實作一個完整的資源成長追蹤機制。目前的實作存在以下問題：

1. 資料收集不完整
   - 缺乏每日數據收集機制
   - 沒有實作多平台數據整合
   - 歷史數據儲存結構未完全實現

2. 成長率計算不準確
   - 使用模擬數據而非實際歷史數據
   - 沒有考慮多平台的情況
   - 缺乏數據驗證機制

3. 效能考量未實現
   - 缺少快照機制
   - 沒有實作定期清理
   - 缺乏資料一致性檢查

## Decision

我們將通過以下步驟來實作 ADR 0023 的設計：

### 1. 資料收集實作

```python
class ResourceDataCollector:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.history_dir = base_dir / "data" / "history"
        self.logger = structlog.get_logger(__name__)
    
    def collect_daily_stats(self) -> None:
        """收集每日統計數據"""
        date = datetime.now(ZoneInfo("Asia/Taipei"))
        stats = self._gather_platform_stats()
        
        # 建立日期目錄結構
        daily_dir = self.history_dir / str(date.year) / f"{date.month:02d}"
        daily_dir.mkdir(parents=True, exist_ok=True)
        
        # 儲存每日統計
        daily_file = daily_dir / f"{date.day:02d}.json"
        with open(daily_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        # 更新最新快照
        latest_file = self.history_dir / "latest.json"
        with open(latest_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    
    def _gather_platform_stats(self) -> Dict[str, Any]:
        """從各平台收集統計數據"""
        return {
            "resource_stats": {
                # 實作平台數據收集邏輯
            }
        }
```

### 2. 週統計實作

```python
class WeeklyStatsAggregator:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.history_dir = base_dir / "data" / "history"
    
    def aggregate_weekly_stats(self) -> None:
        """產生週統計彙整"""
        date = datetime.now(ZoneInfo("Asia/Taipei"))
        week_number = date.isocalendar()[1]
        
        # 讀取本週每日統計
        daily_stats = self._get_daily_stats(date)
        
        # 產生週統計
        weekly_dir = self.history_dir / str(date.year) / "weekly"
        weekly_dir.mkdir(parents=True, exist_ok=True)
        
        weekly_file = weekly_dir / f"{week_number:02d}.json"
        with open(weekly_file, "w", encoding="utf-8") as f:
            json.dump(daily_stats, f, ensure_ascii=False, indent=2)
    
    def _get_daily_stats(self, date: datetime) -> Dict[str, Any]:
        """讀取每日統計數據"""
        stats = {}
        # 實作每日統計讀取邏輯
        return stats
```

### 3. 成長率計算改進

```python
class GrowthAnalyzer:
    def calculate_growth_rate(self, resource_id: str) -> float:
        """計算資源成長率"""
        current_week = self._get_weekly_downloads(resource_id)
        last_week = self._get_last_weekly_downloads(resource_id)
        
        if not last_week:
            return 0.0
        
        return (current_week - last_week) / last_week * 100
    
    def _get_weekly_downloads(self, resource_id: str) -> int:
        """取得本週下載量"""
        # 實作週下載量計算邏輯
        return 0
```

### 4. 資料維護機制

```python
class DataMaintainer:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.history_dir = base_dir / "data" / "history"
    
    def cleanup_old_data(self, months: int = 3) -> None:
        """清理過舊的歷史數據"""
        cutoff_date = datetime.now() - timedelta(days=months * 30)
        # 實作資料清理邏輯
    
    def verify_data_integrity(self) -> bool:
        """檢查資料一致性"""
        # 實作資料一致性檢查
        return True
```

### 5. 系統整合

```python
class ResourceTracker:
    def __init__(self, base_dir: Path):
        self.collector = ResourceDataCollector(base_dir)
        self.aggregator = WeeklyStatsAggregator(base_dir)
        self.analyzer = GrowthAnalyzer()
        self.maintainer = DataMaintainer(base_dir)
    
    def run_daily_tasks(self) -> None:
        """執行每日任務"""
        self.collector.collect_daily_stats()
        self.maintainer.verify_data_integrity()
    
    def run_weekly_tasks(self) -> None:
        """執行週期任務"""
        self.aggregator.aggregate_weekly_stats()
        self.maintainer.cleanup_old_data()
```

## Consequences

### 優點

1. 完整實現 ADR 0023 的設計
2. 提供可靠的成長率計算
3. 支援多平台數據整合
4. 具備資料維護機制
5. 改進效能表現

### 缺點

1. 增加系統複雜度
2. 需要額外的運算資源
3. 需要定期維護
4. 可能需要調整現有程式碼

## 實作步驟

1. 建立基礎檔案結構
2. 實作資料收集機制
3. 實作週統計彙整
4. 改進成長率計算
5. 加入資料維護功能
6. 整合到現有系統
7. 撰寫測試案例
8. 部署監控機制

## 相關文件

- [ADR 0023](./0023-resource-growth-tracking.md)
- [ADR 0021](./0021-data-analysis-strategy.md)
- [ADR 0022](./0022-insights-and-search-integration.md)
- [ADR 0016](./0016-frontend-table-design.md) 