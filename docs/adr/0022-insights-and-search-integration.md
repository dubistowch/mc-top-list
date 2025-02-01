# ADR 0022: 整合洞察報告與搜尋功能

## 狀態

提議

## 背景

目前系統有兩個主要的 HTML 輸出：
1. 由 aggregator 產生的搜尋頁面（`public/index.html`）
2. 由 insights 產生的週報頁面（`public/index.html`）

這兩個功能都很重要，但目前互相覆蓋，需要一個整合方案來提供更好的使用者體驗。

## 決策

我們決定將這兩個功能整合到同一個網頁介面中，主要以週報為主頁，並加入搜尋功能。具體實施方案如下：

### 1. 檔案結構調整

```
public/
  ├── index.html          # 主頁（週報）
  ├── search.html         # 搜尋頁面
  ├── css/
  │   ├── insights.css    # 週報樣式
  │   ├── search.css      # 搜尋頁面樣式
  │   └── common.css      # 共用樣式
  ├── js/
  │   ├── insights.js     # 週報互動功能
  │   ├── search.js       # 搜尋功能
  │   └── common.js       # 共用功能
  └── data/              # 靜態資料檔案
      ├── latest.json    # 最新資料
      └── reports/       # 歷史報告
```

### 2. 使用者介面整合

1. 導航欄設計：
   - 在頁面頂部加入導航欄
   - 包含週報和搜尋兩個主要分頁
   - 提供快速搜尋框

2. 主頁（週報）功能：
   - 保持現有的週報內容
   - 加入快速搜尋框
   - 新增資源卡片的快速預覽功能

3. 搜尋頁面增強：
   - 整合現有的搜尋功能
   - 加入進階過濾選項
   - 提供搜尋結果的視覺化展示

### 3. 實作步驟

1. 第一階段：基礎架構
   - 建立新的檔案結構
   - 實作共用的樣式和腳本
   - 修改 insights 生成器以支援新的結構

2. 第二階段：搜尋整合
   - 將搜尋功能模組化
   - 建立搜尋 API 端點
   - 整合到主頁的快速搜尋

3. 第三階段：使用者體驗優化
   - 實作進階搜尋功能
   - 加入資源預覽
   - 優化效能和響應式設計

4. 第四階段：資料同步
   - 實作資料更新機制
   - 建立緩存策略
   - 優化資料載入效能

### 4. 技術實作細節

1. 後端調整：
   ```python
   class InsightsGenerator:
       def generate(self):
           # 生成週報
           self._generate_insights()
           # 生成搜尋頁面
           self._generate_search_page()
           # 更新共用資源
           self._update_shared_resources()
   ```

2. 前端架構：
   ```javascript
   // common.js
   class ResourceManager {
       async search() { /* ... */ }
       async getDetails() { /* ... */ }
   }

   // insights.js
   class InsightsView {
       async initialize() { /* ... */ }
       async quickSearch() { /* ... */ }
   }

   // search.js
   class SearchView {
       async initialize() { /* ... */ }
       async advancedSearch() { /* ... */ }
   }
   ```

### 5. 指令與資料管理

1. 指令整合：
   ```bash
   # 生成所有頁面（週報和搜尋頁面）
   python -m insights generate

   # 清除舊的輸出檔案
   python -m insights clean
   ```

   指令說明：
   - `generate`: 一次性生成所有頁面，包含：
     - 週報頁面（index.html）
     - 搜尋頁面（search.html）
     - 靜態資源（css、js、images）
     - 建立必要的符號連結
   - `clean`: 清除所有生成的檔案，但保留原始資料

2. 資料目錄連結：
   ```
   data/
   ├── raw/                 # 原始資料
   ├── processed/           # 處理後資料
   ├── aggregated/          # 彙整資料
   │   ├── {timestamp}/    # 時間戳記目錄
   │   └── latest/         # 最新資料的符號連結
   ├── reports/            # 週報 JSON 檔案
   └── public/             # 公開資料
       ├── data/           # 符號連結到 aggregated/latest
       └── reports/        # 符號連結到 reports/

   # 建立符號連結的指令
   ln -sf ../aggregated/latest public/data
   ln -sf ../reports public/reports
   ```

### 6. 程式碼重組

1. 需要移除的檔案：
   ```
   scraper/services/aggregator/html_generator.py    # 搜尋頁面生成器移至 insights
   public/index.html                               # 由新的生成器取代
   public/js/search.js                            # 移至新結構
   public/css/style.css                           # 移至新結構
   ```

2. 需要移動的檔案：
   ```
   # 從 scraper 移動到 insights
   scraper/services/aggregator/templates/* -> insights/templates/search/
   scraper/services/aggregator/static/*    -> insights/static/

   # 重組後的 insights 目錄結構
   insights/
   ├── __init__.py
   ├── __main__.py
   ├── services/
   │   ├── __init__.py
   │   ├── weekly_insights.py
   │   └── search_insights.py      # 新增：搜尋頁面生成
   ├── templates/
   │   ├── base.html.j2           # 共用模板
   │   ├── components/            # 共用元件
   │   ├── weekly/               # 週報模板
   │   └── search/               # 搜尋模板
   └── static/
       ├── css/
       ├── js/
       └── img/
   ```

3. 設定檔調整：
   ```yaml
   # config.yml 新增設定
   insights:
     templates:
       path: insights/templates
     static:
       path: insights/static
     output:
       path: public
     data:
       path: data
   ```

## 影響

### 正面影響

1. 提供統一的使用者體驗
2. 改善資源的可發現性
3. 減少程式碼重複
4. 優化維護效率
5. 提供更豐富的功能組合

### 負面影響

1. 增加系統複雜度
2. 需要更多的前端開發工作
3. 可能需要更多的測試覆蓋
4. 初期開發工作量較大

## 實作指南

1. 建立新的目錄結構
2. 更新 insights 生成器
3. 重構搜尋功能
4. 實作共用元件
5. 更新部署流程
6. 加入新的測試案例

7. 資料遷移步驟：
   - 備份現有的 public 目錄
   - 建立新的目錄結構
   - 遷移靜態資源
   - 建立必要的符號連結
   - 驗證資料存取

8. 程式碼清理步驟：
   - 確認所有相依性
   - 移除廢棄的程式碼
   - 更新單元測試
   - 更新文件

## 相關 ADR

- ADR 0019: 新資料結構設計
- ADR 0021: 內容創作者週報

## 參考資料

- Bootstrap 5 文件
- Jinja2 模板引擎文件
- 現代前端架構最佳實踐 