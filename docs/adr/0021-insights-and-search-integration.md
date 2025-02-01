# ADR 0021: 整合洞察報告與搜尋功能

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

## 相關 ADR

- ADR 0019: 新資料結構設計
- ADR 0020: 內容創作者週報

## 參考資料

- Bootstrap 5 文件
- Jinja2 模板引擎文件
- 現代前端架構最佳實踐 