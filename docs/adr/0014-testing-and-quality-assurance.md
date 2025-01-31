# ADR 0014: Testing and Quality Assurance Strategy

## Status
Accepted

## Context
根據 ADR 0010 和 ADR 0013 的要求，我們需要建立完整的測試和程式碼品質保證策略。這包括自動化測試、程式碼格式化、靜態分析和覆蓋率要求。

## Decision

### 1. 測試框架和工具
- 使用 pytest 作為主要測試框架
- pytest-asyncio 用於非同步測試
- pytest-cov 用於測試覆蓋率報告
- pytest-mock 用於模擬物件
- pytest-timeout 用於測試超時控制
- aioresponses 用於模擬 HTTP 請求
- freezegun 用於時間相關測試

### 2. 程式碼品質工具
- black：程式碼格式化
  ```toml
  [tool.black]
  line-length = 100
  target-version = ["py39"]
  ```

- ruff：程式碼檢查
  ```toml
  [tool.ruff]
  select = ["E", "W", "F", "I", "C", "B", "UP"]
  line-length = 100
  ```

- mypy：型別檢查
  ```toml
  [tool.mypy]
  disallow_untyped_defs = true
  strict_equality = true
  ```

### 3. 測試結構
```
tests/
├── unit/                  # 單元測試
│   ├── clients/          # API 客戶端測試
│   ├── services/         # 服務層測試
│   └── models/           # 資料模型測試
├── integration/          # 整合測試
│   ├── api/             # API 整合測試
│   └── storage/         # 儲存整合測試
└── fixtures/            # 測試資料
    ├── responses/       # API 回應資料
    └── configs/         # 測試設定
```

### 4. 測試規範
1. 單元測試：
   - 每個公開方法至少一個測試案例
   - 使用 pytest.mark 標記測試類型
   - 使用 pytest fixtures 共享測試資料

2. 整合測試：
   - 測試完整的資料流程
   - 模擬外部 API 回應
   - 驗證資料轉換和儲存

3. 覆蓋率要求：
   - 整體覆蓋率至少 80%
   - 核心邏輯覆蓋率至少 90%
   - 使用 pytest-cov 產生報告

### 5. CI/CD 整合
```yaml
# 在 GitHub Actions 中執行
- name: Run Tests
  run: |
    pytest --cov=scraper --cov-report=xml
    
- name: Check Code Quality
  run: |
    black --check .
    ruff check .
    mypy scraper/
```

## Consequences

### Positive
- 確保程式碼品質和可靠性
- 自動化測試減少人為錯誤
- 清晰的測試結構便於維護
- 型別檢查提早發現問題
- 統一的程式碼風格

### Negative
- 需要額外的開發時間
- 測試維護成本增加
- CI/CD 執行時間增加
- 開發者需要學習新工具

## Related ADRs
- [ADR 0010](./0010-code-refactoring-principles.md)
- [ADR 0013](./0013-codebase-restructuring.md)

## Date
01/31/2025 