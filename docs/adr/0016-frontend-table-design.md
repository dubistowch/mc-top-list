# ADR 0016: Frontend Table Design and Filtering Implementation

## Status
Accepted (Updated 2025/02/15)

## Context
We need an intuitive and feature-complete frontend interface to display Minecraft plugin/mod data collected from different platforms. Users need to be able to quickly browse, search, and filter this data to find content they're interested in. To quickly implement basic functionality, we chose to use Bootstrap to create a simple and practical interface.

## Decision
We will implement the following frontend design strategy:

1. **Technology Stack**
   - Use Bootstrap 5 as the UI framework
   - Use Jinja2 for server-side templating
   - Pure HTML + JavaScript implementation, no frontend framework dependency

2. **Template Structure**
   ```
   templates/
   ├── base.html.j2           # Base template with common layout
   ├── weekly/
   │   └── index.html.j2      # Weekly report template
   └── components/            # Reusable components
   ```

3. **Base Template Design**
   ```html
   <!DOCTYPE html>
   <html lang="zh-Hant-TW">
   <head>
     <meta charset="UTF-8">
     <meta name="viewport" content="width=device-width, initial-scale=1.0">
     <title>{% block title %}{% endblock %}</title>
     <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
     <link href="/css/common.css" rel="stylesheet">
     {% block extra_css %}{% endblock %}
   </head>
   <body>
     <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
       <!-- Navigation content -->
     </nav>

     <main class="container my-4">
       {% block content %}{% endblock %}
     </main>

     <footer class="bg-light py-3 mt-5">
       <!-- Footer content -->
     </footer>

     <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
     {% block extra_js %}{% endblock %}
   </body>
   </html>
   ```

4. **Data Presentation Features**
   - 使用卡片式設計展示資源資訊
   - 支援多種資料視圖（列表、網格）
   - 提供分類和標籤過濾
   - 實作響應式設計
   - 支援多語言（預設繁體中文）

5. **User Experience Optimization**
   - 實作響應式設計
   - 提供直觀的導航系統
   - 支援搜尋功能
   - 優化載入速度
   - 提供清晰的資料更新時間標示

## Consequences
### Positive
- 使用 Jinja2 模板系統提供更好的維護性
- 支援伺服器端渲染，提升首次載入效能
- 模組化設計便於擴展
- 響應式設計支援各種裝置
- 無需複雜的前端建置工具

### Negative
- 較難實現複雜的動態功能
- 伺服器端渲染可能增加伺服器負載
- 需要額外管理模板檔案
- 較難實現即時更新功能

## Related ADRs
- [ADR 0015](./0015-data-aggregation-and-storage.md)
- [ADR 0020](./0020-content-creator-insights.md)
- [ADR 0022](./0022-insights-and-search-integration.md)

## Date
2025/02/15