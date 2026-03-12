<p align="center">
  <img src="assets/TauricResearch.png" style="width: 60%; height: auto;">
</p>

<div align="center" style="line-height: 1;">
  <a href="https://arxiv.org/abs/2412.20138" target="_blank"><img alt="arXiv" src="https://img.shields.io/badge/arXiv-2412.20138-B31B1B?logo=arxiv"/></a>
  <a href="https://discord.com/invite/hk9PGKShPK" target="_blank"><img alt="Discord" src="https://img.shields.io/badge/Discord-TradingResearch-7289da?logo=discord&logoColor=white&color=7289da"/></a>
  <a href="./assets/wechat.png" target="_blank"><img alt="WeChat" src="https://img.shields.io/badge/WeChat-TauricResearch-brightgreen?logo=wechat&logoColor=white"/></a>
  <a href="https://x.com/TauricResearch" target="_blank"><img alt="X Follow" src="https://img.shields.io/badge/X-TauricResearch-white?logo=x&logoColor=white"/></a>
  <br>
  <a href="https://github.com/TauricResearch/" target="_blank"><img alt="Community" src="https://img.shields.io/badge/Join_GitHub_Community-TauricResearch-14C290?logo=discourse"/></a>
</div>

<div align="center">
  <a href="README.md">English</a> | <strong>简体中文</a>
</div>

---

# TradingAgents: 多代理 LLM 金融交易框架

## 最新动态
- [2026-02] **TradingAgents v0.2.0** 发布，支持多 LLM 提供商（GPT-5.x、Gemini 3.x、Claude 4.x、Grok 4.x）并改进系统架构。
- [2026-01] **Trading-R1** [技术报告](https://arxiv.org/abs/2509.11420) 发布，[终端](https://github.com/TauricResearch/Trading-R1) 即将推出。

<div align="center">
<a href="https://www.star-history.com/#TauricResearch/TradingAgents&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=TauricResearch/TradingAgents&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=TauricResearch/TradingAgents&type=Date" />
   <img alt="TradingAgents Star History" src="https://api.star-history.com/svg?repos=TauricResearch/TradingAgents&type=Date" style="width: 80%; height: auto;" />
 </picture>
</a>
</div>

> 🎉 **TradingAgents** 正式发布！我们收到了大量关于这项工作的咨询，在此感谢社区的广泛关注。
>
> 因此我们决定完全开源该框架。期待与您共同构建有影响力的项目！

<div align="center">

🚀 [框架介绍](#tradingagents-框架) | ⚡ [安装与 CLI](#安装与-cli) | 🎬 [演示](https://www.youtube.com/watch?v=90gr5lwjIho) | 📦 [Python 包使用](#python-包使用) | 🤝 [贡献](#贡献) | 📄 [引用](#引用)

</div>

## TradingAgents 框架

TradingAgents 是一个多代理交易框架，模拟真实交易公司的运作模式。通过部署专业化的 LLM 驱动代理——从基本面分析师、情绪专家和技术分析师，到交易员、风险管理团队，平台协作评估市场状况并提供交易决策。此外，这些代理通过动态讨论来制定最优策略。

<p align="center">
  <img src="assets/schema.png" style="width: 100%; height: auto;">
</p>

> TradingAgents 框架专用于研究目的。交易表现可能因多种因素而异，包括所选骨干语言模型、模型温度、交易周期、数据质量和其他非确定性因素。[本框架不构成财务、投资或交易建议。](https://tauric.ai/disclaimer/)

我们的框架将复杂的交易任务分解为专业化角色。这确保系统能够实现稳健、可扩展的市场分析和决策方法。

### 分析师团队
- **基本面分析师**：评估公司财务和绩效指标，识别内在价值和潜在风险信号。
- **情绪分析师**：使用情绪评分算法分析社交媒体和公众情绪，以衡量短期市场情绪。
- **新闻分析师**：监控全球新闻和宏观经济指标，解读事件对市场状况的影响。
- **技术分析师**：利用技术指标（如 MACD 和 RSI）检测交易模式并预测价格走势。

<p align="center">
  <img src="assets/analyst.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

### 研究员团队
- 包括看涨和看跌研究员，他们批判性评估分析师团队提供的见解。通过结构化辩论，他们平衡潜在收益与内在风险。

<p align="center">
  <img src="assets/researcher.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

### 交易员代理
- 综合分析师和研究员的报告，做出明智的交易决策。它根据全面的市场洞察确定交易时机和规模。

<p align="center">
  <img src="assets/trader.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

### 风险管理和投资组合经理
- 通过评估市场波动性、流动性和其他风险因素，持续评估投资组合风险。风险管理团队评估并调整交易策略，向投资组合经理提供评估报告以供最终决策。
- 投资组合经理批准/拒绝交易提案。如果获得批准，订单将发送到模拟交易所并执行。

<p align="center">
  <img src="assets/risk.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

## 安装与 CLI

### 安装

克隆 TradingAgents：
```bash
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents
```

⚠️ **推荐使用 conda 环境隔离**：
```bash
# 方法 1: 使用自动化脚本（推荐）
bash scripts/setup_conda_env.sh
conda activate tradingagents

# 方法 2: 手动创建环境
conda create -n tradingagents python=3.10 -y
conda activate tradingagents
pip install -r requirements.txt
```

**每次运行前确保激活环境**: `conda activate tradingagents`

### 必需的 API

TradingAgents 支持多个 LLM 提供商。为您选择的提供商设置 API 密钥：

```bash
export OPENAI_API_KEY=...          # OpenAI (GPT)
export GOOGLE_API_KEY=...          # Google (Gemini)
export ANTHROPIC_API_KEY=...       # Anthropic (Claude)
export XAI_API_KEY=...             # xAI (Grok)
export OPENROUTER_API_KEY=...      # OpenRouter
export ZHIPU_API_KEY=...          # 智谱 AI (GLM 4.7)
export ALPHA_VANTAGE_API_KEY=...   # Alpha Vantage
```

对于本地模型，在配置中设置 `llm_provider: "ollama"`。

或者，复制 `.env.example` 到 `.env` 并填写您的密钥：
```bash
cp .env.example .env
# 编辑 .env 文件，添加您的 API 密钥
```

### CLI 使用

您也可以直接运行 CLI：
```bash
# 确保在 conda 环境中
conda activate tradingagents

# 运行 CLI
python -m cli.main
```

您将看到一个界面，可以在其中选择所需的各种股票代码、日期、LLM、研究深度等。

<p align="center">
  <img src="assets/cli/cli_init.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

将出现一个界面，显示加载时的结果，让您跟踪代理的运行进度。

<p align="center">
  <img src="assets/cli/cli_news.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

<p align="center">
  <img src="assets/cli/cli_transaction.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

## Python 包使用

### 实现细节

我们使用 LangGraph 构建 TradingAgents，以确保灵活性和模块化。该框架支持多个 LLM 提供商：OpenAI、Google、Anthropic、xAI、OpenRouter 和 Ollama。

### Python 用法

要在代码中使用 TradingAgents，您可以导入 `tradingagents` 模块并初始化 `TradingAgentsGraph()` 对象。`.propagate()` 函数将返回决策。您可以运行 `main.py`，这里还有一个快速示例：

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())

# 前向传播
_, decision = ta.propagate("NVDA", "2026-01-15")
print(decision)
```

您还可以调整默认配置以设置自己的 LLM 选择、辩论轮数等。

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openai"        # openai, google, anthropic, xai, openrouter, ollama
config["deep_think_llm"] = "gpt-5.2"     # 用于复杂推理的模型
config["quick_think_llm"] = "gpt-5-mini" # 用于快速任务的模型
config["max_debate_rounds"] = 2

ta = TradingAgentsGraph(debug=True, config=config)
_, decision = ta.propagate("NVDA", "2026-01-15")
print(decision)
```

有关所有配置选项，请参阅 `tradingagents/default_config.py`。

## 配置选项

### LLM 配置

```python
config = {
    # LLM 提供商选择
    "llm_provider": "openai",  # 可选: openai, google, anthropic, xai, openrouter, ollama, zhipu

    # 模型选择
    "deep_think_llm": "gpt-5.2",      # 用于复杂推理的主模型
    "quick_think_llm": "gpt-5-mini",  # 用于快速任务的轻量模型

    # 推理配置（可选）
    "google_thinking_level": None,      # Google Gemini: "high", "minimal" 等
    "openai_reasoning_effort": None,    # OpenAI: "medium", "high", "low"

    # API 调用配置
    "max_llm_retries": 3,               # API 调用失败时的自动重试次数（默认 3）
                                         # 用于处理 429 限流错误和网络错误
}
```

**💡 新增：支持智谱 AI GLM 4.7！**

```python
config = {
    "llm_provider": "zhipu",
    "deep_think_llm": "glm-4.7-plus",   # GLM 4.7 Plus（最强）
    "quick_think_llm": "glm-4.7-flash", # GLM 4.7 Flash（最快）
}
```

**优势**：中文能力强、成本更低、速度快。详见 [GLM_4.7_使用指南.md](GLM_4.7_使用指南.md)

### 讨论配置

```python
config = {
    # 辩论轮数
    "max_debate_rounds": 1,        # 研究员辩论轮数
    "max_risk_discuss_rounds": 1,  # 风险管理讨论轮数
    "max_recur_limit": 100,        # 最大递归限制
}
```

### 数据供应商配置

```python
config = {
    # 数据供应商选择
    "data_vendors": {
        "core_stock_apis": "yfinance",       # 可选: alpha_vantage, yfinance
        "technical_indicators": "yfinance",
        "fundamental_data": "yfinance",
        "news_data": "yfinance",
    },

    # 工具级配置（优先级高于类别级）
    "tool_vendors": {
        # "get_stock_data": "alpha_vantage",  # 示例：覆盖类别默认值
    },
}
```

### 运行示例

**简单运行**：
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())
_, decision = ta.propagate("AAPL", "2026-01-15")
print(decision)
```

**自定义配置**：
```python
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "google"
config["deep_think_llm"] = "gemini-2.5-pro"
config["max_debate_rounds"] = 3

ta = TradingAgentsGraph(debug=True, config=config)
_, decision = ta.propagate("TSLA", "2026-01-15")
print(decision)
```

## 项目结构

```
TradingAgents/
├── cli/                      # CLI 应用
├── scripts/                  # 安装脚本
├── tradingagents/
│   ├── agents/               # 代理实现
│   │   ├── analysts/         # 分析师代理
│   │   ├── researchers/      # 研究员代理
│   │   ├── risk_mgmt/        # 风险管理代理
│   │   └── utils/            # 工具和状态
│   ├── dataflows/            # 数据获取层
│   ├── graph/                # LangGraph 图构建
│   ├── llm_clients/          # LLM 客户端
│   └── default_config.py     # 默认配置
├── main.py                   # 示例使用脚本
├── test.py                   # 测试脚本
├── pyproject.toml            # 项目配置
└── requirements.txt          # 依赖列表
```

## 常见问题

### 1. 如何选择 LLM 提供商？

根据您的需求和 API 密钥选择：

- **OpenAI (GPT)**: 最强大，需要 `OPENAI_API_KEY`
- **Google (Gemini)**: 性价比高，需要 `GOOGLE_API_KEY`
- **Anthropic (Claude)**: 安全可靠，需要 `ANTHROPIC_API_KEY`
- **xAI (Grok)**: 实时数据，需要 `XAI_API_KEY`
- **OpenRouter**: 多模型聚合，需要 `OPENROUTER_API_KEY`
- **Ollama**: 本地运行，无需 API 密钥

### 2. 如何调整代理数量？

在配置中设置 `selected_analysts`：

```python
config = DEFAULT_CONFIG.copy()
config["selected_analysts"] = ["market", "fundamentals", "news"]  # 只使用这三个
```

### 3. 如何提高分析质量？

- 增加 `max_debate_rounds` 以进行更深入讨论
- 使用更强大的 `deep_think_llm` 模型
- 确保使用高质量数据供应商

### 4. 是否需要 API 密钥？

- **必需**: 至少需要一个 LLM 提供商的 API 密钥（OpenAI、Google、Anthropic、xAI 或 OpenRouter）
- **可选**: Alpha Vantage API 密钥（默认使用免费的 yfinance）

### 5. 如何在本地运行？

使用 Ollama：

```python
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "ollama"
config["deep_think_llm"] = "llama3.2"
config["backend_url"] = "http://localhost:11434/v1"
```

## 开发指南

### 运行测试

**⚠️ 必须在 conda 虚拟环境中运行**：

```bash
# 激活环境
conda activate tradingagents

# 运行测试
python test.py
```

### 代码质量检查

```bash
# 在 conda 环境中
conda activate tradingagents

# 安装工具
pip install mypy black ruff

# 运行检查
mypy tradingagents/       # 类型检查
black tradingagents/ cli/ # 格式化
ruff check tradingagents/ cli/  # lint
```

### 添加新代理

参考 `AGENTS.md` 中的模板。基本步骤：

1. 在 `tradingagents/agents/` 下创建新模块
2. 使用工厂模式 `create_your_analyst(llm)`
3. 返回节点函数供 LangGraph 使用
4. 在 `TradingAgentsGraph` 中注册

## 贡献

我们欢迎社区贡献！无论是修复错误、改进文档还是建议新功能，您的输入都会让这个项目变得更好。如果您对这条研究路线感兴趣，请考虑加入我们的开源金融 AI 研究社区 [Tauric Research](https://tauric.ai/)。

## 引用

如果 *TradingAgents* 对您有所帮助，请引用我们的工作 :)

```
@misc{xiao2025tradingagentsmultiagentsllmfinancial,
      title={TradingAgents: Multi-Agents LLM Financial Trading Framework},
      author={Yijia Xiao and Edward Sun and Di Luo and Wei Wang},
      year={2025},
      eprint={2412.20138},
      archivePrefix={arXiv},
      primaryClass={q-fin.TR},
      url={https://arxiv.org/abs/2412.20138},
}
```

## 许可证

本项目采用 Apache 2.0 许可证。详见 [LICENSE](LICENSE) 文件。

## 免责声明

TradingAgents 框架专用于研究目的。交易表现可能因多种因素而异，包括所选骨干语言模型、模型温度、交易周期、数据质量和其他非确定性因素。本框架不构成财务、投资或交易建议。使用本框架产生的任何交易决策的风险由用户自行承担。

---

## 相关资源

- 📄 [论文](https://arxiv.org/abs/2412.20138)
- 🎬 [视频演示](https://www.youtube.com/watch?v=90gr5lwjIho)
- 💬 [Discord 社区](https://discord.com/invite/hk9PGKShPK)
- 🌐 [Tauric Research](https://tauric.ai/)
- 📧 [联系我们](mailto:info@tauric.ai)
