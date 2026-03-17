# 修复财务数据模拟数据问题

## TL;DR

> **Quick Summary**: 将 sina_finance.py 中的硬编码模拟财务数据替换为 baostock 获取的真实数据
> 
> **Deliverables**: 
> - 修复 4 个财务数据函数获取真实数据
> - 更新 requirements.txt 添加 baostock 依赖
> - 更新 default_config.py 配置
>
> **Estimated Effort**: Medium
> **Parallel Execution**: NO - 顺序执行
> **Critical Path**: Task 1 → Task 2 → Task 3 → Task 4

---

## Context

### Original Request
用户发现 `get_cashflow` 和 `get_income_statement` 返回的数据只截止到 2024Q3，实际上是硬编码的模拟数据。

### 问题分析

**当前状态**：`sina_finance.py` 中的 4 个财务数据函数返回硬编码模拟数据：
1. `get_sina_fundamentals` - 公司基本面（第 178-284 行）
2. `get_sina_balance_sheet` - 资产负债表（第 287-383 行）
3. `get_sina_income_statement` - 利润表（第 386-477 行）
4. `get_sina_cashflow` - 现金流量表（第 481-577 行）

**根本原因**：
- 这些函数内部直接返回硬编码字符串
- TODO 注释表明需要实现真实数据获取
- akshare 的财务报表 API 当前不稳定（返回 None）

**解决方案**：使用 baostock 获取真实财务数据
- baostock 已测试可用
- 支持利润表、资产负债表、现金流量表等
- 数据格式为财务指标，足以支撑基本面分析

### 验证结果

```
baostock 登录: success
利润表字段: ['code', 'pubDate', 'statDate', 'roeAvg', 'npMargin', 'gpMargin', 'netProfit', 'epsTTM', 'MBRevenue', 'totalShare', 'liqaShare']
资产负债表字段: ['code', 'pubDate', 'statDate', 'currentRatio', 'quickRatio', 'cashRatio', 'YOYLiability', 'liabilityToAsset', 'assetToEquity']
现金流量表字段: ['code', 'pubDate', 'statDate', 'CAToAsset', 'NCAToAsset', 'tangibleAssetToAsset', 'ebitToInterest', 'CFOToOR', 'CFOToNP', 'CFOToGr']
```

---

## Work Objectives

### Core Objective
将 sina_finance.py 中的模拟数据替换为 baostock 获取的真实数据

### Concrete Deliverables
- 修改 `tradingagents/dataflows/sina_finance.py`
- 更新 `requirements.txt` 添加 baostock
- 测试验证真实数据获取

### Definition of Done
- [x] 运行 `test_glm.py` 能获取到真实财务数据
- [x] 数据日期不再是硬编码的 2024Q3

### Must Have
- 使用 baostock 获取真实数据
- 保留 fallback 机制（baostock 失败时提示用户）
- 数据格式为 Markdown 表格

### Must NOT Have
- 不再返回硬编码的模拟数据
- 不破坏现有 API 接口

---

## Verification Strategy

### QA Policy
每个任务完成后通过运行测试验证：

```bash
python3 -c "
from tradingagents.dataflows.sina_finance import get_sina_fundamentals, get_sina_balance_sheet, get_sina_income_statement, get_sina_cashflow

print('测试 get_sina_fundamentals...')
print(get_sina_fundamentals('sh600941')[:500])

print('\n测试 get_sina_income_statement...')
print(get_sina_income_statement('sh600941')[:500])
"
```

---

## Execution Strategy

### Dependency Matrix

- **1**: — — 2
- **2**: 1 — 3
- **3**: 2 — 4
- **4**: 3 — F1

---

## TODOs

- [x] 1. 添加 baostock 依赖和导入

  **What to do**:
  - 在 `requirements.txt` 添加 `baostock`
  - 在 `sina_finance.py` 头部添加 baostock 导入
  - 添加 BAOSTOCK_AVAILABLE 全局变量检测是否可用

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocks**: Task 2

  **References**:
  - `requirements.txt` - 添加依赖
  - `tradingagents/dataflows/sina_finance.py:1-15` - 导入位置

  **Acceptance Criteria**:
  - [ ] `pip list | grep baostock` 显示已安装
  - [ ] `import baostock as bs` 不报错

  **QA Scenarios**:
  ```
  Scenario: baostock 导入成功
    Tool: Bash
    Steps:
      1. python3 -c "import baostock as bs; print(bs.__version__)"
    Expected Result: 输出版本号
    Evidence: .sisyphus/evidence/task-1-baostock-import.txt
  ```

---

- [x] 2. 实现 `_get_baostock_financial_data` 辅助函数

  **What to do**:
  - 创建辅助函数统一处理 baostock 数据获取
  - 支持 profit_data, balance_data, cash_flow_data 三种类型
  - 获取最近 4 个季度的数据
  - 转换为 Markdown 表格格式

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocked By**: Task 1
  - **Blocks**: Task 3, 4

  **References**:
  - `tradingagents/dataflows/sina_finance.py` - 添加函数位置

  **Acceptance Criteria**:
  - [ ] 函数能获取利润表、资产负债表、现金流量表数据
  - [ ] 返回格式为 Markdown 表格
  - [ ] 失败时返回 None 或错误信息

  **QA Scenarios**:
  ```
  Scenario: 获取利润表数据
    Tool: Bash
    Steps:
      1. 调用 _get_baostock_financial_data('sh.600941', 'profit')
    Expected Result: 返回包含 roeAvg, netProfit 等字段的 Markdown 表格
    Evidence: .sisyphus/evidence/task-2-profit-data.txt
  ```

---

- [x] 3. 重写 4 个财务数据函数

  **What to do**:
  - 修改 `get_sina_fundamentals` 使用 baostock + akshare 获取真实数据
  - 修改 `get_sina_balance_sheet` 调用辅助函数
  - 修改 `get_sina_income_statement` 调用辅助函数
  - 修改 `get_sina_cashflow` 调用辅助函数
  - 保留 fallback：baostock 不可用时返回提示信息

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocked By**: Task 2
  - **Blocks**: Task 4

  **References**:
  - `tradingagents/dataflows/sina_finance.py:178-577` - 需要重写的函数

  **Must NOT do**:
  - 不要删除函数签名（保持 API 兼容）
  - 不要删除 fallback 机制

  **Acceptance Criteria**:
  - [ ] 4 个函数返回真实数据
  - [ ] 数据日期为最近 4 个季度
  - [ ] baostock 不可用时返回明确提示

  **QA Scenarios**:
  ```
  Scenario: 获取真实财务数据
    Tool: Bash
    Steps:
      1. from tradingagents.dataflows.sina_finance import get_sina_cashflow
      2. result = get_sina_cashflow('sh600941')
      3. 检查结果是否包含 "baostock" 或真实数据标识
    Expected Result: 不包含 "示例数据"、"模拟数据" 字样
    Evidence: .sisyphus/evidence/task-3-real-data.txt
  ```

---

- [x] 4. 集成测试

  **What to do**:
  - 运行 test_glm.py 验证完整流程
  - 验证数据获取成功
  - 验证报告生成正常

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocked By**: Task 3

  **References**:
  - `test_glm.py` - 测试脚本

  **Acceptance Criteria**:
  - [ ] `python test_glm.py` 运行成功
  - [ ] 生成的报告包含真实财务数据

  **QA Scenarios**:
  ```
  Scenario: 完整流程测试
    Tool: Bash
    Steps:
      1. 运行 test_glm.py（或简化测试）
      2. 检查生成的 Markdown 报告
    Expected Result: 财务数据不为模拟数据
    Evidence: .sisyphus/evidence/task-4-integration.txt
  ```

---

## Final Verification Wave

- [x] F1. 数据真实性验证
  调用所有 4 个函数，验证返回数据不是模拟数据

- [x] F2. 代码质量检查
  运行 mypy 和 ruff 检查代码质量

---

## Commit Strategy

- **Commit 1**: `feat(dataflows): add baostock dependency for real financial data`
  - Files: requirements.txt, sina_finance.py (imports)
  
- **Commit 2**: `feat(dataflows): replace mock financial data with baostock`
  - Files: sina_finance.py

---

## Success Criteria

### Verification Commands
```bash
# 测试财务数据获取
python3 -c "
from tradingagents.dataflows.sina_finance import get_sina_income_statement
result = get_sina_income_statement('sh600941')
assert '示例' not in result and '模拟' not in result, 'Still using mock data'
print('OK: Real data returned')
"
```

### Final Checklist
- [x] All 4 financial functions return real data
- [x] baostock dependency added
- [x] No mock data in production flow
