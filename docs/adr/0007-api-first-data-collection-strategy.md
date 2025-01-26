# ADR 0007: API-First Data Collection Strategy

## Status
Accepted

## Context
在評估了各個 Minecraft 插件/模組平台後，我們發現有幾個主要平台提供了官方 API。使用官方 API 不僅可以避免違反使用條款，還能獲得更可靠和穩定的數據存取方式。

目前已確認提供 API 的平台有：
- Builtbybit (前身為 MC-Market)：提供 v1 API
- Polymart：提供完整的資源訪問 API
- CurseForge：提供項目查詢 API
- Modrinth：提供搜索和項目資訊 API

## Decision
我們將採用 "API 優先" 的數據收集策略：

1. **優先實現的 API 整合**：
   - Modrinth API
   - CurseForge API
   - Polymart API
   - Builtbybit API（需要授權）

2. **API 實現方式**：
   - 在 `/scraper/api_clients/` 目錄下為每個平台建立專門的 API 客戶端
   - 實現統一的數據模型轉換層
   - 使用 API 密鑰管理系統處理認證

3. **數據收集頻率**：
   - 每日更新一次
   - 遵守各平台的 API 速率限制
   - 實現錯誤重試機制

## Consequences
### 正面影響
- 完全合規的數據收集方式
- 更可靠的數據來源
- 減少維護成本
- 更好的錯誤處理能力
- 可能獲得更多元數據（如下載統計、評分等）

### 負面影響
- 需要管理多個 API 密鑰
- 可能需要處理 API 速率限制
- 需要適應不同 API 的數據格式
- 部分 API 可能需要付費使用

## Related ADRs
- [ADR 0006](./0006-data-scraping-policy.md)
- [ADR 0005](./0005-github-actions-for-ci-cd.md)
- [ADR 0001](./0001-use-python-for-scraper.md)

## Date
January 26, 2025
