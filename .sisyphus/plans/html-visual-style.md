# HTML 报告视觉风格调整 — 经济学人杂志风

## TL;DR

> **Quick Summary**: 将 HTML 报告的视觉风格从当前的"简洁清爽浅色主题"调整为"经济学人杂志风"（冷色调蓝灰青、衬线标题、精致表格、编辑排版感），通过重写 LLM prompt 中的样式描述实现。
> 
> **Deliverables**:
> - 重写 `_build_html_prompt()` 方法中的视觉风格描述块（约 L570-707）
> - 更新 `tests/fixtures/sample_report.html` 的 CSS 和颜色以匹配新风格
> - 保持所有结构性约束和技术约束不变
> 
> **Estimated Effort**: Short (2-3 hours)
> **Parallel Execution**: YES - 2 waves
> **Critical Path**: Task 1 (prompt 重写) → Task 2 (fixture 更新) → Task 3 (结构验证)

---

## Context

### Original Request
用户希望调整最终 HTML 报告的视觉风格，从当前的"白底黑字简洁浅色主题"改为更高级的杂志风格。

### Interview Summary
**关键设计决策**:
- **风格方向**: 经济学人风格（深蓝标题、图表驱动、英伦克制优雅）
- **配色方案**: 冷色调蓝灰青（冷灰背景 + 深蓝文字 + 蓝色/青色强调）
- **决策卡配色**: 冷化语义色（BUY=青绿/薄荷、SELL=玫红/冷红、HOLD=石板蓝）
- **字体**: 标题衬线（Georgia）+ 正文无衬线（系统字体栈）
- **数据展示**: 精致表格（条纹行、圆角、强调行）
- **布局**: 保持手机 375px 固定宽度
- **范围**: 中等改造，仅调整 LLM prompt 和 test fixture

**Scope Boundaries**:
- INCLUDE: `_build_html_prompt()` 样式描述重写 + `sample_report.html` CSS 更新
- EXCLUDE: 后备模板 `_generate_fallback_html()`、`html_to_jpg.py`、合规模块、Markdown 生成逻辑

### Metis Review
**Identified Gaps** (已全部解决):
1. ✅ 决策卡配色语义 → 用户选择"冷化语义色"
2. ✅ 衬线字体中文渲染 → 用户选择"标题衬线+正文无衬线"
3. ✅ sample_report.html DOM 结构 → 仅更新 CSS，保持 DOM 不变
4. ✅ Prompt 语言 → 保持中文，风格术语可适当用英文

**关键风险**:
- R1: LLM 非确定性 → prompt 必须极其具体（hex 值、像素值、CSS 规则），不用模糊描述
- R2: 颜色对比度 → 冷灰背景 + 深蓝文字，需确保 WCAG 合规
- R3: 字体可用性 → Georgia 字体栈必须有安全后备

---

## Work Objectives

### Core Objective
将 HTML 报告的视觉风格从"简洁清爽浅色"调整为"经济学人杂志风"，通过重写 LLM prompt 实现，同时确保 HTML 结构约束和分段截图兼容性不受影响。

### Concrete Deliverables
- `tradingagents/graph/report_generator.py` — `_build_html_prompt()` 方法的样式描述块重写
- `tests/fixtures/sample_report.html` — CSS 更新以匹配新风格配色

### Definition of Done
- [ ] `_build_html_prompt()` 输出的 prompt 包含完整的经济学人风格样式描述
- [ ] Prompt 中所有结构性约束（container/section/h2、375px、无 JS）保持不变
- [ ] `sample_report.html` DOM 结构不变，CSS 配色和样式更新
- [ ] `html_to_jpg.py` 分段逻辑仍能正常处理新风格的 fixture

### Must Have
- 冷色调配色方案（蓝灰青系）
- 衬线标题字体 + 无衬线正文字体
- 精致表格样式描述（条纹行、圆角、强调行）
- 冷化语义色的决策卡（BUY=薄荷绿、SELL=冷红、HOLD=石板蓝）
- 编辑排版感（更多留白、细线分隔、视觉层次）
- WCAG 对比度合规的颜色配对

### Must NOT Have (Guardrails)
- ❌ 不修改 `_generate_fallback_html()` 方法
- ❌ 不修改 `html_to_jpg.py` 分段逻辑
- ❌ 不修改合规检查模块
- ❌ 不修改 HTML 结构约束（container > section > h2）
- ❌ 不引入外部 CSS/JS 框架
- ❌ 不使用模糊描述如"类似经济学人"代替具体的 hex/像素值
- ❌ 不改变技术约束（无 JS、内联 CSS、UTF-8）
- ❌ 不改变 `error_feedback` 处理逻辑（L709-717）

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed.

### Test Decision
- **Infrastructure exists**: YES (pytest, conda env)
- **Automated tests**: None (user preference)
- **Framework**: pytest (existing)
- **Verification**: Structural assertions, not visual tests

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Prompt validation**: Use Bash (python REPL) — Import module, call method, assert output contains required strings
- **DOM validation**: Use Bash (python + BeautifulSoup) — Parse fixture, assert structure intact
- **Segmentation validation**: Use Bash (python) — Call segment function, assert output count

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately - core changes):
├── Task 1: 重写 LLM prompt 样式描述块 [unspecified-high]
├── Task 2: 更新 sample_report.html CSS 配色 [quick]
└── Task 3: 更新 sample_report.html 表格和决策卡样式 [quick]

Wave 2 (After Wave 1 - structural verification):
├── Task 4: 验证 prompt 结构约束完整性 [quick]
├── Task 5: 验证 fixture DOM 结构和分段兼容性 [quick]

Wave FINAL (After ALL tasks — parallel reviews):
├── Task F1: Plan compliance audit [oracle]
├── Task F2: Code quality review [unspecified-high]
├── Task F3: Real manual QA [unspecified-high]
├── Task F4: Scope fidelity check [deep]
-> Present results -> Get explicit user okay

Critical Path: Task 1 → Task 4 → Task 5 → F1-F4 → user okay
Parallel Speedup: ~50% faster than sequential
Max Concurrent: 3 (Wave 1)
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|-----------|--------|
| 1    | None      | 4      |
| 2    | None      | 5      |
| 3    | 2         | 5      |
| 4    | 1         | F1-F4  |
| 5    | 2, 3      | F1-F4  |

### Agent Dispatch Summary

- **Wave 1**: 3 tasks — T1 → `unspecified-high`, T2 → `quick`, T3 → `quick`
- **Wave 2**: 2 tasks — T4 → `quick`, T5 → `quick`
- **FINAL**: 4 — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [x] 1. 重写 LLM prompt 样式描述块

  **What to do**:
  - 重写 `tradingagents/graph/report_generator.py` 中 `_build_html_prompt()` 方法的样式描述部分（约 L570-707）
  - 将当前"简洁清爽浅色主题"描述替换为"经济学人杂志风"描述
  - 新配色方案（具体 hex 值）：
    * 页面背景：冷灰 `#F0F2F5`（非纯白）
    * 主文字：深蓝 `#1A2B4A`（非纯黑）
    * 次文字：中灰蓝 `#5A6B82`
    * 强调色：青蓝 `#2D6A9F`
    * 分隔线：浅灰蓝 `#D5DBE3`
    * 表格条纹：交替 `#F5F7FA` / `#FFFFFF`
    * 表格头背景：深灰蓝 `#E8ECF2`
  - 决策卡冷化语义色：
    * BUY：薄荷/青绿 — 背景 `#E0F2F1`，边框 `#00897B`，文字 `#1A2B4A`
    * SELL：冷红/玫红 — 背景 `#FFEBEE`，边框 `#C62828`，文字 `#1A2B4A`
    * HOLD：石板蓝 — 背景 `#E3F2FD`，边框 `#1565C0`，文字 `#1A2B4A`
  - 字体方案：
    * 标题（H1/H2）：`Georgia, "Times New Roman", "Noto Serif SC", "STSong", serif`
    * 正文：`-apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", sans-serif`
  - 精致表格样式描述：
    * 圆角 6px 边框
    * 条纹行（交替浅灰蓝背景）
    * 表头深灰蓝背景 + 深蓝粗体文字
    * 数据行 hover 强调色提示
  - 编辑排版感：
    * 更多留白（段落间距 28px，标题上方间距 36px）
    * 细线分隔（1px `#D5DBE3`）代替粗边框
    * H2 标题下方 2px 底线（颜色 `#2D6A9F`）
    * 引用/高亮框使用浅青蓝背景 `#E8F4F8` + 1px 青蓝边框
  - 必须保持不变的内容（逐字保留）：
    * HTML 结构约束段落（L614-631 的 container > section > h2 规则）
    * 技术限制段落（L606-612 的内联 CSS、无 JS、无外部文件、UTF-8）
    * viewport meta 设置（width=375）
    * 375px/343px 尺寸值
    * error_feedback 处理逻辑（L709-717）

  **Must NOT do**:
  - 不修改 `_generate_fallback_html()` 方法
  - 不修改 HTML 结构约束文字
  - 不修改技术限制文字
  - 不修改 error_feedback 部分
  - 不使用模糊描述代替具体 hex/像素值
  - 不引入外部 CSS/JS 框架的提及

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 需要仔细阅读大文件（1158行）并精确替换约178行文本块，同时保持多个约束段落不变。需要深入理解当前 prompt 结构。
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: 不需要——修改 Python 文件中的文本字符串，不是前端代码

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3)
  - **Blocks**: Task 4
  - **Blocked By**: None (can start immediately)

  **References** (CRITICAL):

  **Pattern References** (existing code to follow):
  - `tradingagents/graph/report_generator.py:542-718` — 整个 `_build_html_prompt()` 方法，理解当前 prompt 的完整结构
  - `tradingagents/graph/report_generator.py:570-707` — 需要重写的样式描述核心块（约178行）
  - `tradingagents/graph/report_generator.py:606-612` — 技术限制约束，必须逐字保留
  - `tradingagents/graph/report_generator.py:614-631` — HTML 结构约束，必须逐字保留
  - `tradingagents/graph/report_generator.py:709-717` — error_feedback 处理，必须逐字保留

  **API/Type References**:
  - `tradingagents/graph/report_generator.py:796-858` — `generate_html_report_with_llm()` 确认 prompt 输入输出契约
  - `tradingagents/graph/report_generator.py:743-794` — `_call_llm_for_html()` 确认 LLM 如何消费 prompt

  **External References**:
  - WCAG 2.1 对比度: `#1A2B4A` on `#F0F2F5` ≈ 10:1（合规）; `#5A6B82` on `#F0F2F5` ≈ 4.8:1（合规）

  **Acceptance Criteria**:

  **QA Scenarios:**

  ```
  Scenario: Prompt 结构约束完整性验证
    Tool: Bash (python REPL)
    Preconditions: report_generator.py 已修改
    Steps:
      1. conda activate tradingagents
      2. python -c "
         from tradingagents.graph.report_generator import ReportGenerator
         rg = ReportGenerator.__new__(ReportGenerator)
         prompt = rg._build_html_prompt('# NVDA - NVIDIA 交易分析报告\nTest content', company_name='NVIDIA')
         checks = [
             ('375px' in prompt, '375px layout'),
             ('343px' in prompt, '343px content area'),
             ('<div class=\"container\">' in prompt, 'container div'),
             ('<section>' in prompt, 'section tag'),
             ('<h2>' in prompt, 'h2 tag'),
             ('严禁使用任何 JavaScript' in prompt, 'no-JS rule'),
             ('<style>' in prompt, 'inline CSS rule'),
             ('utf-8' in prompt, 'UTF-8 encoding'),
             ('#F0F2F5' in prompt, 'cold gray background'),
             ('#1A2B4A' in prompt, 'deep blue text'),
             ('#2D6A9F' in prompt, 'accent cyan-blue'),
             ('Georgia' in prompt, 'serif heading font'),
             ('#E0F2F1' in prompt, 'BUY mint bg'),
             ('#FFEBEE' in prompt, 'SELL cold red bg'),
             ('#E3F2FD' in prompt, 'HOLD slate blue bg'),
         ]
         for ok, desc in checks: print(f'  {\"✅\" if ok else \"❌\"} {desc}')
         assert all(ok for ok, _ in checks), 'FAILED'
         print('All checks passed!')
         "
    Expected Result: 15/15 checks pass
    Failure Indicators: 任何一个 check 为 ❌
    Evidence: .sisyphus/evidence/task-1-prompt-structure-check.txt

  Scenario: error_feedback 处理保留验证
    Tool: Bash (python REPL)
    Preconditions: report_generator.py 已修改
    Steps:
      1. conda activate tradingagents
      2. python -c "
         from tradingagents.graph.report_generator import ReportGenerator
         rg = ReportGenerator.__new__(ReportGenerator)
         prompt = rg._build_html_prompt('# Test', error_feedback=['Missing closing tag'], company_name='TestCorp')
         assert 'Missing closing tag' in prompt, 'error_feedback not preserved'
         assert '上一次生成验证失败' in prompt, 'error section header missing'
         print('✅ error_feedback handling preserved')
         "
    Expected Result: error_feedback 机制完整保留
    Evidence: .sisyphus/evidence/task-1-error-feedback-check.txt
  ```

  **Commit**: YES
  - Message: `style(report): restyle LLM prompt to Economist magazine style`
  - Files: `tradingagents/graph/report_generator.py`

- [x] 2. 更新 sample_report.html CSS 配色

  **What to do**:
  - 更新 `tests/fixtures/sample_report.html` 的 `<style>` 标签中的颜色值
  - 替换以下配色：
    * `background-color: #FFFFFF` → `#F0F2F5`（冷灰背景）
    * `color: #1A1A1A` → `#1A2B4A`（深蓝文字）
    * `color: #666666` → `#5A6B82`（中灰蓝次要文字）
    * `color: #333333` → `#1A2B4A`（深蓝标题）
    * `color: #444444` → `#5A6B82`（中灰蓝 H3）
    * `border-bottom: 2px solid #F0F0F0` → `2px solid #2D6A9F`（H2 青蓝底线）
    * `border: 1px solid #E0E0E0` → `1px solid #D5DBE3`（表格/分隔线浅灰蓝）
    * `background-color: #F5F5F5` → `#E8ECF2`（表头深灰蓝背景）
    * `background-color: #F9F9F9` → `#E8F4F8`（高亮框浅青蓝）
    * `background-color: #F0F0F0` → `#E8ECF2`（section-tag 背景）
    * 决策卡背景: `#E8F5E9` → `#E0F2F1`（BUY 薄荷绿），边框 `#2E7D32` → `#00897B`
  - 更新字体栈：
    * H1/H2 font-family → `Georgia, "Times New Roman", "Noto Serif SC", "STSong", serif`
    * Body font-family 保持当前系统字体栈不变

  **Must NOT do**:
  - 不修改 DOM 结构（不增删改任何 HTML 元素或 class）
  - 不修改内容文字
  - 不添加新的 CSS 规则（仅替换颜色值和字体栈）

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 简单的颜色值替换操作，不涉及复杂逻辑
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3)
  - **Blocks**: Task 5
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `tests/fixtures/sample_report.html:8-184` — 当前 CSS `<style>` 块，需要逐项替换颜色
  - `tests/fixtures/sample_report.html:89-115` — 决策卡样式，需要替换 BUY/SELL/HOLD 颜色

  **Test References**:
  - `tests/test_html_to_jpg.py` — 使用 sample_report.html 作为 fixture，确认 DOM 结构不能改变

  **Acceptance Criteria**:

  **QA Scenarios:**

  ```
  Scenario: Fixture 配色值验证
    Tool: Bash (python + grep)
    Preconditions: sample_report.html 已修改
    Steps:
      1. python -c "
         html = open('tests/fixtures/sample_report.html').read()
         new_colors = ['#F0F2F5', '#1A2B4A', '#5A6B82', '#2D6A9F', '#D5DBE3', '#E0F2F1', '#E8F4F8']
         old_colors = ['#FFFFFF', '#1A1A1A', '#666666', '#E0E0E0']
         for c in new_colors: assert c in html, f'Missing new color {c}'
         # Verify old main colors are gone (except in fallback which we don't touch)
         for c in ['#1A1A1A']: assert c not in html, f'Old color {c} still present'
         print('✅ Color values updated correctly')
         "
    Expected Result: 新配色值存在，旧主配色已替换
    Evidence: .sisyphus/evidence/task-2-color-check.txt
  ```

  **Commit**: YES (groups with Task 3)
  - Message: `style(fixture): update sample_report.html CSS to match Economist palette`
  - Files: `tests/fixtures/sample_report.html`

- [x] 3. 更新 sample_report.html 表格和决策卡样式

  **What to do**:
  - 在 `tests/fixtures/sample_report.html` 的 `<style>` 中添加精致表格样式：
    * `table { border-radius: 6px; overflow: hidden; }` — 圆角表格
    * `tr:nth-child(even) td { background-color: #F5F7FA; }` — 条纹行
    * `th { background-color: #E8ECF2; color: #1A2B4A; font-weight: bold; }` — 深灰蓝表头
    * `border-bottom: 1px solid #D5DBE3` 代替 `#E0E0E0` — 浅灰蓝分隔
  - 更新决策卡样式：
    * `.decision-card { background-color: #E0F2F1; border-left: 4px solid #00897B; }` — BUY 薄荷绿
    * `.decision-label { color: #00897B; }` — BUY 标签色
  - 更新编辑排版细节：
    * `.highlight-box { background-color: #E8F4F8; border: 1px solid #2D6A9F; }` — 青蓝高亮框
    * `p { margin-bottom: 28px; }` 代替 24px — 更大段落间距
    * `h2 { margin: 36px 0 16px; }` 代替 32px — 更大标题上方间距

  **Must NOT do**:
  - 不修改 DOM 结构
  - 不修改内容文字
  - 不添加新的 HTML 元素

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: CSS 属性值的简单添加和替换
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (但依赖 Task 2 的颜色基底)
  - **Parallel Group**: Wave 1 (with Task 1, 2)
  - **Blocks**: Task 5
  - **Blocked By**: Task 2 (配色基底需先更新)

  **References**:
  - `tests/fixtures/sample_report.html:127-148` — 当前表格 CSS，需要添加条纹和圆角
  - `tests/fixtures/sample_report.html:89-115` — 决策卡 CSS，需要更新颜色
  - `tests/fixtures/sample_report.html:153-159` — highlight-box CSS，需要更新为青蓝色

  **Acceptance Criteria**:

  **QA Scenarios:**

  ```
  Scenario: 精致表格样式验证
    Tool: Bash (python + grep)
    Steps:
      1. python -c "
         html = open('tests/fixtures/sample_report.html').read()
         checks = [
             ('border-radius' in html, 'rounded table corners'),
             ('nth-child' in html, 'stripe rows'),
             ('#E8ECF2' in html, 'deep gray-blue table header'),
             ('#D5DBE3' in html, 'light gray-blue borders'),
             ('#2D6A9F' in html, 'accent cyan-blue'),
             ('#E0F2F1' in html, 'BUY mint background'),
             ('#00897B' in html, 'BUY teal border'),
         ]
         for ok, desc in checks: print(f'  {\"✅\" if ok else \"❌\"} {desc}')
         assert all(ok for ok, _ in checks), 'FAILED'
         print('All style additions verified!')
         "
    Expected Result: 所有新样式属性和颜色值存在
    Evidence: .sisyphus/evidence/task-3-style-additions-check.txt
  ```

  **Commit**: YES (groups with Task 2)
  - Message: `style(fixture): update sample_report.html CSS to match Economist palette`
  - Files: `tests/fixtures/sample_report.html`

- [x] 4. 验证 prompt 结构约束完整性

  **What to do**:
  - 运行完整的 prompt 结构约束验证脚本
  - 确认所有结构性约束（container/section/h2、375px、无JS、内联CSS）在修改后的 prompt 中完整保留
  - 确认新风格描述（冷灰背景、深蓝文字、衬线标题、青蓝强调）正确嵌入
  - 确认 error_feedback 处理逻辑不受影响

  **Must NOT do**:
  - 不修改任何文件

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 纯验证任务，运行几个 python 命令检查输出
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Task 1 completing)
  - **Parallel Group**: Wave 2 (sequential after Task 1)
  - **Blocks**: F1-F4
  - **Blocked By**: Task 1

  **References**:
  - `tradingagents/graph/report_generator.py:542-718` — 验证目标方法
  - `.sisyphus/plans/html-visual-style.md` — Success Criteria 中的验证脚本

  **Acceptance Criteria**:

  **QA Scenarios:**

  ```
  Scenario: 完整 prompt 约束验证
    Tool: Bash (python REPL)
    Steps:
      1. conda activate tradingagents
      2. 运行计划中 Success Criteria 的完整验证脚本
      3. 所有 15+ checks pass
    Expected Result: 所有结构性约束 + 新风格描述验证通过
    Failure Indicators: 任何 check 失败
    Evidence: .sisyphus/evidence/task-4-full-prompt-verification.txt
  ```

  **Commit**: NO (纯验证任务)

- [x] 5. 验证 fixture DOM 结构和分段兼容性

  **What to do**:
  - 运行 DOM 结构验证脚本确认 `sample_report.html` 结构完整
  - 运行分段兼容性验证脚本确认 `html_to_jpg.py` 能正常处理更新后的 fixture
  - 确认关键 DOM 元素存在：`div.container`, `header`, `.decision-card`, `section` (≥5), `footer`
  - 确认无 `<script>` 标签
  - 确认分段产出 ≥3 个片段，每个片段包含 `<html>` 和 `<style>`

  **Must NOT do**:
  - 不修改任何文件

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 纯验证任务，运行 python 命令检查 DOM 和分段结果
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 4, both are verification)
  - **Parallel Group**: Wave 2 (with Task 4)
  - **Blocks**: F1-F4
  - **Blocked By**: Task 2, 3

  **References**:
  - `tests/fixtures/sample_report.html` — 验证目标文件
  - `tradingagents/utils/html_to_jpg.py:25-252` — 分段逻辑，确认兼容性
  - `.sisyphus/plans/html-visual-style.md` — Success Criteria 中的 DOM 和分段验证脚本

  **Acceptance Criteria**:

  **QA Scenarios:**

  ```
  Scenario: DOM 结构完整性验证
    Tool: Bash (python + BeautifulSoup)
    Steps:
      1. 运行 Success Criteria 中的 DOM 验证脚本
      2. 确认 container, header, footer, decision-card, sections (≥5) 存在
      3. 确认无 script 标签
    Expected Result: 所有 DOM 元素存在，无 script 标签
    Evidence: .sisyphus/evidence/task-5-dom-verification.txt

  Scenario: 分段兼容性验证
    Tool: Bash (python)
    Steps:
      1. conda activate tradingagents
      2. 运行 Success Criteria 中的分段验证脚本
      3. 确认 segment_html_by_sections 返回 ≥3 片段
      4. 每个片段包含 <html> 和 <style>
    Expected Result: ≥3 片段，每个结构完整
    Evidence: .sisyphus/evidence/task-5-segmentation-verification.txt
  ```

  **Commit**: NO (纯验证任务)

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE.

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists. For each "Must NOT Have": search codebase for forbidden patterns. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  Run `tsc --noEmit` + linter (ruff check) on modified file. Review all changed files for: `as any`/type issues, empty catches, console.log in prod, commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction, generic names.
  Output: `Lint [PASS/FAIL] | Files [N clean/N issues] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high`
  Start from clean state. Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Test cross-task integration: prompt produces fixture-matching style, segmentation works. Save to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff. Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **Commit 1**: `style(report): restyle LLM prompt to Economist magazine style` — `tradingagents/graph/report_generator.py`
- **Commit 2**: `style(fixture): update sample_report.html CSS to match Economist palette` — `tests/fixtures/sample_report.html`

---

## Success Criteria

### Verification Commands
```bash
# Prompt 结构约束验证
python -c "
from tradingagents.graph.report_generator import ReportGenerator
rg = ReportGenerator.__new__(ReportGenerator)
prompt = rg._build_html_prompt('# TEST 交易分析报告\nTest')
checks = [
    ('375px' in prompt, '375px layout'),
    ('<div class=\"container\">' in prompt, 'container div'),
    ('<section>' in prompt, 'section tag'),
    ('<h2>' in prompt, 'h2 tag'),
    ('严禁使用任何 JavaScript' in prompt, 'no-JS rule'),
    ('<style>' in prompt, 'inline CSS'),
    ('utf-8' in prompt, 'UTF-8'),
    ('343px' in prompt, '343px content area'),
]
for ok, desc in checks: print(f'  {\"✅\" if ok else \"❌\"} {desc}')
assert all(ok for ok, _ in checks), 'FAILED'
print('All structural constraints verified!')
"

# Fixture DOM 结构验证
python -c "
from bs4 import BeautifulSoup
html = open('tests/fixtures/sample_report.html').read()
soup = BeautifulSoup(html, 'html.parser')
container = soup.find('div', class_='container')
assert container, 'Missing div.container'
sections = container.find_all('section', recursive=False)
assert len(sections) >= 5, f'Expected 5+ sections, got {len(sections)}'
assert container.find('header'), 'Missing header'
assert container.find('footer'), 'Missing footer'
assert container.find('div', class_='decision-card'), 'Missing decision-card'
assert not soup.find('script'), 'Found script tag!'
print('✅ DOM structure validated')
"

# 分段兼容性验证
python -c "
from tradingagents.utils.html_to_jpg import segment_html_by_sections
html = open('tests/fixtures/sample_report.html').read()
segments = segment_html_by_sections(html)
assert len(segments) >= 3, f'Expected 3+ segments, got {len(segments)}'
for i, seg in enumerate(segments):
    assert '<html' in seg, f'Segment {i} missing html'
    assert '<style>' in seg, f'Segment {i} missing style'
print(f'✅ Segmentation: {len(segments)} segments OK')
"
```

### Final Checklist
- [x] All "Must Have" present (冷色调配色、衬线标题、精致表格、冷化语义决策卡、编辑排版感、WCAG 对比度)
- [x] All "Must NOT Have" absent (不改后备模板、不改 html_to_jpg、不改合规模块、不改结构约束、无外部框架、无模糊描述、不改技术约束、不改 error_feedback)
- [x] Prompt structure assertions pass
- [x] Fixture DOM assertions pass
- [x] Segmentation compatibility assertions pass