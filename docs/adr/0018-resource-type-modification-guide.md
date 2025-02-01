# 18. Resource Type 修改指南

日期: 2024-02-01

## 狀態

已接受

## 背景

在系統中新增或修改 resource type 時,需要同時修改多個相關的程式碼部分。為了確保修改的一致性和完整性,需要一個明確的指南來說明所有需要修改的部分。

## 決策

我們決定建立一個標準化的流程,列出新增或修改 resource type 時需要更新的所有程式碼位置:

### 1. 設定檔修改
- 位置：`scraper/config.yml`
- 修改項目：
  - 在對應平台的 `resource_types` 列表中新增新的類型

### 2. API 客戶端修改
- 位置：`scraper/clients/{platform}.py`
- 修改項目：
  - 在類型映射中新增對應（如 `category_map`、`type_map`）
  - 確保 `fetch_resources` 方法支援新的類型
  - 實作資源類型分組的資料結構

### 3. 資料儲存格式
- 原始資料：
  - 位置：`data/raw/{timestamp}/{platform}_{type}_raw.json`
  - 格式：每個資源類型獨立檔案
  - 結構：
    ```json
    {
      "hits": [...],
      "offset": 0,
      "limit": 100,
      "total": 50
    }
    ```
- 處理後資料：
  - 位置：`data/processed/{timestamp}/{platform}_processed.json`
  - 格式：所有類型合併在同一檔案
  - 結構：
    ```json
    {
      "timestamp": "2024-02-01T00:00:00Z",
      "platform": "platform_name",
      "resources": {
        "mod": [...],
        "plugin": [...],
        "pluginpack": [...]
      }
    }
    ```

### 4. 資料轉換器修改
- 位置：`scraper/services/transformers/{platform}.py`
- 修改項目：
  - 確保 `transform` 方法支援新的 resource type
  - 更新相關的日誌記錄
  - 處理新類型特有的欄位轉換

### 5. 資料聚合修改
- 位置：`scraper/services/aggregator.py`
- 修改項目：
  - 在 `_group_resources` 方法中新增類型標籤
  - 確保新類型的資源能正確分類
  - 更新統計計算邏輯

### 6. 測試案例修改
- 位置：`scraper/tests/test_scraper.py`
- 修改項目：
  - 新增新 resource type 的測試資料
  - 新增轉換邏輯的測試案例
  - 新增聚合結果的測試案例
  - 更新相關的 mock 資料

### 7. 文件更新
- 修改項目：
  - 更新 README.md 中的支援資源類型列表
  - 更新 API 文件中的資源類型說明
  - 更新聚合結果的格式文件
  - 更新相關的 ADR 文件

## 影響

### 正面影響

1. 標準化的修改流程可以減少遺漏
2. 明確的修改指南可以提高開發效率
3. 完整的文件更新可以確保系統文件的準確性
4. 確保資料聚合結果的一致性
5. 資源類型分檔儲存提高了資料的可讀性和可維護性
6. 獨立檔案儲存便於資料的版本控制和差異比對

### 負面影響

1. 每次新增 resource type 需要修改多個檔案
2. 需要額外的測試工作來確保修改的正確性
3. 需要確保聚合邏輯與新的 resource type 相容
4. 資源類型分檔儲存會產生較多的檔案數量

## 備註

- 在進行修改時,建議先在測試環境中完整測試
- 確保所有相關的日誌記錄都有適當更新
- 考慮向後相容性問題
- 確保聚合結果的格式保持一致性
- 定期檢查資料儲存格式是否符合規範
- 考慮使用工具自動化部分修改流程

## 參考資料

- Polymart API 文件: https://polymart.org/wiki/api
- Modrinth API 文件: https://docs.modrinth.com/api-spec/
- 系統架構文件
- ADR-0000: 架構決策記錄模板 