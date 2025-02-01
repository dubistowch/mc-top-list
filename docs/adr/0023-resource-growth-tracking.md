# 23. 資源成長追蹤機制

Date: 2025-02-01

## Status

提議中 (Proposed)

## Context

目前系統在計算資源的週下載量成長率時存在以下問題：
1. 缺乏週下載量的實際數據
2. 成長率計算邏輯過於簡單
3. 沒有歷史數據支持趨勢分析

我們需要一個機制來：
1. 追蹤資源的下載量變化
2. 計算準確的週成長率
3. 提供可靠的趨勢分析數據

## Decision

我們決定：

1. 資料收集策略：
   - 每日記錄所有資源的下載量
   - 使用 JSON 檔案系統儲存歷史數據
   - 資料結構設計：
     ```json
     {
       "resource_stats": {
         "resource_id_1": {
           "daily_stats": [
             {
               "date": "2025-02-01",
               "downloads": 1000,
               "platforms": {
                 "modrinth": 500,
                 "hangar": 500
               }
             }
           ],
           "metadata": {
             "name": "Resource Name",
             "author": "Author Name"
           }
         }
       }
     }
     ```

2. 檔案儲存結構：
   ```
   data/
   ├── history/
   │   ├── 2025/
   │   │   ├── 02/
   │   │   │   ├── 01.json    # 每日統計
   │   │   │   └── 02.json
   │   │   └── weekly/        # 週統計彙整
   │   │       └── 05.json    # 第 5 週
   │   └── latest.json        # 最新統計快照
   └── aggregated/
       └── latest/
           └── aggregated.json # 當前聚合資料
   ```

3. 成長率計算邏輯：
   ```python
   def calculate_growth_rate(self, resource_id: str) -> float:
       """計算資源成長率
       
       1. 取得本週和上週的下載量
       2. 計算成長率
       3. 考慮多平台的情況
       """
       current_week = self._get_weekly_downloads(resource_id)
       last_week = self._get_last_weekly_downloads(resource_id)
       
       if last_week == 0:
           return 0.0
           
       return (current_week - last_week) / last_week
   ```

4. 效能考量：
   - 使用日期作為檔案名稱便於查詢
   - 每週產生一次週統計彙整檔案
   - 保持最新統計的快照以加速讀取
   - 定期清理過舊的歷史數據（預設保留 3 個月）

## Consequences

### 優點

1. 實作簡單：
   - 使用純文字檔案，無需額外資料庫
   - 容易備份和版本控制
   - 方便除錯和手動修正

2. 資料完整性：
   - 保留完整的歷史記錄
   - 支援多平台數據整合
   - 可追蹤長期趨勢

3. 效能表現：
   - 檔案分層儲存減少讀取量
   - 快照機制提升常用數據存取速度
   - 週期性彙整降低計算負擔

### 缺點

1. 擴展性限制：
   - 資料量大時可能影響效能
   - 不支援複雜的查詢功能
   - 缺乏事務處理機制

2. 維護考量：
   - 需要定期清理歷史數據
   - 檔案損壞風險較高
   - 並發處理較為複雜

### 監控和維護

1. 實作資料一致性檢查
2. 定期備份重要數據
3. 監控檔案系統使用量
4. 記錄異常狀況

## 替代方案

1. 使用 SQLite：
   - 優點：支援 SQL 查詢、更好的並發控制
   - 缺點：需要額外的依賴、備份較複雜

2. 使用 MongoDB：
   - 優點：更好的擴展性、原生支援 JSON
   - 缺點：系統複雜度增加、資源消耗較大

3. 使用 Redis：
   - 優點：高性能、支援資料過期
   - 缺點：記憶體需求大、持久化配置複雜

## 行動項目

1. 實作基礎的檔案儲存系統
2. 建立資料收集和彙整機制
3. 改進現有的成長率計算邏輯
4. 加入資料一致性檢查
5. 實作定期清理機制 