# AGENTS.md - TradingAgents 开发指南

本文档为 AI 代理和开发者提供 TradingAgents 代码库的必要信息。

## 项目概述

TradingAgents 是一个基于 LangGraph 的多代理 LLM 金融交易框架。

**技术栈**: Python 3.10+, LangGraph, LangChain, yfinance, Alpha Vantage

**最低 Python 版本**: 3.10（推荐使用 3.10 或 3.13）

## 构建和测试命令

### 环境设置

**推荐使用 conda 环境隔离**：

```bash
# 方法 1: 使用自动化脚本（推荐）
bash scripts/setup_conda_env.sh
conda activate tradingagents

# 方法 2: 手动设置
conda create -n tradingagents python=3.10 -y
conda activate tradingagents
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 添加 API 密钥
```

**每次运行前确保激活环境**: `conda activate tradingagents`

### 运行应用

**⚠️ 重要：所有命令必须在激活的 conda 环境中运行**

```bash
# 1. 确保环境已激活
conda activate tradingagents

# 2. 运行 CLI
python -m cli.main

# 运行示例脚本
python main.py

# 运行测试
python test.py
```

### 测试

**⚠️ 必须在 conda 虚拟环境中运行测试**

项目使用简单的测试脚本（`test.py`），不使用 pytest 框架：

```bash
# 1. 确保环境已激活
conda activate tradingagents

# 2. 运行测试
python test.py

# 或使用模块方式运行
python -m test

# 如需 pytest 支持运行单个测试函数，需先安装 pytest：
pip install pytest
pytest test.py::test_function_name
pytest -k "test_pattern"
```

### 代码质量工具

**⚠️ 必须在 conda 虚拟环境中运行**

项目未配置自动化工具，建议手动运行：

```bash
# 1. 确保环境已激活
conda activate tradingagents

# 2. 安装工具（如未安装）
pip install mypy black ruff

# 3. 运行检查
mypy tradingagents/       # 类型检查
black tradingagents/ cli/ # 格式化
ruff check tradingagents/ cli/  # lint
```

## 代码风格指南

### 导入组织

按此顺序组织，用空行分隔：

1. 标准库
2. 第三方库
3. 本地模块

```python
# 标准库
import os
from datetime import date
from pathlib import Path
from typing import Dict, Any, Optional

# 第三方库
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph
import pandas as pd

# 本地模块
from tradingagents.llm_clients import create_llm_client
from tradingagents.default_config import DEFAULT_CONFIG
```

### 类型提示

使用 `typing` 模块，工具函数使用 `Annotated`：

```python
from typing import Annotated, Dict, Any, Optional, List

def function_name(
    param1: str,
    param2: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """函数文档字符串。"""
    pass

# 工具函数使用 Annotated
def get_stock_data(
    symbol: Annotated[str, "ticker symbol"],
    start_date: Annotated[str, "yyyy-mm-dd format"],
) -> str:
    pass
```

**规则**：公共函数必须有类型提示，使用 `Optional` 表示可选参数。

### 命名约定

| 类型 | 约定 | 示例 |
|------|------|------|
| 函数 | snake_case | `create_risk_manager()`, `get_stock_data()` |
| 类 | PascalCase | `TradingAgentsGraph`, `OpenAIClient` |
| 常量 | UPPER_SNAKE_CASE | `DEFAULT_CONFIG`, `TOOLS_CATEGORIES` |
| 变量 | snake_case | `company_name`, `market_research_report` |
| 私有 | 前缀下划线 | `_is_reasoning_model()` |

### 设计模式

**工厂模式**（代理和 LLM 客户端）：

```python
def create_fundamentals_analyst(llm):
    """返回节点函数供 LangGraph 使用。"""
    def fundamentals_analyst_node(state):
        return {"fundamentals_report": report}
    return fundamentals_analyst_node
```

**抽象基类**（LLM 客户端）：

```python
from abc import ABC, abstractmethod

class BaseLLMClient(ABC):
    @abstractmethod
    def get_llm(self) -> Any:
        pass
```

### 错误处理

```python
# 简单返回错误消息（工具函数常见）
if data.empty:
    return f"No data found for symbol '{symbol}'"

# 使用自定义异常
from .alpha_vantage_common import AlphaVantageRateLimitError
try:
    return impl_func(*args, **kwargs)
except AlphaVantageRateLimitError:
    continue  # 触发 fallback
```

### 文档字符串

使用简洁的 Google 风格：

```python
class TradingAgentsGraph:
    """协调交易代理框架的主类。"""

    def propagate(self, ticker: str, trade_date: str) -> Tuple[Dict, str]:
        """执行前向传播，返回状态和决策。"""
        pass
```

### 配置管理

配置存储在 `tradingagents/default_config.py`，**使用时始终复制**：

```python
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-5-mini"
config["max_llm_retries"] = 3  # 自动重试次数，处理 API 限流（429错误）
```

**重要配置项**：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `llm_provider` | LLM 提供商 | `"openai"` |
| `deep_think_llm` | 深度思考模型 | `"gpt-5.2"` |
| `quick_think_llm` | 快速思考模型 | `"gpt-5-mini"` |
| `max_llm_retries` | API 失败重试次数 | `3` |
| `max_debate_rounds` | 研究辩论轮数 | `1` |
| `max_risk_discuss_rounds` | 风险讨论轮数 | `1` |

**支持的 LLM 提供商**: `openai`, `google`, `anthropic`, `xai`, `openrouter`, `ollama`

**推理配置**：

```python
# Google 思考级别
config["google_thinking_level"] = "high"  # high, minimal

# OpenAI 推理强度
config["openai_reasoning_effort"] = "medium"  # low, medium, high
```

### 日志配置

```python
config["logging"] = {
    "enabled": True,                    # 启用日志系统
    "level": "INFO",                    # 全局日志级别
    "data_api_level": "DEBUG",          # 数据获取层日志级别
    "format": "detailed",               # 日志格式: simple/detailed/json
    "console": True,                    # 控制台输出
    "file": "./logs/tradingagents.log", # 日志文件路径
}
```

**日志级别**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

### 数据供应商路由

项目支持多个数据供应商（yfinance、alpha_vantage、sina_finance）：

```python
from tradingagents.dataflows.interface import route_to_vendor

# 使用默认供应商
result = route_to_vendor("get_stock_data", "AAPL", "2024-01-01", "2024-01-31")

# 配置类别级供应商（影响整个工具类别）
config["data_vendors"] = {
    "core_stock_apis": "sina_finance",     # 优先使用新浪财经（避开 yfinance 限流）
    "technical_indicators": "yfinance",
    "fundamental_data": "sina_finance",
    "news_data": "yfinance",
}

# 配置工具级供应商（覆盖类别配置）
config["tool_vendors"] = {
    "get_stock_data": "alpha_vantage",  # 覆盖 core_stock_apis 默认值
}
```

**优先级**: 工具级配置 > 类别级配置 > 默认值

## LLM 客户端

### 支持的提供商

```python
config["llm_provider"] = "openai"       # OpenAI (GPT)
config["llm_provider"] = "google"       # Google (Gemini)
config["llm_provider"] = "anthropic"    # Anthropic (Claude)
config["llm_provider"] = "xai"          # xAI (Grok)
config["llm_provider"] = "openrouter"   # OpenRouter
config["llm_provider"] = "ollama"       # 本地模型
```

### 创建 LLM 客户端

```python
from tradingagents.llm_clients import create_llm_client

llm = create_llm_client(config)
```

## LangGraph 开发

### 代理节点模式

所有代理节点遵循此模式：

```python
def agent_node(state) -> dict:
    """代理节点函数。"""
    ticker = state["company_of_interest"]
    current_date = state["trade_date"]

    # 处理逻辑...

    return {"field_name": result}  # 仅返回更新的 state 字段
```

### LangGraph 状态管理

状态定义在 `tradingagents/agents/utils/agent_states.py`：

```python
from typing import TypedDict

class AgentState(TypedDict):
    company_of_interest: str
    trade_date: str
    messages: List[Any]
```

## 项目结构

```
TradingAgents/
├── cli/                      # CLI 应用
├── scripts/                  # 安装脚本
├── tradingagents/
│   ├── agents/               # 代理实现
│   │   ├── analysts/         # 分析师
│   │   ├── researchers/      # 研究员
│   │   ├── risk_mgmt/        # 风险管理
│   │   ├── managers/         # 管理器
│   │   ├── trader/           # 交易员
│   │   └── utils/            # 工具和状态
│   ├── dataflows/            # 数据获取层
│   │   └── data_cache/       # 数据缓存目录
│   ├── graph/                # LangGraph 图构建
│   ├── llm_clients/          # LLM 客户端
│   └── default_config.py     # 默认配置
├── logs/                     # 日志文件目录
├── results/                  # 结果输出目录
├── main.py                   # 示例脚本
├── test.py                   # 测试脚本
├── pyproject.toml            # 项目配置
└── requirements.txt          # 依赖列表
```

## 环境变量

在 `.env` 文件中配置 API 密钥：

```bash
# LLM 提供商（选择你要使用的）
OPENAI_API_KEY=              # OpenAI (GPT)
GOOGLE_API_KEY=              # Google (Gemini)
ANTHROPIC_API_KEY=           # Anthropic (Claude)
XAI_API_KEY=                 # xAI (Grok)
OPENROUTER_API_KEY=          # OpenRouter

# 数据源（可选，yfinance 为默认）
ALPHA_VANTAGE_API_KEY=       # Alpha Vantage

# 自定义路径（可选）
TRADINGAGENTS_RESULTS_DIR=./results
```

## 重要约束

1. **⚠️ 强制环境隔离**: 所有开发和测试必须在 conda 虚拟环境中进行
   - 每次运行前执行: `conda activate tradingagents`
   - 验证环境: `which python` 应显示 conda 环境路径
2. **配置复制**: 始终使用 `DEFAULT_CONFIG.copy()`
3. **节点返回格式**: 代理节点必须返回字典，仅包含更新的 state 字段
4. **类型提示**: 公共函数必须有完整类型提示
5. **工厂函数**: 创建代理使用 `create_*` 工厂函数
6. **LLM 客户端**: 通过 `create_llm_client()` 工厂创建
7. **Python 版本**: 最低支持 Python 3.10

## 故障排查

### 常见问题

1. **API 限流 (429 错误)**
   - 增大 `max_llm_retries` 值（默认为 3）
   - 降低并发请求数
   - 切换到不同的数据供应商（如从 yfinance 切换到 sina_finance）

2. **导入错误**
   - 确保已激活 conda 环境：`conda activate tradingagents`
   - 重新安装依赖：`pip install -r requirements.txt`
   - 验证 Python 版本：`python --version`（需要 >= 3.10）

3. **数据获取失败**
   - 检查网络连接
   - 验证 API 密钥有效性
   - 查看日志文件：`./logs/tradingagents.log`
   - 尝试切换数据供应商

4. **环境变量未生效**
   - 确保已创建 `.env` 文件：`cp .env.example .env`
   - 重启终端或重新激活 conda 环境
   - 在代码中使用 `os.getenv()` 验证变量是否加载

### 调试模式

```python
ta = TradingAgentsGraph(debug=True, config=config)
```

启用后将输出详细的执行日志，包括每个代理的输入输出。

### 查看日志

```bash
# 查看最近的日志
tail -f ./logs/tradingagents.log

# 搜索错误
grep "ERROR" ./logs/tradingagents.log
```

## 添加新代理模板

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

def create_your_analyst(llm):
    """创建新的分析师代理。"""
    def your_analyst_node(state):
        ticker = state["company_of_interest"]
        current_date = state["trade_date"]

        tools = [...]  # 添加工具

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are... {system_message}"),
            MessagesPlaceholder(variable_name="messages"),
        ])

        chain = prompt | llm.bind_tools(tools)
        response = chain.invoke({"messages": state["messages"]})

        return {"your_field": response.content}

    return your_analyst_node
```
