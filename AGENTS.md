# AGENTS.md - TradingAgents 开发指南

TradingAgents 是一个基于 LangGraph 的多代理 LLM 金融交易框架。

**技术栈**: Python ≥3.10, LangGraph, LangChain, yfinance, Alpha Vantage, sina_finance, akshare

## 构建和测试命令

### 环境设置

```bash
bash scripts/setup_conda_env.sh && conda activate tradingagents
# 或手动: conda create -n tradingagents python=3.10 -y && pip install -r requirements.txt
```

**⚠️ 每次运行前必须激活环境**: `conda activate tradingagents`

### 运行与测试

```bash
conda activate tradingagents

# 主程序
python -m cli.main                          # CLI 界面
python main.py                              # 示例

# 测试（根目录独立脚本）
python test.py                              # 主测试
python test_news_api.py                     # 新闻 API
python test_a_share_indicators.py           # A 股指标
python test_a_share_fundamentals.py         # A 股基本面

# pytest（tests/ 目录）
pytest tests/                               # 全部测试
pytest tests/test_compliance_agent.py       # 单文件
pytest tests/test_compliance_agent.py::test_decision_terms_buy  # 单函数
pytest tests/ -k "compliance"               # 按名称匹配
pytest test_news_api.py::test_yfinance_news # 根目录测试
```

### 代码质量

```bash
mypy tradingagents/          # 类型检查
black tradingagents/         # 格式化
ruff check tradingagents/    # lint
```

**注意**: 项目无 ruff/black/mypy 专用配置，使用工具默认设置。

## 项目结构

```
tradingagents/
├── agents/          # 各类代理（分析师、研究员、风控、交易员、合规）
├── dataflows/       # 数据获取层（多供应商路由 + fallback）
├── graph/           # LangGraph 图构建
├── llm_clients/     # LLM 客户端抽象与工厂
└── utils/           # 通用工具
tests/               # 测试套件
```

## 代码风格

### 命名约定

| 类型 | 约定 | 示例 |
|------|------|------|
| 函数 | snake_case | `create_risk_manager()` |
| 类 | PascalCase | `TradingAgentsGraph`, `BaseLLMClient` |
| 常量 | UPPER_SNAKE_CASE | `DEFAULT_CONFIG`, `VENDOR_METHODS` |
| 私有 | 前缀下划线 | `_config`（模块内全局） |
| 代理工厂 | `create_` 前缀 | `create_fundamentals_analyst(llm)` |
| 异常类 | 描述性后缀 | `AlphaVantageRateLimitError` |

### 导入组织

- 标准库 → 第三方库 → 本地模块（绝对导入）。
- 可选依赖使用 `try/except ImportError` 保护。

### 类型提示

- 公共函数必须有完整类型提示。
- LangGraph 工具函数使用 `Annotated[type, "description"]`。
- 状态定义使用 `TypedDict` + `Annotated`。

### 文档字符串

使用 Google 风格 docstring，支持中英文混合。

### 错误处理

- **工具函数**: 返回错误消息字符串（不抛异常）。
- **数据层**: 自定义异常触发供应商 fallback。
- **模块级**: config 校验抛 `ValueError`。

### 日志规范

- 使用 `logging.getLogger(__name__)`。
- 日志标签：`[ROUTE_DECISION]`, `[RATE_LIMIT]`, `[VENDOR_ERROR]`。
- 配置位于 `dataflows/logging_config.py`，日志文件：`./logs/tradingagents.log`。

## 设计模式

### 工厂模式（代理节点）

所有代理通过闭包工厂 `create_xxx(llm)` 创建，返回符合 LangGraph 的节点函数。节点返回字典，仅包含**更新的** state 字段。

### 路由器模式（数据供应商）

`dataflows/interface.py` 实现多供应商路由 + fallback。优先级：工具级 > 类别级 > 默认值。仅 `AlphaVantageRateLimitError` 触发 fallback。

### LLM 客户端模式

- 工厂函数 `create_llm_client()` 创建客户端。
- 支持超时保护 `invoke_with_timeout()`。

### 配置管理

- 必须使用 `DEFAULT_CONFIG.copy()`，禁止原地修改。
- 运行时配置通过 `dataflows/config.py` 的 `get_config()` / `set_config()` 管理。

## 环境变量

从 `.env.example` 复制，或直接 export：

```bash
OPENAI_API_KEY=          # OpenAI（默认）
GOOGLE_API_KEY=          # Google Gemini
ANTHROPIC_API_KEY=       # Anthropic Claude
XAI_API_KEY=             # xAI Grok
OPENROUTER_API_KEY=      # OpenRouter
ZHIPU_API_KEY=           # 智谱
ALPHA_VANTAGE_API_KEY=   # Alpha Vantage（可选）
```

## 重要约束

1. **强制环境隔离**: 必须在 `conda activate tradingagents` 后操作
2. **配置复制**: 始终使用 `DEFAULT_CONFIG.copy()`，禁止修改原字典
3. **节点返回格式**: 代理节点返回字典，仅包含更新的 state 字段
4. **工具函数返回值**: 返回字符串（成功 = 数据，失败 = 错误消息），不抛异常
5. **LLM 超时保护**: 所有 LLM 调用需通过 `BaseLLMClient.invoke_with_timeout()` 或配置 `llm_invoke_timeout`
6. **状态定义集中**: 所有 LangGraph 状态类型在 `agents/utils/agent_states.py`

## 故障排查

| 问题 | 解决方案 |
|------|----------|
| API 限流 (429) | 增大 `max_llm_retries` 或切换数据供应商 |
| LLM 调用超时 | 调整 `llm_invoke_timeout`（默认 120s） |
| 导入错误 | 激活 conda 环境后重装依赖 |
| 数据获取失败 | 检查 API 密钥，查看日志 `./logs/tradingagents.log` |
