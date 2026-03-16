# HTML 报告生成器功能计划（使用 LLM Agent）

## TL;DR

> **Quick Summary**: 为 TradingAgents 添加基于 LLM Agent 的 HTML 报告生成功能，自动集成到调用方（test_glm.py 和 CLI），使用 Markdown 作为输入，生成 Bloomberg 风格深色主题的视觉化 HTML 报告。
>
> **Deliverables**:
> - `ReportGenerator.generate_html_report_with_llm()` 方法（带验证和重试）
> - `_validate_html()` 方法（使用 html5lib）
> - `_build_html_prompt()` 方法（纯文字描述）
> - 修改 `test_glm.py` 自动生成 HTML
> - 修改 `cli/main.py` 自动生成 HTML
>
> **Estimated Effort**: Medium (4-6 hours)
> **Parallel Execution**: NO - sequential
> **Critical Path**: 安装依赖 → 实现验证 → 实现 LLM 生成 → 集成到调用方 → 测试

---

## Context

### Original Request
用户希望基于现有生成的 `report.md`，使用 **LLM Agent** 生成一个完全面向投资小白的视觉化 .html 格式报告，并**自动集成到主流程**。

### Interview Summary

**关键设计决策**：

**技术方案**：
- ✅ **使用 LLM Agent 生成**（不是 Python 解析）
- ✅ **集成在调用方**（test_glm.py 和 CLI，不修改 propagate()）
- ✅ **使用 Markdown 作为输入**（先调用 generate_markdown_report）
- ✅ **纯文字描述提示**（不给 LLM 模板）
- ✅ **验证后使用**（html5lib 验证 + retry）

**视觉设计**：
- **主题**: Bloomberg 风格深色主题（黑色背景 #000000）
- **布局**: 单页长卷，执行摘要优先
- **长度**: 两页内（2000-3000px）
- **响应式**: 仅桌面端（固定宽度 1200px）
- **元素**: 决策卡片（BUY 绿、SELL 红、HOLD 蓝）

**质量保证**：
- **验证**: 使用 html5lib 的 strict=True 模式
- **重试**: 复用项目的 `retry_with_backoff` 机制
- **错误反馈**: 将验证错误反馈给 LLM 重新生成

### Research Findings

**Librarian Agent 研究（HTML 验证）**:

**推荐方案**: html5lib（轻量级、纯 Python）

```python
import html5lib

def validate_html(html_string: str) -> tuple[bool, list[str]]:
    """验证 HTML 语法"""
    try:
        parser = html5lib.HTMLParser(strict=True)
        parser.parse(html_string)
        return True, []
    except Exception as e:
        return False, [str(e)]
```

**优点**:
- ✅ 纯 Python，无外部 C 依赖
- ✅ strict=True 模式会抛出详细异常
- ✅ 符合 HTML5 标准

**Explore Agent 研究（项目 Retry 逻辑）**:

**核心函数**: `retry_with_backoff`（位于 `tradingagents/dataflows/yfinance_news_safe.py`）

```python
def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 2.0,
    backoff_factor: float = 2.0,
    *args,
    **kwargs
) -> Optional[Any]:
    """带有指数退避的重试机制"""
    # 实现：检测 429/rate limit 错误，指数退避
```

**配置**: `max_llm_retries: 3`（在 DEFAULT_CONFIG 中）

---

## Work Objectives

### Core Objective
添加基于 LLM Agent 的 HTML 报告生成功能，自动集成到调用方，支持验证和重试。

### Concrete Deliverables

1. **Python 代码**:
   - `ReportGenerator.generate_html_report_with_llm(state, decision)` - 主方法
   - `ReportGenerator._validate_html(html)` - HTML 验证
   - `ReportGenerator._build_html_prompt(markdown)` - Prompt 构建
   - `ReportGenerator._call_llm_for_html(prompt)` - LLM 调用

2. **调用方修改**:
   - `test_glm.py` - 自动生成 HTML
   - `cli/main.py` - 自动生成 HTML

3. **依赖更新**:
   - `requirements.txt`: 添加 `html5lib>=1.1`

### Definition of Done

- [ ] 运行 `python test_glm.py` 自动生成 HTML 报告
- [ ] HTML 文件包含所有报告内容（决策、章节、免责声明）
- [ ] 深色主题正确应用（黑色背景、高对比度文字）
- [ ] 决策卡片颜色正确（BUY 绿、SELL 红、HOLD 蓝）
- [ ] HTML 通过语法验证（无错误）
- [ ] 支持自动重试（验证失败时重新生成）
- [ ] 文件可在浏览器直接打开

### Must Have
- ✅ 使用 LLM Agent 生成 HTML（不是 Python 解析）
- ✅ 输入为 Markdown 文本（先调用 generate_markdown_report）
- ✅ Bloomberg 风格深色主题
- ✅ HTML 语法验证（html5lib strict=True）
- ✅ 自动重试机制（复用 retry_with_backoff）
- ✅ 错误反馈给 LLM
- ✅ 自动集成到调用方

### Must NOT Have (Guardrails)
- ❌ 不使用 Python markdown 库解析（LLM 自己处理）
- ❌ 不提供 HTML 模板给 LLM（纯文字描述）
- ❌ 不修改 `propagate()` 方法
- ❌ 不使用 JavaScript
- ❌ 不需要响应式设计

---

## Verification Strategy (MANDATORY)

> **UNIVERSAL RULE: ZERO HUMAN INTERVENTION**
>
> ALL tasks in this plan MUST be verifiable WITHOUT any human action.

### Test Decision
- **Infrastructure exists**: NO
- **Automated tests**: NO
- **Framework**: None

### Agent-Executed QA Scenarios (MANDATORY — ALL tasks)

**Task 4: HTML 验证功能**

\`\`\`
Scenario: 验证 HTML 语法检查
  Tool: Bash (Python)
  Preconditions: html5lib 已安装
  Steps:
    1. python -c "
    from tradingagents.graph.report_generator import ReportGenerator
    gen = ReportGenerator({})
    
    # 测试有效 HTML
    valid_html = '<!doctype html><html><body><h1>Test</h1></body></html>'
    is_valid, errors = gen._validate_html(valid_html)
    print(f'Valid HTML: {is_valid}, Errors: {errors}')
    
    # 测试无效 HTML
    invalid_html = '<div><p>未闭合'
    is_valid, errors = gen._validate_html(invalid_html)
    print(f'Invalid HTML: {is_valid}, Errors: {errors}')
    "
  Expected Result:
    - Valid HTML: True, Errors: []
    - Invalid HTML: False, Errors: [包含错误信息]
  Evidence: Python 输出
\`\`\`

**Task 6: LLM 生成 HTML**

\`\`\`
Scenario: 使用 LLM 生成 HTML 报告
  Tool: Bash (Python)
  Preconditions: 有现有的 state 和 decision
  Steps:
    1. python -c "
    from tradingagents.graph.report_generator import ReportGenerator
    from tradingagents.default_config import DEFAULT_CONFIG
    import os
    os.environ['ZHIPU_API_KEY'] = 'test-key'  # 或真实 key
    
    config = DEFAULT_CONFIG.copy()
    gen = ReportGenerator(config)
    
    # 模拟 state（简化）
    state = {
        'company_of_interest': 'TEST',
        'trade_date': '2026-03-16',
        'market_report': '测试市场分析内容',
        'fundamentals_report': '测试基本面内容',
    }
    decision = 'BUY'
    
    # 生成 HTML
    html = gen.generate_html_report_with_llm(state, decision, translate=False)
    
    print(f'HTML 长度: {len(html)}')
    print(f'包含 DOCTYPE: {\"<!DOCTYPE html>\" in html or \"<!doctype html>\" in html}')
    print(f'包含黑色背景: {\"#000000\" in html or \"background-color: #000\" in html}')
    print(f'包含决策: {\"BUY\" in html or \"买入\" in html}')
    "
  Expected Result:
    - HTML 长度 > 5000
    - 包含 DOCTYPE 声明
    - 包含黑色背景 CSS
    - 包含决策信息
  Evidence: Python 输出
\`\`\`

**Task 7: 验证和重试机制**

\`\`\`
Scenario: 验证失败时自动重试
  Tool: Bash (Python)
  Preconditions: LLM 可用
  Steps:
    1. python -c "
    from tradingagents.graph.report_generator import ReportGenerator
    from tradingagents.default_config import DEFAULT_CONFIG
    
    config = DEFAULT_CONFIG.copy()
    config['max_llm_retries'] = 2  # 减少重试次数用于测试
    gen = ReportGenerator(config)
    
    state = {
        'company_of_interest': 'TEST',
        'trade_date': '2026-03-16',
        'market_report': '测试内容',
    }
    decision = 'HOLD'
    
    # 生成 HTML（应该自动验证和重试）
    html = gen.generate_html_report_with_llm(state, decision, translate=False)
    
    # 验证结果
    is_valid, errors = gen._validate_html(html)
    print(f'最终验证结果: {is_valid}')
    print(f'错误数量: {len(errors)}')
    "
  Expected Result:
    - 最终验证结果: True
    - 错误数量: 0
  Evidence: Python 输出
\`\`\`

**Task 8: test_glm.py 集成**

\`\`\`
Scenario: test_glm.py 自动生成 HTML
  Tool: Bash
  Preconditions: 已修改 test_glm.py
  Steps:
    1. grep "generate_html_report_with_llm" test_glm.py
    2. grep "save_html_report" test_glm.py
    3. Assert 输出包含这两个方法调用
  Expected Result: test_glm.py 包含 HTML 生成调用
  Evidence: grep 输出
\`\`\`

**Task 9: 浏览器验证**

\`\`\`
Scenario: HTML 在浏览器中正确渲染
  Tool: Playwright (playwright skill)
  Preconditions: HTML 文件已生成
  Steps:
    1. 运行 python test_glm.py（使用真实或 mock 数据）
    2. 等待 HTML 文件生成
    3. 启动 Chromium 浏览器
    4. 导航到 file:///path/to/reports/TEST_2026-03-16_中文报告.html
    5. 等待页面加载（timeout: 5s）
    6. Assert h1 标题存在
    7. Assert body 背景色为黑色 (rgb(0, 0, 0))
    8. Assert 包含决策卡片
    9. Assert 包含免责声明
    10. 截图保存到 .sisyphus/evidence/html-report-llm.png
  Expected Result: HTML 正确渲染，深色主题应用
  Evidence: .sisyphus/evidence/html-report-llm.png
\`\`\`

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately):
├── Task 1: 添加 html5lib 依赖
└── Task 2: 研究 prompt 设计（准备 prompt 文本）

Wave 2 (After Wave 1):
└── Task 3: 实现 _validate_html() 方法

Wave 3 (After Wave 2):
├── Task 4: 实现 _build_html_prompt() 方法
└── Task 5: 实现 _call_llm_for_html() 方法

Wave 4 (After Wave 3):
├── Task 6: 实现 generate_html_report_with_llm() 主方法
└── Task 7: 实现 save_html_report() 方法

Wave 5 (After Wave 4):
├── Task 8: 修改 test_glm.py
└── Task 9: 修改 cli/main.py

Wave 6 (After Wave 5):
└── Task 10: 端到端测试

Critical Path: Task 1 → Task 3 → Task 6 → Task 8 → Task 10
Parallel Speedup: ~20% faster than sequential
```

### Dependency Matrix

| Task | Depends On | Blocks | Can Parallelize With |
|------|------------|--------|---------------------|
| 1 | None | 3 | 2 |
| 2 | None | 4 | 1 |
| 3 | 1 | 4, 5 | None |
| 4 | 2, 3 | 6 | 5 |
| 5 | 3 | 6 | 4 |
| 6 | 4, 5 | 7, 8, 9 | None |
| 7 | 6 | 8, 9 | None |
| 8 | 6, 7 | 10 | 9 |
| 9 | 6, 7 | 10 | 8 |
| 10 | 8, 9 | None | None |

---

## TODOs

- [ ] 1. 添加 html5lib 依赖

  **What to do**:
  - 在 `requirements.txt` 中添加 `html5lib>=1.1`
  - 不添加其他依赖

  **Must NOT do**:
  - 不添加 lxml（需要 C 依赖）
  - 不添加其他验证库

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 简单的文本文件编辑
  - **Skills**: [`git-master`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 2)
  - **Blocks**: Task 3
  - **Blocked By**: None

  **References**:
  - `requirements.txt` - 现有依赖格式

  **Acceptance Criteria**:
  \`\`\`
  Scenario: 验证 html5lib 依赖已添加
    Tool: Bash
    Steps: grep "html5lib" requirements.txt
    Expected: 输出包含 "html5lib>=1.1"
  \`\`\`

  **Commit**: YES
  - Message: `feat(deps): add html5lib for HTML validation`
  - Files: `requirements.txt`

---

- [ ] 2. 研究 prompt 设计（准备 prompt 文本）

  **What to do**:
  - 设计纯文字描述的 HTML 生成 prompt
  - 包含所有设计要求（深色主题、布局、颜色等）
  - 准备错误反馈 prompt 模板

  **Prompt 模板**：
  \`\`\`
  你是一个专业的金融报告设计师。请根据以下 Markdown 分析报告，生成一个面向投资小白的视觉化 HTML 报告。

  **设计要求**：

  1. **主题风格**：Bloomberg 终端深色主题
     - 背景色：#000000（纯黑色）
     - 文字颜色：#E9ECF1（高对比度白色）
     - 次要文字：#A9B3C1（灰色）

  2. **布局结构**：
     - 单页长卷，固定宽度 1200px
     - 执行摘要优先（决策卡片在最前面）
     - 内容精简在两页内（约 2000-3000px 高度）

  3. **决策卡片样式**：
     - BUY 决策：绿色边框（#4AF6C3），绿色文字
     - SELL 决策：红色边框（#FF433D），红色文字
     - HOLD 决策：蓝色边框（#0068FF），蓝色文字
     - 卡片样式：padding: 24px, border-left: 4px solid

  4. **技术约束**：
     - 单文件 HTML（所有 CSS 必须内联在 <style> 标签中）
     - 不使用 JavaScript（纯静态 HTML）
     - 不使用外部 CSS/JS 文件
     - 使用 UTF-8 编码

  5. **内容组织**：
     - 顶部：股票代码、日期
     - 执行摘要：决策卡片、关键结论
     - 详细分析：市场分析、基本面分析、技术分析、风险评估等
     - 底部：免责声明

  **Markdown 报告**：
  {markdown_content}

  **输出要求**：
  - 只输出 HTML 代码，不要任何解释
  - 确保 HTML 语法正确（标签闭合、嵌套正确）
  - 确保 CSS 语法正确
  \`\`\`

  **错误反馈 Prompt**：
  \`\`\`
  上一次生成的 HTML 验证失败，请修复以下错误：

  {validation_errors}

  请重新生成完整的 HTML 代码，修复上述错误。
  \`\`\`

  **Must NOT do**:
  - 不提供 HTML 模板或示例
  - 不使用 few-shot 示例

  **Recommended Agent Profile**:
  - **Category**: `writing`
    - Reason: 需要设计清晰、准确的 prompt 文本
  - **Skills**: 无特定技能

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 1)
  - **Blocks**: Task 4
  - **Blocked By**: None

  **References**:
  - 无（新 prompt 设计）

  **Acceptance Criteria**:
  - Prompt 文本清晰、准确
  - 包含所有设计要求
  - 包含错误反馈模板

  **Commit**: YES (groups with 1)
  - Message: `feat(prompt): design HTML generation prompt template`
  - Files: `tradingagents/graph/report_generator.py`

---

- [ ] 3. 实现 _validate_html() 方法

  **What to do**:
  - 在 `ReportGenerator` 类中添加 `_validate_html(self, html: str) -> tuple[bool, list[str]]` 方法
  - 使用 html5lib 的 strict=True 模式验证 HTML
  - 返回 (is_valid, error_messages)

  **方法签名**：
  \`\`\`python
  def _validate_html(self, html: str) -> tuple[bool, list[str]]:
      """验证 HTML 语法

      Args:
          html: HTML 内容

      Returns:
          (is_valid, error_messages)
      """
  \`\`\`

  **实现参考**：
  \`\`\`python
  import html5lib

  def _validate_html(self, html: str) -> tuple[bool, list[str]]:
      try:
          parser = html5lib.HTMLParser(strict=True)
          parser.parse(html)
          return True, []
      except Exception as e:
          return False, [str(e)]
  \`\`\`

  **Must NOT do**:
  - 不使用 lxml（避免 C 依赖）
  - 不自动修复 HTML（只验证）

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 简单的验证逻辑实现
  - **Skills**: [`git-master`]

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 4, 5
  - **Blocked By**: Task 1

  **References**:
  - `tradingagents/graph/report_generator.py:47-114` - 现有方法模式

  **Acceptance Criteria**:
  \`\`\`
  Scenario: 测试 HTML 验证
    Tool: Bash (Python)
    Steps:
      python -c "
      from tradingagents.graph.report_generator import ReportGenerator
      gen = ReportGenerator({})
      
      valid_html = '<!doctype html><html><body><h1>Test</h1></body></html>'
      is_valid, errors = gen._validate_html(valid_html)
      assert is_valid == True
      assert len(errors) == 0
      
      invalid_html = '<div><p>未闭合'
      is_valid, errors = gen._validate_html(invalid_html)
      assert is_valid == False
      assert len(errors) > 0
      "
    Expected: 所有断言通过
  \`\`\`

  **Commit**: YES
  - Message: `feat(report): add HTML validation method`
  - Files: `tradingagents/graph/report_generator.py`

---

- [ ] 4. 实现 _build_html_prompt() 方法

  **What to do**:
  - 添加 `_build_html_prompt(self, markdown: str) -> str` 方法
  - 构建 HTML 生成 prompt（包含所有设计要求）
  - 可选：添加错误反馈参数

  **方法签名**：
  \`\`\`python
  def _build_html_prompt(
      self,
      markdown: str,
      error_feedback: Optional[list[str]] = None
  ) -> str:
      """构建 HTML 生成 prompt

      Args:
          markdown: Markdown 报告内容
          error_feedback: 可选的错误反馈列表

      Returns:
          完整的 prompt 文本
      """
  \`\`\`

  **Must NOT do**:
  - 不包含 HTML 模板或示例
  - 不使用 few-shot learning

  **Recommended Agent Profile**:
  - **Category**: `writing`
    - Reason: 需要清晰的 prompt 文本组织
  - **Skills**: 无特定技能

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Task 5)
  - **Blocks**: Task 6
  - **Blocked By**: Task 2, 3

  **References**:
  - Task 2 的 prompt 模板

  **Acceptance Criteria**:
  - Prompt 包含所有设计要求
  - Prompt 清晰、准确

  **Commit**: YES (groups with 5)
  - Message: `feat(report): add HTML prompt builder`
  - Files: `tradingagents/graph/report_generator.py`

---

- [ ] 5. 实现 _call_llm_for_html() 方法

  **What to do**:
  - 添加 `_call_llm_for_html(self, prompt: str) -> str` 方法
  - 调用 LLM 生成 HTML
  - 复用现有的 translator (self.translator)

  **方法签名**：
  \`\`\`python
  def _call_llm_for_html(self, prompt: str) -> str:
      """调用 LLM 生成 HTML

      Args:
          prompt: HTML 生成 prompt

      Returns:
          LLM 生成的 HTML 代码
      """
  \`\`\`

  **实现参考**：
  \`\`\`python
  def _call_llm_for_html(self, prompt: str) -> str:
      if not self.translator:
          raise RuntimeError("Translation not initialized")
      
      llm = self.translator.get_llm()
      from langchain_core.messages import HumanMessage, SystemMessage
      
      messages = [
          SystemMessage(content="你是一个专业的金融报告设计师，擅长生成高质量的 HTML 报告。"),
          HumanMessage(content=prompt)
      ]
      
      result = llm.invoke(messages)
      return result.content
  \`\`\`

  **Must NOT do**:
  - 不创建新的 LLM 客户端（复用 translator）

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 简单的 LLM 调用逻辑
  - **Skills**: [`git-master`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Task 4)
  - **Blocks**: Task 6
  - **Blocked By**: Task 3

  **References**:
  - `tradingagents/graph/report_generator.py:79-96` - translate_to_chinese() 方法模式

  **Acceptance Criteria**:
  - 方法正确调用 LLM
  - 返回 HTML 字符串

  **Commit**: YES (groups with 4)
  - Message: `feat(report): add LLM HTML generation caller`
  - Files: `tradingagents/graph/report_generator.py`

---

- [ ] 6. 实现 generate_html_report_with_llm() 主方法

  **What to do**:
  - 添加 `generate_html_report_with_llm(state, decision, translate, max_retries)` 方法
  - 集成所有子方法：
    1. 生成 Markdown（调用现有方法）
    2. 构建 prompt
    3. 调用 LLM（带验证和重试）
    4. 验证结果
    5. 如果验证失败，反馈错误并重试
  - 复用项目的 `retry_with_backoff` 机制

  **方法签名**：
  \`\`\`python
  def generate_html_report_with_llm(
      self,
      state: Dict[str, Any],
      decision: str,
      translate: bool = True,
      max_retries: int = 3
  ) -> str:
      """使用 LLM Agent 生成 HTML 报告（带验证和重试）

      Args:
          state: Agent 状态字典
          decision: 最终交易决策
          translate: 是否翻译为中文
          max_retries: 最大重试次数

      Returns:
          HTML 报告内容
      """
  \`\`\`

  **实现逻辑**：
  \`\`\`python
  def generate_html_report_with_llm(self, state, decision, translate=True, max_retries=3):
      # 1. 先生成 Markdown
      markdown_text = self.generate_markdown_report(state, decision, translate=translate)
      
      # 2. 尝试生成 HTML（带重试）
      for attempt in range(max_retries):
          # 构建 prompt
          prompt = self._build_html_prompt(markdown_text)
          
          # 调用 LLM
          html = self._call_llm_for_html(prompt)
          
          # 验证
          is_valid, errors = self._validate_html(html)
          
          if is_valid:
              print(f"✅ HTML 生成成功（第 {attempt + 1} 次尝试）")
              return html
          else:
              print(f"⚠️ HTML 验证失败（第 {attempt + 1} 次尝试）: {errors}")
              # 添加错误反馈并重试
              markdown_text = self._build_html_prompt(markdown_text, error_feedback=errors)
      
      # 所有重试都失败
      print(f"❌ HTML 生成失败，已尝试 {max_retries} 次")
      return html  # 返回最后一次结果
  \`\`\`

  **Must NOT do**:
  - 不跳过验证步骤
  - 不在验证失败时直接返回

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
    - Reason: 标准的 Python 方法实现
  - **Skills**: [`git-master`]

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 7, 8, 9
  - **Blocked By**: Task 4, 5

  **References**:
  - `tradingagents/graph/report_generator.py:126-275` - generate_markdown_report() 方法
  - `tradingagents/dataflows/yfinance_news_safe.py` - retry_with_backoff 函数

  **Acceptance Criteria**:
  \`\`\`
  Scenario: 端到端生成 HTML
    Tool: Bash (Python)
    Steps: 见 "Verification Strategy" 部分
  \`\`\`

  **Commit**: YES (groups with 7)
  - Message: `feat(report): add LLM-based HTML report generation`
  - Files: `tradingagents/graph/report_generator.py`

---

- [ ] 7. 实现 save_html_report() 方法

  **What to do**:
  - 添加 `save_html_report(html_content: str, filepath: str)` 方法
  - 保存 HTML 文件（UTF-8 编码）
  - 打印成功消息

  **实现参考**：
  \`\`\`python
  def save_html_report(self, html_content: str, filepath: str) -> None:
      """保存 HTML 报告到文件

      Args:
          html_content: HTML 报告内容
          filepath: 保存路径
      """
      report_path = Path(filepath)
      report_path.parent.mkdir(parents=True, exist_ok=True)
      
      with open(report_path, 'w', encoding='utf-8') as f:
          f.write(html_content)
      
      print(f"✅ HTML 报告已保存: {report_path}")
  \`\`\`

  **Must NOT do**:
  - 不修改 `save_report()` 方法

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 简单的文件保存操作
  - **Skills**: [`git-master`]

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 8, 9
  - **Blocked By**: Task 6

  **References**:
  - `tradingagents/graph/report_generator.py:344-359` - save_report() 方法

  **Acceptance Criteria**:
  - 文件成功保存
  - UTF-8 编码正确

  **Commit**: YES (groups with 6)
  - Message: `feat(report): add HTML report saver`
  - Files: `tradingagents/graph/report_generator.py`

---

- [ ] 8. 修改 test_glm.py

  **What to do**:
  - 在报告生成部分（第 84-106 行附近）添加 HTML 生成
  - 在生成 Markdown 之后，自动生成 HTML
  - 保存到相同目录，文件名为 `{ticker}_{date}_中文报告.html`

  **修改位置**：
  \`\`\`python
  # 生成报告
  if generate_markdown:
      print("\n📝 正在生成报告...")
      print("-"*60)

      generator = ReportGenerator(config)
      
      # Markdown（现有）
      markdown_report = generator.generate_markdown_report(
          state,
          decision,
          translate=translate_to_chinese
      )
      report_filename = f"{ticker}_{trade_date}_{'中文' if translate_to_chinese else '英文'}报告.md"
      report_path = f"reports/{report_filename}"
      generator.save_report(markdown_report, report_path)
      print(f"✅ Markdown 报告已保存到: {report_path}")
      
      # 🆕 HTML（新增）
      print("\n🌐 正在生成 HTML 报告...")
      html_report = generator.generate_html_report_with_llm(
          state,
          decision,
          translate=translate_to_chinese
      )
      html_filename = f"{ticker}_{trade_date}_{'中文' if translate_to_chinese else '英文'}报告.html"
      html_path = f"reports/{html_filename}"
      generator.save_html_report(html_report, html_path)
      print(f"✅ HTML 报告已保存到: {html_path}")
  \`\`\`

  **Must NOT do**:
  - 不修改现有的 Markdown 生成逻辑
  - 不破坏现有的输出格式

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 简单的代码添加
  - **Skills**: [`git-master`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 5 (with Task 9)
  - **Blocks**: Task 10
  - **Blocked By**: Task 6, 7

  **References**:
  - `test_glm.py:84-106` - 报告生成部分

  **Acceptance Criteria**:
  \`\`\`
  Scenario: 验证 test_glm.py 包含 HTML 生成
    Tool: Bash
    Steps:
      grep "generate_html_report_with_llm" test_glm.py
      grep "save_html_report" test_glm.py
    Expected: 两个方法都被调用
  \`\`\`

  **Commit**: YES (groups with 9)
  - Message: `feat(test): auto-generate HTML report in test_glm.py`
  - Files: `test_glm.py`

---

- [ ] 9. 修改 cli/main.py

  **What to do**:
  - 找到 CLI 中的报告生成部分
  - 添加 HTML 生成逻辑（类似 test_glm.py）
  - 确保与现有的 Markdown 生成并列执行

  **Must NOT do**:
  - 不破坏现有的 CLI 功能
  - 不改变现有的参数结构

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 简单的代码添加
  - **Skills**: [`git-master`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 5 (with Task 8)
  - **Blocks**: Task 10
  - **Blocked By**: Task 6, 7

  **References**:
  - `cli/main.py` - CLI 实现
  - `test_glm.py:84-106` - 参考实现

  **Acceptance Criteria**:
  - CLI 自动生成 HTML
  - 与 Markdown 并列生成

  **Commit**: YES (groups with 8)
  - Message: `feat(cli): auto-generate HTML report`
  - Files: `cli/main.py`

---

- [ ] 10. 端到端测试

  **What to do**:
  - 运行 `python test_glm.py`（使用真实 API key 或 mock）
  - 验证 HTML 文件生成
  - 在浏览器中打开 HTML 验证渲染
  - 使用 Playwright 自动化测试

  **Must NOT do**:
  - 不跳过浏览器验证

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
    - Reason: 标准的端到端测试
  - **Skills**: [`playwright`]

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: None (final task)
  - **Blocked By**: Task 8, 9

  **Acceptance Criteria**:
  \`\`\`
  Scenario: 完整流程测试
    Tool: Playwright
    Steps: 见 "Verification Strategy" 部分
  \`\`\`

  **Commit**: NO (testing only)

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 1, 2 | `feat(deps, prompt): setup html5lib and HTML generation prompt` | requirements.txt, report_generator.py | `grep html5lib requirements.txt` |
| 3 | `feat(report): add HTML validation method` | report_generator.py | `python -c "from ...; gen = ReportGenerator(); gen._validate_html('<h1>test</h1>')"` |
| 4, 5 | `feat(report): add HTML prompt builder and LLM caller` | report_generator.py | `python -c "assert hasattr(ReportGenerator, '_build_html_prompt')"` |
| 6, 7 | `feat(report): add LLM-based HTML generation` | report_generator.py | `python -c "assert hasattr(ReportGenerator, 'generate_html_report_with_llm')"` |
| 8, 9 | `feat(cli, test): auto-generate HTML in CLI and test script` | test_glm.py, cli/main.py | `grep generate_html_report test_glm.py cli/main.py` |
| 10 | No commit | - | - |

---

## Success Criteria

### Verification Commands
```bash
# 1. 验证依赖
grep "html5lib" requirements.txt

# 2. 验证方法存在
python -c "
from tradingagents.graph.report_generator import ReportGenerator
import inspect
methods = [m for m in dir(ReportGenerator) if not m.startswith('_')]
print('Methods:', methods)
assert 'generate_html_report_with_llm' in methods
assert '_validate_html' in methods
"

# 3. 生成 HTML（需要有 API key）
python test_glm.py  # 或使用 mock

# 4. 验证文件
test -f reports/sh600941_2026-03-16_中文报告.html

# 5. 验证 HTML 内容
grep "<!DOCTYPE html>" reports/sh600941_2026-03-16_中文报告.html
grep "#000000" reports/sh600941_2026-03-16_中文报告.html
```

### Final Checklist
- [ ] html5lib 依赖已添加
- [ ] `_validate_html()` 方法已实现
- [ ] `_build_html_prompt()` 方法已实现
- [ ] `_call_llm_for_html()` 方法已实现
- [ ] `generate_html_report_with_llm()` 方法已实现
- [ ] `save_html_report()` 方法已实现
- [ ] test_glm.py 自动生成 HTML
- [ ] cli/main.py 自动生成 HTML
- [ ] HTML 通过语法验证
- [ ] HTML 在浏览器中正确渲染
- [ ] 深色主题正确应用
- [ ] 端到端测试通过
