# TradingAgents 软件架构详解

> 本文面向初学者，完整讲解 TradingAgents 的软件架构。阅读前只需具备基础 Python 知识即可。

---

## 一、项目是什么？

TradingAgents 是一个**多智能体协作系统**，模拟真实交易公司的运作流程。多个 AI 角色（分析师、研究员、交易员、风控）各司其职，通过协作讨论，最终输出一个交易决策：**买入 / 卖出 / 持有**。

它的核心思想是：**让不同立场的 AI 角色互相辩论，避免单一 AI 的偏见，做出更全面的投资决策。**

---

## 二、一张图看全流程

```
用户输入（股票代码 + 日期）
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│                   分析师团队（并行）                        │
│                                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │ 市场分析师 │ │ 情绪分析师│ │ 新闻分析师 │ │ 基本面分析师│  │
│  │(技术指标) │ │(社交媒体) │ │(全球新闻) │ │(财务报表)  │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └─────┬─────┘  │
│       │            │            │             │         │
│       ▼            ▼            ▼             ▼         │
│   市场报告      情绪报告     新闻报告      基本面报告     │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │    投资研究辩论       │
              │                     │
              │  多方研究员 ──┐      │
              │  ┌──────────┐│      │
              │  │牛方研究员 ││      │
              │  └────┬─────┘│      │
              │       │      │      │
              │  ┌────▼─────┐│      │
              │  │熊方研究员 ││      │
              │  └────┬─────┘│      │
              │       │      │      │
              │       ▼      │      │
              │  ┌──────────┐│      │
              │  │研究经理   │◀──────┘
              │  │(裁决+计划)│
              │  └────┬─────┘
              └───────┼───────┘
                      │ 投资计划
                      ▼
              ┌───────────────┐
              │    交易员       │
              │ (制定交易方案)  │
              └───────┬───────┘
                      │ 交易提案
                      ▼
              ┌─────────────────────┐
              │   风控辩论           │
              │                     │
              │  ┌───────────────┐  │
              │  │ 激进分析师     │  │
              │  └──────┬────────┘  │
              │         │           │
              │  ┌──────▼────────┐  │
              │  │ 保守分析师     │  │
              │  └──────┬────────┘  │
              │         │           │
              │  ┌──────▼────────┐  │
              │  │ 中立分析师     │  │
              │  └──────┬────────┘  │
              │         │           │
              │         ▼           │
              │  ┌───────────────┐  │
              │  │ 风控经理(裁决) │  │
              │  └──────┬────────┘  │
              └─────────┼──────────┘
                        │
                        ▼
               最终决策: BUY / SELL / HOLD
                        │
                        ▼
              ┌─────────────────────┐
              │  后处理管线          │
              │  信号提取 → 报告生成  │
              │  → 翻译 → 合规检查   │
              └─────────────────────┘
```

---

## 三、系统分层架构

系统从下到上分为 **4 层**，每层各司其职：

```
┌─────────────────────────────────────────┐
│         CLI / 入口层 (cli/)             │  用户交互界面
├─────────────────────────────────────────┤
│       图编排层 (graph/)                 │  工作流控制、辩论逻辑、报告生成
├─────────────────────────────────────────┤
│       代理层 (agents/)                  │  各角色的 AI 逻辑
├─────────────────────────────────────────┤
│       基础设施层 (dataflows/ + llm_clients/) │  数据获取、LLM 调用、记忆系统
└─────────────────────────────────────────┘
```

---

## 四、逐层详解

### 4.1 基础设施层

这是整个系统的地基，不包含任何业务逻辑。

#### 4.1.1 LLM 客户端 (`llm_clients/`)

**问题**：不同 AI 厂商（OpenAI、Google、Anthropic）的 API 接口不同。

**解决**：用**工厂模式 + 抽象基类**统一接口。

```
                BaseLLMClient (抽象基类)
                 /     |      \
                /      |       \
      OpenAIClient  AnthropicClient  GoogleClient
      (同时兼容)     (Claude)         (Gemini)
       Ollama
       OpenRouter
       xAI
       智谱
```

```python
# 使用方式：一行代码创建任意厂商的客户端
client = create_llm_client(
    provider="openai",      # 或 google, anthropic, xai...
    model="gpt-5.2",
    base_url="https://api.openai.com/v1"
)
llm = client.get_llm()  # 返回统一的 LangChain ChatModel
```

**关键设计**：
- `BaseLLMClient.invoke_with_timeout()` — 所有 LLM 调用都有超时保护，防止卡死
- `UnifiedChatOpenAI` — 自动检测推理模型（如 o1、gpt-5），移除不兼容的 `temperature` 参数
- `create_llm_client()` 工厂函数 — 一个入口创建所有厂商客户端

#### 4.1.2 数据获取层 (`dataflows/`)

**问题**：股票数据、新闻、财务报表来自不同供应商（yfinance、Alpha Vantage、新浪财经、akshare），如何统一调用？

**解决**：**路由器模式** — 一次调用，自动路由到最优供应商，失败时自动切换。

```
代理调用: get_stock_data("AAPL", "2024-01-01", "2024-01-31")
                │
                ▼
        ┌───────────────┐
        │  route_to_vendor │  ← 路由器（总调度）
        └───────┬───────┘
                │
        按优先级尝试：
        ┌───────┴───────┐
        │ 1. sina_finance │ ← 配置的首选供应商
        │    (失败?)      │
        ├────────────────┤
        │ 2. alpha_vantage│ ← 自动切换
        │    (失败?)      │
        ├────────────────┤
        │ 3. yfinance     │ ← 最终兜底
        └────────────────┘
```

**数据工具分 4 类**：

| 类别 | 工具函数 | 说明 |
|------|---------|------|
| 行情数据 | `get_stock_data` | OHLCV 价格数据 |
| 技术指标 | `get_indicators` | MACD、RSI、均线等 |
| 基本面 | `get_fundamentals`, `get_balance_sheet`... | 财务报表 |
| 新闻数据 | `get_news`, `get_global_news`... | 新闻和内幕交易 |

**配置优先级**（从高到低）：
```
工具级配置 > 类别级配置 > 默认值

# 示例：只把 "获取股票数据" 指向 alpha_vantage，其他不变
config["tool_vendors"] = {"get_stock_data": "alpha_vantage"}
```

#### 4.1.3 记忆系统 (`agents/utils/memory.py`)

**问题**：AI 角色如何从过去的错误中学习？

**解决**：基于 **BM25 算法**的本地记忆系统（不需要调 API，不消耗 token）。

```python
# 1. 交易结束后，反思并存储经验
memory.add_situations([
    ("高通胀+加息环境", "考虑防御性板块，减少成长股配置"),
    ("科技股剧烈波动", "降低高风险科技股仓位"),
])

# 2. 下次遇到类似市场环境，自动检索历史经验
matches = memory.get_memories("当前通胀上升，科技股波动加大", n_matches=2)
# → 返回相似度最高的历史经验和教训
```

每个需要学习的角色都有独立记忆：牛方研究员、熊方研究员、交易员、研究经理、风控经理。

#### 4.1.4 配置系统

```python
# 使用方式
config = DEFAULT_CONFIG.copy()  # 必须 .copy()，禁止修改原始配置

# 关键配置项
config["llm_provider"] = "openai"       # LLM 厂商
config["deep_think_llm"] = "gpt-5.2"    # 复杂推理用
config["quick_think_llm"] = "gpt-5-mini"# 快速任务用
config["max_debate_rounds"] = 1          # 辩论轮数
config["llm_invoke_timeout"] = 120       # LLM 超时(秒)
```

---

### 4.2 代理层 (`agents/`)

这是系统的核心业务层，定义了所有 AI 角色的行为。

#### 4.2.1 角色总览

| 角色 | 文件位置 | 职责 | 用哪种 LLM |
|------|---------|------|-----------|
| 市场分析师 | `analysts/market_analyst.py` | 技术指标分析 | quick |
| 情绪分析师 | `analysts/social_media_analyst.py` | 社交媒体情绪分析 | quick |
| 新闻分析师 | `analysts/news_analyst.py` | 全球新闻和内幕交易 | quick |
| 基本面分析师 | `analysts/fundamentals_analyst.py` | 财务报表分析 | quick |
| 牛方研究员 | `researchers/bull_researcher.py` | 为投资做多方论证 | quick |
| 熊方研究员 | `researchers/bear_researcher.py` | 为投资做空方论证 | quick |
| 研究经理 | `managers/research_manager.py` | 裁决辩论，制定投资计划 | deep |
| 交易员 | `trader/trader.py` | 根据计划制定具体交易方案 | quick |
| 激进分析师 | `risk_mgmt/aggressive_debator.py` | 风控辩论（激进派） | quick |
| 保守分析师 | `risk_mgmt/conservative_debator.py` | 风控辩论（保守派） | quick |
| 中立分析师 | `risk_mgmt/neutral_debator.py` | 风控辩论（中立派） | quick |
| 风控经理 | `managers/risk_manager.py` | 裁决风控辩论，最终决策 | deep |

> **deep think** = 复杂推理模型（如 gpt-5.2），用于需要深度判断的角色
> **quick think** = 快速模型（如 gpt-5-mini），用于常规分析

#### 4.2.2 代理工厂模式

所有代理都使用**闭包工厂**创建。这是本项目最核心的设计模式：

```python
def create_bull_researcher(llm, memory):
    """工厂函数：创建牛方研究员节点"""
    
    def bull_node(state) -> dict:
        """内部函数：LangGraph 节点，每次被调用时执行"""
        # 1. 从 state 中读取当前状态
        reports = state["market_report"]  # 分析师报告
        history = state["investment_debate_state"]["history"]  # 辩论历史
        
        # 2. 从记忆中检索类似的历史经验
        past_memories = memory.get_memories(reports, n_matches=2)
        
        # 3. 构建 prompt 并调用 LLM
        prompt = f"你是牛方分析师...基于以下数据论证投资价值：{reports}"
        response = llm.invoke(prompt)
        
        # 4. 更新 state 并返回（只返回变更的字段！）
        return {"investment_debate_state": {
            "history": history + "\n" + argument,
            "bull_history": ...,
            "count": count + 1,
        }}
    
    return bull_node  # 返回节点函数
```

**为什么用闭包？**
- `llm` 和 `memory` 只需注入一次，内部节点函数无需重复传递
- 返回的函数签名 `f(state) -> dict` 完美适配 LangGraph 的节点接口
- 每个代理的逻辑完全隔离，互不干扰

#### 4.2.3 分析师如何使用工具

分析师（如市场分析师）不是直接调数据 API，而是通过 LangGraph 的 **ToolNode** 间接调用：

```
市场分析师节点
    │
    │ 调用 llm.bind_tools(tools).invoke()
    │
    ▼
LLM 返回 tool_calls: [{"name": "get_stock_data", "args": {...}}]
    │
    ▼
ConditionalLogic 检测到 tool_calls
    │
    ▼
路由到 tools_market 节点 (ToolNode)
    │
    ▼
ToolNode 自动执行 get_stock_data()
    │
    ▼
结果返回给市场分析师，继续分析
```

**工具定义**（以 `get_stock_data` 为例）：

```python
@tool  # LangChain 的工具装饰器，自动注册为可调用的工具
def get_stock_data(
    symbol: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """Retrieve stock price data (OHLCV)..."""
    return route_to_vendor("get_stock_data", symbol, start_date, end_date)
```

> `Annotated[str, "描述"]` 中的描述是给 LLM 看的，帮助它理解何时该调用这个工具。

#### 4.2.4 辩论机制

系统有两轮辩论，是整个框架最精华的部分：

**第一轮：投资辩论（牛方 vs 熊方）**

```
牛方研究员 → 熊方研究员 → 牛方研究员 → 熊方研究员 → ... (循环)
                                              │
                                    达到辩论轮数上限？
                                              │ 是
                                              ▼
                                        研究经理裁决
                                        输出：投资计划
```

```python
# 条件逻辑：决定辩论是否继续
def should_continue_debate(state):
    if state["investment_debate_state"]["count"] >= 2 * max_debate_rounds:
        return "Research Manager"  # 辩论结束，交给经理
    if state["investment_debate_state"]["current_response"].startswith("Bull"):
        return "Bear Researcher"   # 牛方说完，轮到熊方
    return "Bull Researcher"       # 熊方说完，轮到牛方
```

**第二轮：风控辩论（三方）**

```
激进分析师 → 保守分析师 → 中立分析师 → 激进分析师 → ... (循环)
                                                    │
                                      达到辩论轮数上限？
                                                    │ 是
                                                    ▼
                                              风控经理裁决
                                              输出：最终决策
```

#### 4.2.5 合规代理 (`agents/compliance/`)

最终报告生成后，合规代理负责将不合规的术语替换为合规表述：

```
"建议买入" → "可加入观察列表"
"稳赚不赔" → "存在投资机会"
"BUY"      → "值得研究"
```

---

### 4.3 图编排层 (`graph/`)

这一层用 **LangGraph** 把所有代理"串"成一个有向图，定义执行流程。

#### 4.3.1 LangGraph 是什么？

LangGraph 是一个**状态机框架**。你定义节点（代理函数）和边（执行顺序），它会自动管理状态的传递。

```
核心概念：
- Node（节点）：一个函数，接收 state，返回 state 的更新
- Edge（边）：节点之间的连线，可以是固定的或条件分支
- State（状态）：所有节点共享的数据字典
```

#### 4.3.2 核心类和职责

| 文件 | 类名 | 职责 |
|------|------|------|
| `trading_graph.py` | `TradingAgentsGraph` | **主入口**：初始化所有组件，暴露 `propagate()` 方法 |
| `setup.py` | `GraphSetup` | 构建 LangGraph 图：添加节点、定义边 |
| `conditional_logic.py` | `ConditionalLogic` | 条件分支逻辑（工具调用、辩论轮转） |
| `propagation.py` | `Propagator` | 创建初始 state，配置图运行参数 |
| `reflection.py` | `Reflector` | 交易后的反思和经验存储 |
| `signal_processing.py` | `SignalProcessor` | 从长篇决策文本中提取 BUY/SELL/HOLD |
| `report_generator.py` | `ReportGenerator` | 生成 Markdown / HTML 报告、翻译、合规检查 |

#### 4.3.3 完整图结构

以下是用 LangGraph 构建的实际图（来自 `setup.py`）：

```
START
  │
  ▼
Market Analyst ←→ tools_market     ┐ (分析师按序执行)
  │                                  │
Msg Clear Market                     │
  │                                  │
  ▼                                  │
Social Analyst ←→ tools_social      │
  │                                  │
Msg Clear Social                     │
  │                                  │
  ▼                                  │
News Analyst ←→ tools_news          │
  │                                  │
Msg Clear News                       │
  │                                  │
  ▼                                  │
Fundamentals Analyst ←→ tools_fund  ┘
  │
  ▼
Bull Researcher ←→ Bear Researcher  (辩论循环)
  │
  ▼ (辩论结束)
Research Manager                    (裁决 + 输出投资计划)
  │
  ▼
Trader                              (制定交易方案)
  │
  ▼
Aggressive Analyst                  ┐
  ↑                                 │ (三方辩论循环)
Conservative Analyst                │
  ↑                                 │
Neutral Analyst ────────────────────┘
  │
  ▼ (辩论结束)
Risk Judge (风控经理)               (最终裁决)
  │
  ▼
END
```

#### 4.3.4 状态定义

所有代理共享一个 `AgentState`，它是一个 **TypedDict**：

```python
class AgentState(MessagesState):   # 继承 LangGraph 的基础状态
    # === 输入参数 ===
    company_of_interest: str   # 股票代码（如 "AAPL"）
    trade_date: str            # 交易日期（如 "2024-05-10"）

    # === 分析师报告（第一阶段产出） ===
    market_report: str         # 市场分析报告
    sentiment_report: str      # 情绪分析报告
    news_report: str           # 新闻分析报告
    fundamentals_report: str   # 基本面分析报告

    # === 投资辩论状态（第二阶段） ===
    investment_debate_state: InvestDebateState  # 嵌套状态
    investment_plan: str       # 研究经理输出的投资计划

    # === 交易员输出 ===
    trader_investment_plan: str

    # === 风控辩论状态（第三阶段） ===
    risk_debate_state: RiskDebateState  # 嵌套状态
    final_trade_decision: str  # 最终交易决策
```

**关键规则**：每个节点只返回它**修改的字段**，不返回整个 state：
```python
# ✅ 正确
return {"market_report": "这是市场分析报告..."}

# ❌ 错误
return {"company_of_interest": "AAPL", "market_report": "...", "trade_date": "..."}  # 不要返回未修改的字段
```

#### 4.3.5 执行流程

```python
# 1. 创建图实例
ta = TradingAgentsGraph(
    selected_analysts=["market", "social", "news", "fundamentals"],
    debug=True,
    config=config
)

# 2. 运行（核心方法）
final_state, decision = ta.propagate("NVDA", "2024-05-10")
#                       股票代码      日期

# propagate 内部做了什么：
#   1. 创建初始 state（股票代码、日期、空报告）
#   2. 调用 graph.invoke(state) 执行整个图
#   3. 从 final_trade_decision 中提取 BUY/SELL/HOLD 信号
#   4. 保存完整状态到 JSON 日志

# 3. 可选：交易后反思（学习经验）
ta.reflect_and_remember(returns_losses=1000)  # 传入实际收益
```

#### 4.3.6 报告生成管线

`ReportGenerator` 负责把原始状态转化为可读的报告：

```
AgentState
    │
    ▼
generate_markdown_report()    ← 生成 Markdown 结构化报告
    │
    ▼
_translate_reports_parallel() ← 并行翻译为中文（5 个线程同时翻译）
    │
    ▼
generate_html_report_with_llm() ← 调用 LLM 生成手机端 HTML 报告
    │   ├── _build_html_prompt()     ← 构建详细的 HTML 设计 prompt
    │   ├── _call_llm_for_html()     ← 调用 LLM 生成
    │   ├── _validate_html()         ← 验证 HTML 语法（html5lib）
    │   └── 失败时自动重试（最多 3 次）
    │
    ▼
compliance_officer.review_html() ← 合规检查（替换不合规术语）
    │
    ▼
保存 reports/{ticker}_original.html
保存 reports/{ticker}_compliant.html
```

---

### 4.4 CLI / 入口层 (`cli/`)

用户通过命令行交互界面使用系统。

```bash
python -m cli.main           # 启动交互式 CLI
```

**CLI 技术栈**：
- **Typer** — 命令行框架（支持子命令、参数验证）
- **Rich** — 终端美化（进度条、面板、颜色、实时输出）
- **Questionary** — 交互式问答（选择股票、日期、模型等）

**CLI 核心功能**：
- 选择股票代码和交易日期
- 配置 LLM 模型
- 实时显示各代理的输出
- 生成和保存报告
- 统计 LLM 和工具的调用次数/耗时

**最简使用方式**（不通过 CLI）：
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())
_, decision = ta.propagate("AAPL", "2024-05-10")
print(decision)  # 输出: BUY / SELL / HOLD
```

---

## 五、数据流全景图

以 `propagate("NVDA", "2024-05-10")` 为例，数据如何流经整个系统：

```
1. Propagator.create_initial_state()
   → state = {company_of_interest: "NVDA", trade_date: "2024-05-10", ...空报告}

2. Market Analyst 节点
   → LLM 决定调用 get_stock_data("NVDA", ...)
   → route_to_vendor() 路由到 sina_finance
   → 获取 OHLCV 数据 → 返回给 LLM
   → LLM 生成技术分析报告
   → state["market_report"] = "基于MACD金叉..."

3. Social / News / Fundamentals 分析师
   → 同理，各自调用不同工具获取数据
   → state 中填入 sentiment_report, news_report, fundamentals_report

4. Bull Researcher 节点
   → 读取所有 4 份报告 + 记忆系统中的历史经验
   → LLM 生成多方论证
   → state["investment_debate_state"].history += "牛方: ..."

5. Bear Researcher 节点
   → 读取历史报告 + 牛方论证
   → LLM 生成反方论证
   → state["investment_debate_state"].history += "熊方: ..."

6. (循环辩论直到轮数上限)

7. Research Manager 节点
   → 综合辩论历史 + 历史经验
   → LLM 裁决 + 制定投资计划
   → state["investment_plan"] = "建议在当前价位买入..."
   → state["investment_debate_state"].judge_decision = "综合分析..."

8. Trader 节点
   → 读取投资计划 + 所有报告
   → LLM 制定具体交易方案
   → state["trader_investment_plan"] = "FINAL TRANSACTION PROPOSAL: **BUY**"

9. Aggressive / Conservative / Neutral 风控辩论
   → 读取交易方案 + 所有报告
   → 三方辩论

10. Risk Manager 节点
    → 综合风控辩论 + 交易方案 + 历史经验
    → LLM 裁决
    → state["final_trade_decision"] = "综合分析...建议 BUY"

11. SignalProcessor
    → 从长文本中提取: "BUY"

12. ReportGenerator
    → 翻译 → 生成 HTML → 合规检查 → 保存报告
```

---

## 六、关键设计决策

### 6.1 为什么用两套 LLM 模型？

```
deep_think_llm (gpt-5.2)     → 研究经理、风控经理（需要深度推理和判断）
quick_think_llm (gpt-5-mini)  → 分析师、研究员、交易员（常规分析和推理）
```

**原因**：深度推理模型贵且慢，只在关键决策点使用；快速模型便宜且快，用于大量数据分析和辩论。

### 6.2 为什么分析师串行而非并行？

分析师之间通过 `state["messages"]` 传递 LangChain 消息。串行设计确保：
- 每个分析师完成后清空消息（避免 token 溢出）
- 消息中不累积前一个分析师的工具调用结果

### 6.3 为什么辩论后需要"经理"裁决？

直接用辩论结果做决策的问题是：双方可能各执一词，难以给出明确结论。经理角色负责：
- 总结双方核心论点
- 做出明确决策（BUY / SELL / HOLD）
- 制定可执行的投资计划

### 6.4 为什么记忆用 BM25 而不是向量数据库？

- BM25 是纯本地算法，不需要 API 调用
- 金融文本关键词匹配效果好
- 零额外依赖，离线可用

---

## 七、目录结构速查

```
tradingagents/
├── agents/                          # 🤖 代理层
│   ├── analysts/                    #   分析师（市场/情绪/新闻/基本面）
│   ├── researchers/                 #   研究员（牛方/熊方）
│   ├── risk_mgmt/                   #   风控辩论者（激进/保守/中立）
│   ├── managers/                    #   经理（研究经理/风控经理）
│   ├── trader/                      #   交易员
│   ├── compliance/                  #   合规检查（术语替换）
│   └── utils/                       #   状态定义、工具函数、记忆系统
│       ├── agent_states.py          #     所有状态类型定义（必读）
│       ├── agent_utils.py           #     工具导入和消息清理
│       ├── memory.py                #     BM25 记忆系统
│       ├── core_stock_tools.py      #     @tool: get_stock_data
│       ├── technical_indicators_tools.py  # @tool: get_indicators
│       ├── fundamental_data_tools.py     # @tool: get_fundamentals...
│       └── news_data_tools.py       #     @tool: get_news, get_global_news
│
├── dataflows/                       # 📊 数据获取层
│   ├── interface.py                 #   路由器（route_to_vendor）
│   ├── config.py                    #   运行时配置管理
│   ├── logging_config.py            #   日志配置
│   ├── y_finance.py                 #   yfinance 数据源
│   ├── alpha_vantage.py             #   Alpha Vantage 数据源
│   ├── alpha_vantage_common.py      #   自定义异常 AlphaVantageRateLimitError
│   ├── sina_finance.py              #   新浪财经数据源（A 股）
│   ├── akshare_news.py              #   akshare 新闻数据源
│   └── akshare_fundamentals.py      #   akshare 基本面数据源
│
├── graph/                           # 🔀 图编排层
│   ├── trading_graph.py             #   主入口类 TradingAgentsGraph（必读）
│   ├── setup.py                     #   图构建（节点、边定义）
│   ├── conditional_logic.py         #   条件分支逻辑
│   ├── propagation.py               #   状态初始化
│   ├── reflection.py                #   反思和经验存储
│   ├── signal_processing.py         #   信号提取（BUY/SELL/HOLD）
│   └── report_generator.py          #   报告生成、翻译、合规
│
├── llm_clients/                     # 🧠 LLM 客户端层
│   ├── base_client.py               #   抽象基类（超时保护）
│   ├── factory.py                   #   工厂函数（必读）
│   ├── openai_client.py             #   OpenAI/兼容客户端
│   ├── google_client.py             #   Google Gemini 客户端
│   ├── anthropic_client.py          #   Anthropic Claude 客户端
│   └── validators.py                #   模型名称验证
│
├── utils/                           # 🔧 通用工具
│   └── html_to_jpg.py               #   HTML 转 JPG
│
├── default_config.py                # 默认配置字典（必读）
└── __init__.py                      # 模块导出

cli/                                 # 💻 CLI 入口
├── main.py                          #   Typer 应用（必读）
├── config.py                        #   CLI 配置
├── models.py                        #   数据模型
├── stats_handler.py                 #   LLM/工具调用统计
└── utils.py                         #   CLI 工具函数
```

---

## 八、如何添加一个新角色？

以添加"宏观经济分析师"为例：

**第 1 步**：创建代理文件 `agents/analysts/macro_analyst.py`
```python
def create_macro_analyst(llm):
    def macro_analyst_node(state):
        ticker = state["company_of_interest"]
        # ... 构建 prompt，调用工具 ...
        return {"macro_report": report}
    return macro_analyst_node
```

**第 2 步**：在 `agents/utils/agent_states.py` 中添加状态字段
```python
class AgentState(MessagesState):
    macro_report: Annotated[str, "Report from the Macro Analyst"]
```

**第 3 步**：在 `graph/setup.py` 中注册节点和边

**第 4 步**：在 `agents/__init__.py` 中导出

---

## 九、常见问题

**Q: 修改了代码，需要重启吗？**
A: 如果修改了代理的 prompt 或逻辑，需要重新创建 `TradingAgentsGraph` 实例。

**Q: 如何使用本地模型？**
A: 安装 Ollama 后，配置 `llm_provider: "ollama"` 即可。

**Q: 辩论轮数越多越好吗？**
A: 不是。轮数越多消耗的 token 越多。一般 1 轮已足够，复杂场景可设为 2-3 轮。

**Q: 数据获取失败怎么办？**
A: 系统会自动 fallback 到其他供应商。如果所有供应商都失败，检查 API 密钥和网络连接。
