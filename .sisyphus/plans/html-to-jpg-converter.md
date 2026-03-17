# HTML 转 JPG 图片转换器

## TL;DR

> **Quick Summary**: 开发一个独立 CLI 命令，使用 imgkit + wkhtmltoimage 将 HTML 报告转换为 750px 宽度的 JPG 图片，智能分段保存到本地。
> 
> **Deliverables**:
> - `tradingagents/utils/html_to_jpg.py` - 核心转换模块
> - `tradingagents/utils/__init__.py` - 包初始化文件
> - CLI 命令 `convert-jpg` - 独立触发入口
> - 测试文件 `tests/test_html_to_jpg.py`
> - 测试数据 `tests/fixtures/sample_report.html`
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: T1(TDD基础) → T4(核心逻辑) → T6(CLI集成) → T8(验证)

---

## Context

### Original Request
用户希望将 HTML 报告转换为适合手机阅读的 JPG 图片，方便分享。要求智能分段，输出保存到本地。

### Interview Summary
**Key Discussions**:
- 技术选型: imgkit + wkhtmltoimage（放弃 Playwright）
- 图片宽度: 750px（2倍放大，适合高分辨率手机）
- 图片质量: 75-85%（中等质量，平衡文件大小和清晰度）
- 分段方式: 智能分段（按章节分割）
- 触发方式: 独立 CLI 命令
- 测试策略: TDD（测试优先）

### Metis Review
**Identified Gaps** (addressed):
- **路径假设错误**: 实际 HTML 保存在 `reports/` 目录，不是 `results/{ticker}/{date}/reports/`
- **HTML结构识别**: 使用 `<div class="section">` 而不是 `<section>` 标签
- **CLI框架**: 使用 `typer` 而不是 `argparse`
- **依赖检查**: 必须检查 wkhtmltoimage 是否安装

**Critical Guardrails Applied**:
- 创建 `tradingagents/utils/` 目录（目前不存在）
- 使用 `shutil.which()` 检查依赖
- 输出到与 HTML 相同目录
- 命名模式: `{original_name}_01.jpg`

---

## Work Objectives

### Core Objective
创建一个独立的 HTML 转 JPG 工具，支持智能分段，方便用户在手机上查看和分享交易分析报告。

### Concrete Deliverables
- `tradingagents/utils/__init__.py` - 空包初始化文件
- `tradingagents/utils/html_to_jpg.py` - 核心转换逻辑
- `cli/main.py` 修改 - 添加 `convert-jpg` 命令
- `tests/test_html_to_jpg.py` - 单元测试
- `tests/fixtures/sample_report.html` - 测试数据

### Definition of Done
- [ ] `python -m cli.main convert-jpg reports/test.html` 成功生成 JPG 图片
- [ ] 所有测试通过: `pytest tests/test_html_to_jpg.py`
- [ ] 未安装 wkhtmltoimage 时显示清晰错误提示

### Must Have
- 检查 wkhtmltoimage 是否安装
- 按章节智能分段
- 输出到 HTML 同目录
- 清晰的错误提示

### Must NOT Have (Guardrails)
- 不修改现有 `analyze()` 命令
- 不创建新的日志基础设施（使用 `console.print()`）
- 不支持批量处理（单文件输入）
- 不支持其他图片格式（仅 JPG）

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed.

### Test Decision
- **Infrastructure exists**: YES (pytest)
- **Automated tests**: TDD
- **Framework**: pytest

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (TDD Red Phase — 测试先行):
├── Task 1: 创建测试目录和 fixtures [quick]
├── Task 2: 编写测试用例 (失败状态) [quick]
└── Task 3: 更新 requirements.txt [quick]

Wave 2 (核心实现):
├── Task 4: 创建 html_to_jpg.py 核心模块 [unspecified-high]
├── Task 5: 实现章节分割逻辑 [unspecified-high]
└── Task 6: 添加 CLI 命令集成 [quick]

Wave 3 (验证与文档):
├── Task 7: 运行测试验证 [quick]
└── Task 8: 更新 AGENTS.md 文档 [quick]

Critical Path: T1 → T2 → T4 → T5 → T6 → T7
Parallel Speedup: Wave 1 可并行执行 T1, T3
Max Concurrent: 3
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|------------|--------|
| 1 | — | 2, 4 |
| 2 | 1 | 4, 5 |
| 3 | — | 4 |
| 4 | 1, 2, 3 | 5, 6 |
| 5 | 4 | 6, 7 |
| 6 | 4, 5 | 7 |
| 7 | 5, 6 | 8 |
| 8 | 7 | — |

### Agent Dispatch Summary

- **Wave 1**: T1-T3 → `quick`
- **Wave 2**: T4-T5 → `unspecified-high`, T6 → `quick`
- **Wave 3**: T7-T8 → `quick`

---

## TODOs

- [x] 1. 创建测试目录和 fixtures

  **What to do**:
  - 创建 `tests/fixtures/` 目录（如果不存在）
  - 创建 `tests/fixtures/sample_report.html` 测试用 HTML 文件
  - HTML 文件需包含：header、decision card、多个 section、footer
  - 创建 `tradingagents/utils/__init__.py` 空文件

  **Must NOT do**:
  - 不要创建复杂的 HTML，简单结构即可
  - 不要添加额外的测试数据文件

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 创建目录和简单文件，工作量小
  - **Skills**: []
    - 无需特殊技能

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 3)
  - **Blocks**: Task 2, Task 4
  - **Blocked By**: None

  **References**:
  - `tradingagents/graph/report_generator.py:823-991` - 后备 HTML 模板结构
  - `tests/` - 现有测试目录结构

  **Acceptance Criteria**:
  - [ ] `tests/fixtures/sample_report.html` 文件存在
  - [ ] `tradingagents/utils/__init__.py` 文件存在
  - [ ] HTML 文件包含至少 2 个 `<div class="section">` 元素

  **QA Scenarios**:
  ```
  Scenario: 测试文件创建成功
    Tool: Bash
    Steps:
      1. test -f tests/fixtures/sample_report.html
      2. test -f tradingagents/utils/__init__.py
    Expected Result: 两个命令都返回 exit code 0
    Evidence: .sisyphus/evidence/task-01-files-created.txt
  ```

  **Commit**: NO (与 Task 2 一起提交)

---

- [x] 2. 编写测试用例 (TDD Red Phase)

  **What to do**:
  - 创建 `tests/test_html_to_jpg.py`
  - 编写以下测试用例（预期失败）:
    1. `test_convert_success` - 成功转换测试
    2. `test_missing_wkhtmltoimage` - 依赖缺失测试
    3. `test_file_not_found` - 文件不存在测试
    4. `test_segmentation` - 分段测试
  - 使用 pytest fixture 提供测试数据路径

  **Must NOT do**:
  - 不要实现实际功能代码
  - 不要跳过测试用例

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 编写测试代码，逻辑清晰
  - **Skills**: []
    - 无需特殊技能

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (依赖 Task 1)
  - **Blocks**: Task 4
  - **Blocked By**: Task 1

  **References**:
  - `tests/test_report_generator.py` - 现有测试模式
  - `tradingagents/graph/report_generator.py` - ReportGenerator 类结构

  **Acceptance Criteria**:
  - [ ] `tests/test_html_to_jpg.py` 文件存在
  - [ ] 包含 4 个测试函数
  - [ ] `pytest tests/test_html_to_jpg.py` 执行失败（功能未实现）

  **QA Scenarios**:
  ```
  Scenario: 测试文件存在且包含预期测试
    Tool: Bash
    Steps:
      1. test -f tests/test_html_to_jpg.py
      2. grep -c "def test_" tests/test_html_to_jpg.py
    Expected Result: 文件存在，测试函数数量 >= 4
    Evidence: .sisyphus/evidence/task-02-tests-created.txt
  ```

  **Commit**: YES
  - Message: `test: add html_to_jpg test cases with fixtures`
  - Files: `tests/test_html_to_jpg.py`, `tests/fixtures/sample_report.html`, `tradingagents/utils/__init__.py`

---

- [x] 3. 更新 requirements.txt

  **What to do**:
  - 在 `requirements.txt` 添加 `imgkit` 依赖
  - 保持现有依赖顺序

  **Must NOT do**:
  - 不要删除或修改现有依赖
  - 不要添加 wkhtmltoimage（系统级依赖，不在此管理）

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 单行添加，工作量极小
  - **Skills**: []
    - 无需特殊技能

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 1)
  - **Blocks**: Task 4
  - **Blocked By**: None

  **References**:
  - `requirements.txt` - 现有依赖列表

  **Acceptance Criteria**:
  - [ ] `requirements.txt` 包含 `imgkit`
  - [ ] 现有依赖未被修改

  **QA Scenarios**:
  ```
  Scenario: 依赖已添加
    Tool: Bash
    Steps:
      1. grep "imgkit" requirements.txt
    Expected Result: 找到 imgkit 行
    Evidence: .sisyphus/evidence/task-03-requirements.txt
  ```

  **Commit**: NO (与 Task 4 一起提交)

---

- [x] 4. 创建 html_to_jpg.py 核心模块

  **What to do**:
  - 创建 `tradingagents/utils/html_to_jpg.py`
  - 实现核心功能:
    1. `check_wkhtmltoimage()` - 检查依赖是否安装
    2. `convert_html_to_jpg(html_path, output_dir, quality, width)` - 基本转换
    3. 错误处理: 依赖缺失、文件不存在
  - 使用 `shutil.which()` 检查 wkhtmltoimage
  - 使用 `imgkit` 进行转换
  - 配置: width=750, quality=80

  **Must NOT do**:
  - 不要实现分段逻辑（Task 5）
  - 不要添加 CLI 集成（Task 6）
  - 不要使用 logging，使用 `console.print()`

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 核心功能实现，需要仔细处理错误和边界情况
  - **Skills**: []
    - 无需特殊技能

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (依赖 Task 1, 2, 3)
  - **Blocks**: Task 5, Task 6
  - **Blocked By**: Task 1, Task 2, Task 3

  **References**:
  - `tradingagents/graph/report_generator.py:823-991` - HTML 结构参考
  - imgkit 文档: https://github.com/jarrekk/imgkit

  **Acceptance Criteria**:
  - [ ] `tradingagents/utils/html_to_jpg.py` 文件存在
  - [ ] `check_wkhtmltoimage()` 函数存在
  - [ ] `convert_html_to_jpg()` 函数存在
  - [ ] `pytest tests/test_html_to_jpg.py::test_convert_success` 通过
  - [ ] `pytest tests/test_html_to_jpg.py::test_missing_wkhtmltoimage` 通过
  - [ ] `pytest tests/test_html_to_jpg.py::test_file_not_found` 通过

  **QA Scenarios**:
  ```
  Scenario: 核心转换功能正常
    Tool: Bash
    Preconditions: wkhtmltoimage 已安装
    Steps:
      1. python -c "from tradingagents.utils.html_to_jpg import convert_html_to_jpg; convert_html_to_jpg('tests/fixtures/sample_report.html', 'tests/fixtures/')"
      2. ls tests/fixtures/sample_report.jpg
    Expected Result: 图片文件存在
    Evidence: .sisyphus/evidence/task-04-convert-success.jpg

  Scenario: 依赖缺失报错
    Tool: Bash
    Steps:
      1. python -c "from tradingagents.utils.html_to_jpg import check_wkhtmltoimage; print(check_wkhtmltoimage())"
    Expected Result: 返回 True 或 False
    Evidence: .sisyphus/evidence/task-04-dependency-check.txt
  ```

  **Commit**: YES
  - Message: `feat: add html_to_jpg module with wkhtmltoimage dependency check`
  - Files: `tradingagents/utils/html_to_jpg.py`, `requirements.txt`

---

- [x] 5. 实现章节分割逻辑

  **What to do**:
  - 在 `html_to_jpg.py` 添加 `segment_html_by_sections(html_content)` 函数
  - 使用 BeautifulSoup 解析 HTML
  - 按 `<div class="section">` 元素分割
  - 返回 HTML 片段列表
  - 修改 `convert_html_to_jpg()` 支持多图输出
  - 输出命名: `{original}_01.jpg`, `{original}_02.jpg`, ...

  **Must NOT do**:
  - 不要分割 `<div class="header">` 和 `<div class="decision">`
  - 不要创建过于复杂的分割规则
  - 不要处理嵌套 section

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 需要仔细处理 HTML 解析和分段逻辑
  - **Skills**: []
    - 无需特殊技能

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (依赖 Task 4)
  - **Blocks**: Task 6, Task 7
  - **Blocked By**: Task 4

  **References**:
  - `tradingagents/graph/report_generator.py:823-991` - HTML 结构
  - BeautifulSoup 文档: https://www.crummy.com/software/BeautifulSoup/bs4/doc/

  **Acceptance Criteria**:
  - [ ] `segment_html_by_sections()` 函数存在
  - [ ] `pytest tests/test_html_to_jpg.py::test_segmentation` 通过
  - [ ] 转换输出多张图片

  **QA Scenarios**:
  ```
  Scenario: 分段转换正常
    Tool: Bash
    Preconditions: wkhtmltoimage 已安装
    Steps:
      1. python -c "from tradingagents.utils.html_to_jpg import convert_html_to_jpg; convert_html_to_jpg('tests/fixtures/sample_report.html', 'tests/fixtures/')"
      2. ls tests/fixtures/sample_report_*.jpg | wc -l
    Expected Result: 输出 >= 2 张图片
    Evidence: .sisyphus/evidence/task-05-segmentation.txt
  ```

  **Commit**: YES
  - Message: `feat: add section-based segmentation for smart splitting`
  - Files: `tradingagents/utils/html_to_jpg.py`

---

- [x] 6. 添加 CLI 命令集成

  **What to do**:
  - 在 `cli/main.py` 添加 `convert_jpg` 命令
  - 使用 `@app.command(name="convert-jpg")` 装饰器
  - 参数: `html_file: str`, `--output-dir: str = None`, `--quality: int = 80`
  - 调用 `convert_html_to_jpg()` 函数
  - 使用 `console.print()` 输出状态

  **Must NOT do**:
  - 不要修改现有 `analyze()` 命令
  - 不要添加复杂的参数验证

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 简单的 CLI 集成，遵循现有模式
  - **Skills**: []
    - 无需特殊技能

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (依赖 Task 4, 5)
  - **Blocks**: Task 7
  - **Blocked By**: Task 4, Task 5

  **References**:
  - `cli/main.py:analyze()` - 现有命令模式
  - `cli/main.py` - typer 使用方式

  **Acceptance Criteria**:
  - [ ] `cli/main.py` 包含 `convert_jpg` 函数
  - [ ] `python -m cli.main convert-jpg --help` 显示帮助
  - [ ] CLI 命令可执行

  **QA Scenarios**:
  ```
  Scenario: CLI 命令可用
    Tool: Bash
    Steps:
      1. python -m cli.main convert-jpg --help
    Expected Result: 显示帮助信息，exit code 0
    Evidence: .sisyphus/evidence/task-06-cli-help.txt
  ```

  **Commit**: YES
  - Message: `feat: add convert-jpg CLI command`
  - Files: `cli/main.py`

---

- [x] 7. 运行测试验证

  **What to do**:
  - 运行 `pytest tests/test_html_to_jpg.py -v`
  - 确保所有测试通过
  - 修复失败的测试（如果有）

  **Must NOT do**:
  - 不要跳过测试
  - 不要修改测试用例来适应实现

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 运行测试，工作量小
  - **Skills**: []
    - 无需特殊技能

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (依赖 Task 5, 6)
  - **Blocks**: Task 8
  - **Blocked By**: Task 5, Task 6

  **References**:
  - `tests/test_html_to_jpg.py` - 测试文件

  **Acceptance Criteria**:
  - [ ] `pytest tests/test_html_to_jpg.py` 全部通过
  - [ ] 无测试跳过

  **QA Scenarios**:
  ```
  Scenario: 所有测试通过
    Tool: Bash
    Steps:
      1. pytest tests/test_html_to_jpg.py -v
    Expected Result: 所有测试通过，exit code 0
    Evidence: .sisyphus/evidence/task-07-tests-pass.txt
  ```

  **Commit**: NO (仅验证)

---

- [x] 8. 更新 AGENTS.md 文档

  **What to do**:
  - 在 `AGENTS.md` 添加新 CLI 命令说明
  - 包含: 命令用法、参数说明、依赖要求

  **Must NOT do**:
  - 不要修改现有内容
  - 不要添加过多细节

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 简单的文档更新
  - **Skills**: []
    - 无需特殊技能

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (依赖 Task 7)
  - **Blocks**: None
  - **Blocked By**: Task 7

  **References**:
  - `AGENTS.md` - 现有文档结构

  **Acceptance Criteria**:
  - [ ] `AGENTS.md` 包含 `convert-jpg` 命令说明

  **QA Scenarios**:
  ```
  Scenario: 文档已更新
    Tool: Bash
    Steps:
      1. grep "convert-jpg" AGENTS.md
    Expected Result: 找到命令说明
    Evidence: .sisyphus/evidence/task-08-docs-updated.txt
  ```

  **Commit**: YES
  - Message: `docs: update AGENTS.md with convert-jpg command`
  - Files: `AGENTS.md`

---

## Final Verification Wave (MANDATORY)

- [x] F1. **Plan Compliance Audit** — `oracle`
  验证所有 Must Have 已实现，所有 Must NOT Have 未实现。

- [x] F2. **Code Quality Review** — `unspecified-high`
  运行 `pytest` 和 `mypy`，检查代码质量。

- [x] F3. **Real Manual QA** — `unspecified-high`
  执行实际 HTML 转换，验证输出正确。

---

## Commit Strategy

- **1**: `test: add html_to_jpg test fixtures and failing tests`
- **2**: `feat: add html_to_jpg module with wkhtmltoimage dependency check`
- **3**: `feat: add section-based segmentation for smart splitting`
- **4**: `feat: add convert-jpg CLI command`
- **5**: `docs: update AGENTS.md with convert-jpg command`

---

## Success Criteria

### Verification Commands
```bash
# 测试
pytest tests/test_html_to_jpg.py -v

# 实际使用
python -m cli.main convert-jpg reports/sample.html

# 验证输出
ls reports/sample_*.jpg
```

### Final Checklist
- [x] 所有测试通过
- [x] CLI 命令可用
- [x] 错误提示清晰
- [x] 文档已更新
