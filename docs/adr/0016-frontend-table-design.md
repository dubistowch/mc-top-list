# ADR 0016: Frontend Table Design and Filtering Implementation

## Status
Proposed

## Context
需要一個直觀且功能完整的前端介面來展示從不同平台收集的 Minecraft 插件/模組資料。使用者需要能夠快速瀏覽、搜尋和過濾這些資料，以找到他們感興趣的內容。為了快速實現基本功能，我們選擇使用 Bootstrap 來建立簡單且實用的介面。

## Decision
我們將實作以下前端表格設計策略：

1. **技術選擇**
   - 使用 Bootstrap 5 作為 UI 框架
   - 使用 DataTables 插件處理表格功能
   - 純 HTML + JavaScript 實作，不依賴前端框架

2. **資料呈現**
   ```html
   <!DOCTYPE html>
   <html>
   <head>
     <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
     <link href="https://cdn.datatables.net/1.13.7/css/dataTables.bootstrap5.min.css" rel="stylesheet">
   </head>
   <body>
     <div class="container mt-4">
       <div class="row mb-3">
         <div class="col">
           <input type="text" class="form-control" id="globalSearch" placeholder="搜尋...">
         </div>
       </div>
       
       <table id="modTable" class="table table-striped">
         <thead>
           <tr>
             <th>名稱</th>
             <th>版本</th>
             <th>下載次數</th>
             <th>更新時間</th>
             <th>支援版本</th>
             <th>來源平台</th>
           </tr>
         </thead>
         <tbody>
           <!-- 動態產生的資料列 -->
         </tbody>
       </table>
     </div>

     <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
     <script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
     <script src="https://cdn.datatables.net/1.13.7/js/dataTables.bootstrap5.min.js"></script>
   </body>
   </html>
   ```

3. **過濾功能**
   ```javascript
   $(document).ready(function() {
     $('#modTable').DataTable({
       language: {
         url: '//cdn.datatables.net/plug-ins/1.13.7/i18n/zh-HANT.json'
       },
       pageLength: 25,
       order: [[2, 'desc']], // 預設按下載次數排序
       columns: [
         { data: 'name' },
         { data: 'version' },
         { data: 'downloads', render: $.fn.dataTable.render.number(',', '.', 0) },
         { data: 'updated_at' },
         { data: 'game_versions' },
         { data: 'platform' }
       ]
     });
   });
   ```

4. **使用者體驗優化**
   - 使用 Bootstrap 的響應式設計
   - 實作分頁功能
   - 提供簡單的欄位排序
   - 支援基本的搜尋過濾

## Consequences
### Positive
- 快速實現基本功能
- 較低的開發複雜度
- 無需額外的建置工具
- 容易維護和修改

### Negative
- 功能相對較為基礎
- 較難實現複雜的自定義功能
- 依賴 jQuery
- 效能可能不如現代前端框架

## Related ADRs
- [ADR 0015](./0015-data-aggregation-and-storage.md)

Date: 2025-02-01 