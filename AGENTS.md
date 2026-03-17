# AGENTS.md - TradingAgents 开发指南

TradingAgents 是一个基于 LangGraph 的多代理 LLM 金融交易框架。

**技术栈**: Python 3.10+, LangGraph, LangChain, yfinance, Alpha Vantage, sina_finance, akshare

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
python -m cli.main                          # CLI 交互界面
python main.py                              # 示例脚本
python test.py                              # 主测试
python test_news_api.py                     # 新闻 API 测试

# pytest 单个测试
pytest test_news_api.py::test_yfinance_news
pytest test_a_share_indicators.py -k "sina"

# HTML 转 JPG
python -m cli.main convert-jpg reports/sample.html              # 基本用法
python -m cli.main convert-jpg reports/sample.html -o /path/to/output  # 指定输出目录
python -m cli.main convert-jpg reports/sample.html --quality 90  # 设置图片质量
python -m cli.main convert-jpg reports/sample.html --segment     # 启用分段模式
```

**注意**: `convert-jpg` 命令需要系统依赖 `wkhtmltoimage`
```bash
# Ubuntu/Debian 安装
sudo apt-get install wkhtmltopdf
```

### 代码质量

```bash
mypy tradingagents/     # 类型检查
black tradingagents/    # 格式化
ruff check tradingagents/  # lint
```

## 代码风格

| 类型 | 约定 | 示例 |
|------|------|------|
| 函数 | snake_case | `create_risk_manager()` |
| 类 | PascalCase | `TradingAgentsGraph` |
| 常量 | UPPER_SNAKE_CASE | `DEFAULT_CONFIG` |
| 私有 | 前缀下划线 | `_is_reasoning_model()` |

### 导入组织

```python
# 标准库
from typing import Dict, Any, Optional, Annotated

# 第三方库
from langgraph.graph import StateGraph

# 本地模块
from tradingagents.llm_clients import create_llm_client
from tradingagents.default_config import DEFAULT_CONFIG
```

### 类型提示

```python
# 公共函数必须有类型提示
def function_name(param1: str, param2: Optional[Dict[str, Any]] = None) -> List[str]:
    pass

# 工具函数使用 Annotated（供 LLM 理解）
def get_stock_data(symbol: Annotated[str, "ticker symbol"]) -> str:
    pass
```

### 设计模式

**工厂模式**（代理和 LLM 客户端）：
```python
def create_fundamentals_analyst(llm):
    def fundamentals_analyst_node(state):
        return {"fundamentals_report": report}
    return fundamentals_analyst_node
```

**路由器模式**（数据供应商）：
```python
from tradingagents.dataflows.interface import route_to_vendor
result = route_to_vendor("get_stock_data", "AAPL", "2024-01-01", "2024-01-31")
```

### 错误处理

```python
# 工具函数：返回错误消息字符串
if data.empty:
    return f"No data found for symbol '{symbol}'"

# 数据层：使用自定义异常触发 fallback
except AlphaVantageRateLimitError:
    continue
```

## 配置管理

**始终复制配置**: `config = DEFAULT_CONFIG.copy()`

| 配置项 | 默认值 |
|--------|--------|
| `llm_provider` | `"openai"` |
| `deep_think_llm` | `"gpt-5.2"` |
| `quick_think_llm` | `"gpt-5-mini"` |
| `max_llm_retries` | `3` |
| `max_debate_rounds` | `1` |

**支持 LLM**: `openai`, `google`, `anthropic`, `xai`, `openrouter`, `ollama`

### 数据供应商配置

```python
config["data_vendors"] = {
    "core_stock_apis": "sina_finance",  # 避开 yfinance 限流
    "news_data": "akshare",
}
config["tool_vendors"] = {"get_stock_data": "alpha_vantage"}  # 优先级更高
```

**优先级**: 工具级配置 > 类别级配置 > 默认值

## LangGraph 开发

```python
def agent_node(state) -> dict:
    ticker = state["company_of_interest"]
    return {"field_name": result}  # 仅返回更新的 state 字段
```

状态定义: `tradingagents/agents/utils/agent_states.py`

## 项目结构

```
tradingagents/
├── agents/           # 代理: analysts/, researchers/, risk_mgmt/, trader/
├── dataflows/        # 数据获取层
├── graph/            # LangGraph 图构建
├── llm_clients/      # LLM 客户端工厂
└── default_config.py # 默认配置
```

## 环境变量

```bash
OPENAI_API_KEY=       # OpenAI
GOOGLE_API_KEY=       # Google Gemini
ANTHROPIC_API_KEY=    # Anthropic Claude
XAI_API_KEY=          # xAI Grok
ALPHA_VANTAGE_API_KEY=  # Alpha Vantage (可选)
```

## 重要约束

1. **强制环境隔离**: 必须在 `conda activate tradingagents` 后操作
2. **配置复制**: 始终使用 `DEFAULT_CONFIG.copy()`
3. **节点返回格式**: 代理节点返回字典，仅包含更新的 state 字段
4. **类型提示**: 公共函数必须有完整类型提示
5. **工具函数返回值**: 返回字符串（成功返回数据，失败返回错误消息）

## 故障排查

| 问题 | 解决方案 |
|------|----------|
| API 限流 (429) | 增大 `max_llm_retries` 或切换数据供应商 |
| 导入错误 | 激活 conda 环境后重装依赖 |
| 数据获取失败 | 检查 API 密钥，查看日志 `./logs/tradingagents.log` |
| 调试 | `TradingAgentsGraph(debug=True, config=config)` |
