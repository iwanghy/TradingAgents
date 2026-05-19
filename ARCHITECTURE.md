# TradingAgents 技术栈与架构文档

> 本文档详细描述 TradingAgents 项目的技术栈、模块架构和核心设计模式。

## 目录

- [技术栈概览](#技术栈概览)
- [项目结构](#项目结构)
- [核心模块](#核心模块)
  - [多代理系统 (agents)](#1-多代理系统-agents)
  - [数据获取层 (dataflows)](#2-数据获取层-dataflows)
  - [LangGraph 工作流 (graph)](#3-langgraph-工作流-graph)
  - [LLM 客户端 (llm_clients)](#4-llm-客户端-llm_clients)
  - [命令行界面 (cli)](#5-命令行界面-cli)
- [设计模式](#设计模式)
- [配置管理](#配置管理)
- [日志系统](#日志系统)
- [关键约束](#关键约束)

---

## 技术栈概览

### 核心框架

| 类别 | 技术 | 版本要求 | 用途 |
|------|------|----------|------|
| **工作流编排** | LangGraph | ≥0.4.8 | 多代理状态机编排 |
| **LLM 集成** | LangChain | ≥0.3.81 | AI 模型统一抽象 |
| **编程语言** | Python | ≥3.10 | 项目语言 |

### LangChain 生态

| 包 | 版本 | 用途 |
|----|------|------|
| `langchain-core` | ≥0.3.81 | 核心抽象与接口 |
| `langchain-openai` | ≥0.3.23 | OpenAI GPT 系列 |
| `langchain-anthropic` | ≥0.3.15 | Anthropic Claude 系列 |
| `langchain-google-genai` | ≥2.1.5 | Google Gemini 系列 |
| `langchain-experimental` | ≥0.3.4 | 实验性功能 |

### LLM 提供商支持

| 提供商 | 模型系列 | 客户端类 |
|--------|----------|----------|
| OpenAI | GPT-5.x, GPT-4.1.x, o3/o1 | OpenAIClient |
| Anthropic | Claude Opus/Sonnet/Haiku 4-5 | AnthropicClient |
| Google | Gemini 3.x/2.5/2.0 | GoogleClient |
| xAI | Grok-4.x | OpenAIClient |
| OpenRouter | 聚合模型 | OpenAIClient |
| 智谱 (Zhipu) | GLM-4.x/4.7.x | OpenAIClient |
| Ollama | 本地模型 | OpenAIClient |

### 数据供应商

| 供应商 | 覆盖市场 | 数据类型 | 费用 |
|--------|----------|----------|------|
| **Alpha Vantage** | 美股、国际 | 股价、技术指标、基本面、新闻 | 免费额度/API Key |
| **Yahoo Finance** | 美股、港股、A股 | 股价、技术指标、新闻 | 免费 |
| **新浪财经** | A股 | 实时行情、财务数据 | 免费 |
| **AKShare** | A股 | 基本面、新闻、内幕交易 | 免费 |

### 数据处理与分析

| 包 | 版本 | 用途 |
|----|------|------|
| `pandas` | ≥2.3.0 | 数据结构与分析 |
| `stockstats` | ≥0.6.5 | 股票技术指标计算 |
| `backtrader` | ≥1.9.78.123 | 回测引擎 |
| `rank-bm25` | ≥0.2.2 | BM25 文本检索 |

### 命令行与界面

| 包 | 版本 | 用途 |
|----|------|------|
| `chainlit` | ≥2.5.5 | Web 聊天界面 |
| `typer` | ≥0.21.0 | CLI 框架 |
| `rich` | ≥14.0.0 | 富文本终端输出 |
| `questionary` | ≥2.1.0 | 交互式提示 |

### 基础设施

| 包 | 版本 | 用途 |
|----|------|------|
| `requests` | ≥2.32.4 | HTTP 客户端 |
| `redis` | ≥6.2.0 | 缓存与状态存储 |
| `tqdm` | ≥4.67.1 | 进度条 |
| `pytz` | ≥2025.2 | 时区处理 |

---

## 项目结构

```
TradingAgents/
├── tradingagents/                 # 主源代码包
│   ├── agents/                    # 多代理系统 (13个代理)
│   │   ├── analysts/               # 分析师团队 (4个)
│   │   │   ├── fundamentals_analyst.py
│   │   │   ├── market_analyst.py
│   │   │   ├── news_analyst.py
│   │   │   └── social_media_analyst.py
│   │   ├── researchers/            # 研究员团队 (2个)
│   │   │   ├── bull_researcher.py
│   │   │   └── bear_researcher.py
│   │   ├── managers/               # 管理层 (2个)
│   │   │   ├── research_manager.py
│   │   │   └── risk_manager.py
│   │   ├── risk_mgmt/              # 风险管理团队 (3个)
│   │   │   ├── aggressive_debator.py
│   │   │   ├── conservative_debator.py
│   │   │   └── neutral_debator.py
│   │   ├── trader/                 # 交易员 (1个)
│   │   │   └── trader.py
│   │   ├── compliance/             # 合规检查 (1个)
│   │   │   ├── compliance_officer.py
│   │   │   └── rules.py
│   │   └── utils/                  # 代理工具
│   │       ├── agent_states.py     # 状态定义 (TypedDict)
│   │       ├── agent_utils.py      # 工厂函数
│   │       ├── memory.py           # 记忆管理
│   │       ├── core_stock_tools.py
│   │       ├── technical_indicators_tools.py
│   │       ├── fundamental_data_tools.py
│   │       └── news_data_tools.py
│   ├── dataflows/                  # 数据获取层
│   │   ├── interface.py            # 路由器核心
│   │   ├── config.py               # 运行时配置
│   │   ├── alpha_vantage*.py       # Alpha Vantage 客户端 (4个)
│   │   ├── y_finance.py            # Yahoo Finance 客户端
│   │   ├── sina_finance.py         # 新浪财经 (A股)
│   │   ├── akshare*.py             # AKShare (A股)
│   │   └── data_cache/             # 数据缓存
│   ├── graph/                      # LangGraph 工作流
│   │   ├── trading_graph.py        # 主图入口类
│   │   ├── setup.py                # 图节点初始化
│   │   ├── propagation.py          # 前向传播
│   │   ├── conditional_logic.py    # 条件路由
│   │   ├── signal_processing.py   # 信号处理
│   │   ├── reflection.py           # 反思机制
│   │   └── report_generator.py    # 报告生成
│   ├── llm_clients/                # LLM 客户端抽象
│   │   ├── base_client.py          # 抽象基类 + 超时保护
│   │   ├── factory.py              # 工厂函数
│   │   ├── openai_client.py        # OpenAI 兼容客户端
│   │   ├── anthropic_client.py     # Claude 客户端
│   │   ├── google_client.py        # Gemini 客户端
│   │   └── validators.py           # 模型白名单验证
│   └── utils/
│       └── html_to_jpg.py          # 报告可视化
├── cli/                            # 命令行界面
│   └── main.py                     # CLI 主入口 (Typer + Rich)
├── tests/                          # Pytest 测试套件
├── scripts/                        # 工具脚本
├── logs/                           # 日志输出
├── reports/                        # 交易报告
├── eval_results/                   # 评估结果
├── requirements.txt                # 依赖清单 (25个包)
├── pyproject.toml                  # 项目构建配置 (21个包+版本)
└── .env.example                    # 环境变量模板
```

---

## 核心模块

### 1. 多代理系统 (agents)

#### 1.1 代理架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│                        TradingAgents                            │
│                                                                 │
│  ┌──────────────┐                                               │
│  │   Analysts   │ ──▶ Market / Social / News / Fundamentals     │
│  │   (4 agents) │                                               │
│  └──────┬───────┘                                               │
│         ▼                                                       │
│  ┌──────────────┐                                               │
│  │  Researchers │ ──▶ Bull / Bear (多空辩论)                     │
│  │  (2 agents) │                                               │
│  └──────┬───────┘                                               │
│         ▼                                                       │
│  ┌──────────────┐                                               │
│  │   Research   │ ──▶ Research Manager (汇总辩论,制定投资计划)   │
│  │   Manager    │                                               │
│  └──────┬───────┘                                               │
│         ▼                                                       │
│  ┌──────────────┐                                               │
│  │    Trader    │ ──▶ 基于投资计划给出初步交易建议               │
│  └──────┬───────┘                                               │
│         ▼                                                       │
│  ┌──────────────┐                                               │
│  │Risk Mgmt Team│ ──▶ Aggressive / Conservative / Neutral       │
│  │  (3 agents)  │                                               │
│  └──────┬───────┘                                               │
│         ▼                                                       │
│  ┌──────────────┐                                               │
│  │  Risk Judge  │ ──▶ 最终决策 BUY / SELL / HOLD                │
│  └──────┬───────┘                                               │
│         ▼                                                       │
│  ┌──────────────┐                                               │
│  │ Compliance   │ ──▶ 合规检查 (独立流程)                        │
│  └──────────────┘                                               │
└─────────────────────────────────────────────────────────────────┘
```

#### 1.2 代理类型详解

| 类型 | 代理 | 工厂函数 | 职责 |
|------|------|----------|------|
| **分析师** | 市场分析师 | `create_market_analyst(llm)` | 技术分析 (MACD, RSI, Bollinger Bands, SMA/EMA) |
| | 社交媒体分析师 | `create_social_media_analyst(llm)` | 社交媒体情绪分析 |
| | 新闻分析师 | `create_news_analyst(llm)` | 全球新闻与宏观事件 |
| | 基本面分析师 | `create_fundamentals_analyst(llm)` | 财务数据、资产负债表、现金流 |
| **研究员** | 看涨研究员 | `create_bull_researcher(llm, memory)` | 寻找增长机会,论证买入 |
| | 看跌研究员 | `create_bear_researcher(llm, memory)` | 识别风险,论证卖出 |
| **管理** | 研究经理 | `create_research_manager(llm, memory)` | 协调辩论,制定投资计划 |
| | 风险经理 | `create_risk_manager(llm, memory)` | 协调风险辩论,给出最终决策 |
| **风险** | 激进辩论者 | `create_aggressive_debator(llm)` | 高风险高收益视角 |
| | 保守辩论者 | `create_conservative_debator(llm)` | 风险规避视角 |
| | 中立辩论者 | `create_neutral_debator(llm)` | 平衡视角 |
| **执行** | 交易员 | `create_trader(llm, memory)` | 初步交易决策 |
| **合规** | 合规官 | `create_compliance_officer(llm_client, timeout)` | 平台合规检查 (独立流程) |

#### 1.3 工厂模式实现

所有代理通过**闭包工厂函数**创建：

```python
def create_agent_name(llm, memory=None):
    """工厂函数,返回符合 LangGraph 的节点函数"""
    def agent_node(state: AgentState) -> dict:
        # 1. 从 state 提取必要信息
        # 2. 调用 LLM 获取响应
        # 3. 更新 state 字段
        return {"field_name": updated_value}
    return agent_node
```

**节点返回格式**: 返回字典,仅包含**更新的** state 字段。

#### 1.4 状态定义

| 状态类型 | 文件 | 用途 |
|----------|------|------|
| `AgentState` | agent_states.py | 主状态,继承 LangGraph `MessagesState` |
| `InvestDebateState` | agent_states.py | 投资辩论状态 (Bull/Bear) |
| `RiskDebateState` | agent_states.py | 风险辩论状态 (Aggressive/Conservative/Neutral) |

**AgentState 核心字段**:

```python
class AgentState(MessagesState):
    # 基本信息
    company_of_interest: str   # 目标公司
    trade_date: str             # 交易日期
    
    # 分析师报告
    market_report: str          # 市场分析报告
    sentiment_report: str        # 情绪分析报告
    news_report: str            # 新闻分析报告
    fundamentals_report: str     # 基本面分析报告
    
    # 投资辩论
    investment_debate_state: InvestDebateState
    trader_investment_plan: str  # 交易员初步计划
    
    # 风险辩论
    risk_debate_state: RiskDebateState
    final_trade_decision: str   # 最终决策 BUY/SELL/HOLD
```

---

### 2. 数据获取层 (dataflows)

#### 2.1 架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                     Dataflows Router                             │
│                                                                  │
│  route_to_vendor(method, *args, **kwargs)                        │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 配置层级优先级:                                              │ │
│  │ 1. tool_vendors[method]  (工具级,最高优先)                   │ │
│  │ 2. data_vendors[category] (类别级)                         │ │
│  │ 3. default_vendors  (默认值)                                 │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Vendor Methods Mapping (VENDOR_METHODS)                      │ │
│  │  get_stock_data        → [alpha_vantage, yfinance, sina]    │ │
│  │  get_indicators        → [alpha_vantage, yfinance]         │ │
│  │  get_fundamentals      → [akshare, alpha_vantage, yfinance]│ │
│  │  get_news              → [akshare, alpha_vantage, yfinance]│ │
│  │  get_balance_sheet     → [akshare, alpha_vantage, yfinance]│ │
│  │  get_insider_transactions → [alpha_vantage, yfinance]      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│            ┌─────────────────┼─────────────────┐                │
│            ▼                 ▼                 ▼                │
│    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐          │
│    │ Alpha       │   │ Yahoo       │   │ Sina/AKShare │          │
│    │ Vantage     │   │ Finance     │   │ (A股专用)    │          │
│    └─────────────┘   └─────────────┘   └─────────────┘          │
│            │                 │                 │                │
│            └─────────────────┼─────────────────┘                │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Fallback 机制:                                               │ │
│  │  - AlphaVantageRateLimitError → 自动切换到下一个供应商       │ │
│  │  - 其他异常 → 直接抛出                                      │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

#### 2.2 数据类别

| 类别 | 方法 | 默认供应商 | 覆盖市场 |
|------|------|-----------|----------|
| `core_stock_apis` | `get_stock_data` | sina_finance | A股实时,美股 |
| `technical_indicators` | `get_indicators` | yfinance | 美股,港股,A股 |
| `fundamental_data` | `get_fundamentals`, `get_balance_sheet` | sina_finance | A股 |
| `news_data` | `get_news`, `get_global_news` | akshare | A股,美股 |

#### 2.3 Fallback 机制

```python
# 触发条件
AlphaVantageRateLimitError  # → 触发 fallback

# 不触发 fallback
YFRateLimitError  # → 直接抛出
其他异常           # → 直接抛出
```

#### 2.4 A股特殊处理

- **新浪财经**: 支持 `sh600519` / `sz000001` 格式
- **AKShare**: 专门提供 A股基本面和新闻接口
- **baostock**: requirements.txt 中存在 (可选 A股数据源)

---

### 3. LangGraph 工作流 (graph)

#### 3.1 核心组件

| 文件 | 类 | 职责 |
|------|-----|------|
| `trading_graph.py` | `TradingAgentsGraph` | 主入口类,管理整个交易流程 |
| `setup.py` | `GraphSetup` | 使用 `StateGraph` 构建图结构和边 |
| `propagation.py` | `Propagator` | 初始状态创建和执行参数 |
| `conditional_logic.py` | `ConditionalLogic` | 定义所有条件边路由函数 |
| `reflection.py` | `Reflector` | 事后反思和记忆更新 |
| `signal_processing.py` | `SignalProcessor` | 处理最终交易信号 |
| `report_generator.py` | `ReportGenerator` | 生成 Markdown/HTML 报告 |

#### 3.2 图执行流程

```
START
  │
  ▼
┌─────────────────┐     ┌─────────────┐
│ Market Analyst  │────▶│ tools_market│
└────────┬────────┘     └──────▲──────┘
         │                    │
         ▼ (无tool_calls)      │
┌─────────────────┐            │
│Msg Clear Market │            │
└────────┬────────┘            │
         ▼                     │
┌─────────────────┐     ┌─────────────┐
│ Social Analyst  │────▶│ tools_social│
└────────┬────────┘     └──────▲──────┘
         │                    │
         ▼                    │
┌─────────────────┐            │
│Msg Clear Social │            │
└────────┬────────┘            │
         ▼                     │
┌─────────────────┐     ┌─────────────┐
│ News Analyst    │────▶│ tools_news  │
└────────┬────────┘     └──────▲──────┘
         │                    │
         ▼                    │
┌─────────────────┐            │
│Msg Clear News   │            │
└────────┬────────┘            │
         ▼                     │
┌─────────────────┐     ┌──────────────────┐
│Fundamentals     │────▶│tools_fundamentals│
│    Analyst       │     └──────▲───────────┘
└────────┬────────┘            │
         │                    │
         ▼ (无tool_calls)      │
┌─────────────────┐            │
│Msg Clear Fund. │            │
└────────┬────────┘            │
         ▼                     │
┌─────────────────┐     ┌─────────────┐
│ Bull Researcher │◀───▶│ Bear        │
└────────┬────────┘     │ Researcher  │
         │              └──────▲──────┘
         │                     │
         ▼ (达到辩论轮数上限)    │
┌─────────────────┐            │
│Research Manager │            │
└────────┬────────┘            │
         ▼                     │
┌─────────────────┐            │
│     Trader      │            │
└────────┬────────┘            │
         ▼                     │
┌─────────────────┐            │
│  Aggressive    │◀───┐        │
│   Debator       │    │       │
└────────┬────────┘    │       │
         │             │       │
         ▼             │       │
┌─────────────────┐    │       │
│ Conservative    │────▶│       │
│   Debator       │    │       │
└────────┬────────┘    │       │
         │             │       │
         ▼             │       │
┌─────────────────┐    │       │
│   Neutral      │────┘       │
│   Debator      │            │
└────────┬────────┘            │
         │                     │
         ▼ (达到辩论轮数上限)   │
┌─────────────────┐            │
│   Risk Judge    │            │
└────────┬────────┘            │
         ▼                     │
       END
```

#### 3.3 条件边逻辑

```python
# 分析师条件边
should_continue_market(state)   → "tools_market" | "Msg Clear Market"
should_continue_social(state)   → "tools_social" | "Msg Clear Social"
should_continue_news(state)     → "tools_news" | "Msg Clear News"
should_continue_fundamentals(state) → "tools_fundamentals" | "Msg Clear Fundamentals"

# 研究员辩论条件边
should_continue_debate(state)   → "Bull Researcher" | "Bear Researcher" | "Research Manager"
# 逻辑: count >= 2 * max_debate_rounds → Research Manager

# 风险分析条件边
should_continue_risk_analysis(state) → "Aggressive" | "Conservative" | "Neutral" | "Risk Judge"
# 逻辑: count >= 3 * max_risk_discuss_rounds → Risk Judge
```

#### 3.4 使用示例

```python
from tradingagents.graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 初始化
ta = TradingAgentsGraph(
    selected_analysts=["market", "social", "news", "fundamentals"],
    debug=False,
    config=DEFAULT_CONFIG.copy()
)

# 执行
final_state, decision = ta.propagate("NVDA", "2026-01-15")

# 输出
# final_trade_decision: "BUY" / "SELL" / "HOLD"
```

---

### 4. LLM 客户端 (llm_clients)

#### 4.1 架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                    LLM Client Factory                           │
│                                                                  │
│  create_llm_client(provider, model, base_url, **kwargs)          │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Provider → Client Class Mapping:                           │ │
│  │                                                            │ │
│  │  openai / ollama / openrouter / zhipu / infini            │ │
│  │    └───────────▶ OpenAIClient                             │ │
│  │                                                            │ │
│  │  xai ─────────────────▶ OpenAIClient (使用 x.ai 端点)       │ │
│  │                                                            │ │
│  │  anthropic ────────────▶ AnthropicClient                  │ │
│  │                                                            │ │
│  │  google ───────────────▶ GoogleClient                      │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    BaseLLMClient                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  abstract get_llm() -> LangChain LLM                       │ │
│  │  abstract validate_model(model) -> bool                     │ │
│  │                                                              │ │
│  │  invoke_with_timeout(messages, max_retries=2)              │ │
│  │  ┌──────────────────────────────────────────────────────┐   │ │
│  │  │ ThreadPoolExecutor + timeout (默认 120s)            │   │ │
│  │  │ 超时重试,日志标签:                                    │   │ │
│  │  │   [LLM_TIMEOUT] / [LLM_ERROR] / [LLM_RETRY_SUCCESS] │   │ │
│  │  └──────────────────────────────────────────────────────┘   │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

#### 4.2 客户端特性

| 客户端 | 特性 |
|--------|------|
| **OpenAIClient** | 推理模型 (o1/o3/gpt-5) 自动移除 `temperature`/`top_p` |
| **GoogleClient** | `NormalizedChatGoogleGenerativeAI` 适配器,统一内容格式 |
| **AnthropicClient** | 支持 `max_tokens` 参数 |

#### 4.3 配置参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `timeout` | HTTP 请求超时 (秒) | - |
| `max_retries` | HTTP 请求重试次数 | - |
| `invoke_timeout` | LLM 调用总超时 (秒) | 120 |

#### 4.4 模型验证

`validators.py` 定义各提供商合法模型白名单:

```python
VALID_MODELS = {
    "openai": ["gpt-5.x", "gpt-4.1.x", "o3", "o1", ...],
    "anthropic": ["claude-opus-4-5", "claude-sonnet-4-5", "claude-haiku-4-5", ...],
    "google": ["gemini-3", "gemini-2.5", "gemini-2.0", ...],
    "xai": ["grok-4", "grok-4-beta", ...],
    "zhipu": ["glm-4", "glm-4-7", ...],
}
# ollama / openrouter: 允许任意模型名
```

---

### 5. 命令行界面 (cli)

基于 **Typer + Rich** 构建的交互式命令行:

```bash
# 激活环境
conda activate tradingagents

# 启动 CLI
python -m cli.main

# 示例运行
python main.py
```

---

## 设计模式

### 1. 工厂模式 (代理创建)

```python
def create_xxx_analyst(llm):
    def node(state: AgentState) -> dict:
        # 代理逻辑
        return {"report": content}
    return node
```

### 2. 路由器模式 (数据供应商)

```python
def route_to_vendor(method, *args, **kwargs):
    # 1. 工具级配置优先
    # 2. 类别级配置次之
    # 3. 默认值兜底
    # 4. AlphaVantageRateLimitError 触发 fallback
```

### 3. 策略模式 (LLM 提供商)

```python
def create_llm_client(provider, model, base_url, **kwargs):
    # 根据 provider 选择具体策略 (客户端实现)
```

### 4. 状态机模式 (LangGraph)

```python
graph = StateGraph(AgentState)
graph.add_node("analyst", analyst_node)
graph.add_edge("analyst", "researcher")
graph.add_conditional_edges("researcher", should_continue_debate, ...)
```

---

## 配置管理

### 配置层级

```
tool_vendors[method]  >  data_vendors[category]  >  default_config
```

### 运行时配置

```python
from tradingagents.dataflows.config import get_config, set_config

# 获取当前配置
config = get_config()

# 修改配置
set_config({"llm_provider": "anthropic"})
```

### 环境变量

从 `.env.example` 复制:

```bash
OPENAI_API_KEY=
GOOGLE_API_KEY=
ANTHROPIC_API_KEY=
XAI_API_KEY=
OPENROUTER_API_KEY=
ZHIPU_API_KEY=
ALPHA_VANTAGE_API_KEY=
```

---

## 日志系统

### 日志配置

- **配置文件**: `tradingagents/dataflows/logging_config.py`
- **日志文件**: `./logs/tradingagents.log`
- **日志级别**:
  - 全局: INFO (可配置 DEBUG/WARNING/ERROR/CRITICAL)
  - 数据层: DEBUG (更详细的 API 调用日志)

### 日志标签

| 标签 | 用途 |
|------|------|
| `[ROUTE_DECISION]` | 路由决策 |
| `[ROUTE_ATTEMPT]` | 尝试供应商 |
| `[ROUTE_SUCCESS]` | 路由成功 |
| `[RATE_LIMIT]` | 速率限制 |
| `[VENDOR_ERROR]` | 供应商错误 |
| `[LLM_TIMEOUT]` | LLM 调用超时 |
| `[LLM_ERROR]` | LLM 调用错误 |
| `[LLM_RETRY_SUCCESS]` | LLM 重试成功 |

---

## 关键约束

| 约束 | 说明 |
|------|------|
| **环境隔离** | 必须 `conda activate tradingagents` |
| **配置复制** | 必须 `DEFAULT_CONFIG.copy()`, 禁止原地修改 |
| **节点返回** | 代理节点返回字典, 仅包含更新的 state 字段 |
| **工具错误** | 返回错误消息字符串, 不抛异常 |
| **LLM 超时** | 所有 LLM 调用通过 `invoke_with_timeout()` |
| **状态定义** | 所有 LangGraph 状态在 `agent_states.py` |
| **导入组织** | 标准库 → 第三方 → 本地模块 |

---

## 快速开始

```bash
# 环境设置
bash scripts/setup_conda_env.sh && conda activate tradingagents

# CLI 运行
python -m cli.main

# 示例
python main.py

# 测试
pytest tests/
python test.py
```

---

*文档生成时间: 2026-03-31*
