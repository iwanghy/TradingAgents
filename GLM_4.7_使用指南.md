# GLM 4.7 使用指南

## 概述

TradingAgents 现已完全支持智谱 AI 的 GLM 4.7 系列模型！GLM 4.7 是智谱 AI 最新发布的强大语言模型，通过 OpenAI 兼容 API 接口提供服务。

## 支持的 GLM 模型

### GLM-4.7 系列（最新，推荐）
- `glm-4.7-plus` - 最强大的版本，适合复杂推理
- `glm-4.7` - 标准版本，性能与速度平衡
- `glm-4.7-flash` - 快速版本，适合快速任务
- `glm-4.7-air` - 轻量版本，成本更低

### GLM-4 系列（稳定版）
- `glm-4-plus` - GLM-4 最强版本
- `glm-4-0520` - 2024年5月版本
- `glm-4-air` - 轻量快速版本
- `glm-4-flash` - 超快响应版本
- `glm-4-long` - 长文本版本

## 快速开始

### 方式一：使用 .env 文件（推荐）

#### 1. 获取 API 密钥

访问智谱 AI 开放平台：https://open.bigmodel.cn/
- 注册账号
- 在控制台获取 API Key
- 充值（新用户通常有免费额度）

#### 2. 配置环境变量

在项目根目录创建或编辑 `.env` 文件：

```bash
# 智谱 AI GLM
ZHIPU_API_KEY=your-zhipu-api-key-here
```

#### 3. 运行分析

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv

load_dotenv()

# 配置使用 GLM 4.7
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "zhipu"
config["deep_think_llm"] = "glm-4.7-plus"    # 主模型
config["quick_think_llm"] = "glm-4.7-flash"  # 快速模型
config["max_debate_rounds"] = 2

# 运行分析
ta = TradingAgentsGraph(debug=True, config=config)
state, decision = ta.propagate("AAPL", "2024-01-15")
print(decision)
```

### 方式二：使用自定义 base_url

如果你想使用其他兼容 OpenAI API 的端点：

```python
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openai"
config["deep_think_llm"] = "glm-4.7-plus"
config["backend_url"] = "https://open.bigmodel.cn/api/paas/v4/"

# 在 kwargs 中传入 API key
ta = TradingAgentsGraph(
    debug=True,
    config=config,
    api_key="your-zhipu-api-key"
)
```

## 完整示例

### 示例 1：使用 GLM 4.7 Plus 进行深度分析

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv

load_dotenv()

# 使用 GLM 4.7 Plus 进行深度分析
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "zhipu"
config["deep_think_llm"] = "glm-4.7-plus"
config["quick_think_llm"] = "glm-4.7-flash"
config["max_debate_rounds"] = 3  # 3轮深度辩论
config["max_risk_discuss_rounds"] = 2

ta = TradingAgentsGraph(debug=True, config=config)
state, decision = ta.propagate("NVDA", "2024-01-15")

print("="*60)
print("GLM 4.7 Plus 深度分析结果")
print("="*60)
print(f"股票: NVDA")
print(f"日期: 2024-01-15")
print(f"决策: {decision}")
print("="*60)
```

### 示例 2：使用 GLM 4.7 Flash 进行快速分析

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv

load_dotenv()

# 使用 GLM 4.7 Flash 进行快速分析
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "zhipu"
config["deep_think_llm"] = "glm-4.7"
config["quick_think_llm"] = "glm-4.7-flash"
config["max_debate_rounds"] = 1  # 1轮快速分析

ta = TradingAgentsGraph(debug=True, config=config)
state, decision = ta.propagate("TSLA", "2024-01-15")

print(f"快速分析结果: {decision}")
```

### 示例 3：使用 GLM-4 Air 进行经济分析

```python
# 使用 GLM-4 Air（成本更低）
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "zhipu"
config["deep_think_llm"] = "glm-4-air"
config["quick_think_llm"] = "glm-4-flash"
config["max_debate_rounds"] = 2

ta = TradingAgentsGraph(debug=True, config=config)
state, decision = ta.propagate("AAPL", "2024-01-15")
```

## CLI 使用

### 命令行使用 GLM 4.7

```bash
# 1. 确保环境已激活
conda activate tradingagents

# 2. 配置 .env 文件
echo "ZHIPU_API_KEY=your-key-here" >> .env

# 3. 启动 CLI
python -m cli.main

# 4. 在界面中选择：
#    - LLM Provider: zhipu
#    - Deep Think Model: glm-4.7-plus
#    - Quick Think Model: glm-4.7-flash
```

## 配置说明

### 推荐配置组合

#### 高性能配置（最新最强）
```python
config = {
    "llm_provider": "zhipu",
    "deep_think_llm": "glm-4.7-plus",     # 最强推理
    "quick_think_llm": "glm-4.7-flash",   # 最快响应
    "max_debate_rounds": 3,
}
```

#### 均衡配置（性能与成本平衡）
```python
config = {
    "llm_provider": "zhipu",
    "deep_think_llm": "glm-4.7",          # 标准版本
    "quick_think_llm": "glm-4.7-flash",
    "max_debate_rounds": 2,
}
```

#### 经济配置（成本最优）
```python
config = {
    "llm_provider": "zhipu",
    "deep_think_llm": "glm-4-air",        # 成本低
    "quick_think_llm": "glm-4-flash",
    "max_debate_rounds": 1,
}
```

## GLM 4.7 特性

### 主要优势

1. **中文能力强**：专为中文优化，理解中国市场
2. **推理能力强**：4.7 Plus 版本在复杂推理任务上表现优异
3. **速度更快**：Flash 版本响应速度极快
4. **成本更低**：相比国外 LLM，成本大幅降低
5. **本土化优势**：理解中文财经术语和A股市场特点

### 适用场景

- **A股分析**：GLM 在中文财经内容理解上更有优势
- **港股分析**：理解中资股的业务逻辑
- **美股中概股**：理解中概股的特殊性
- **成本敏感场景**：GLM 价格更实惠

## API 费用参考

### GLM 4.7 定价（仅供参考）

| 模型 | 输入 (元/百万tokens) | 输出 (元/百万tokens) |
|------|---------------------|---------------------|
| glm-4.7-plus | ~0.5 | ~0.5 |
| glm-4.7 | ~0.1 | ~0.1 |
| glm-4.7-flash | ~0.05 | ~0.05 |
| glm-4.7-air | ~0.01 | ~0.01 |

*具体价格请参考智谱 AI 官方定价*

### 预估单次分析费用

使用 GLM 4.7-flash，2 轮辩论：
- **快速分析**（1轮）：约 ¥0.02-0.05
- **标准分析**（2轮）：约 ¥0.05-0.10
- **深度分析**（3轮）：约 ¥0.10-0.20

*比使用 GPT-4 便宜 10-20 倍！*

## 故障排查

### 问题 0: TLS/SSL 连接错误 (curl_cffi OpenSSL 不兼容)

**错误信息**：
```
curl: (35) TLS connect error: error:00000000:lib(0):func(0):reason(0)
```

**说明**：这是 conda 环境的 OpenSSL 版本与系统 curl 不兼容导致的。

**解决方法**：

在导入 yfinance 之前添加环境变量（推荐在脚本开头）：

```python
import os
os.environ['YFINANCE_NO_CURL'] = '1'  # 禁用 curl_cffi，使用 requests

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
```

或者永久设置（在 `~/.bashrc` 或 `~/.zshrc` 中）：

```bash
export YFINANCE_NO_CURL=1
```

### 问题 1: API Key 无效

**错误信息**：`Authentication failed`

**解决方法**：
```bash
# 检查 .env 文件
cat .env | grep ZHIPU

# 确保 API Key 正确
ZHIPU_API_KEY=your-actual-key-here
```

### 问题 2: 模型不存在

**错误信息**：`Model not found`

**解决方法**：
```python
# 检查模型名称是否正确
# 正确的名称：
"glm-4.7-plus"
"glm-4.7"
"glm-4.7-flash"

# 错误的示例：
"glm-4.7-plus-xxx"  # 不存在的变体
"glm-47-plus"      # 缺少点号
```

### 问题 3: 请求超时

**错误信息**：`Request timeout`

**解决方法**：
```python
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "zhipu"

# 增加超时时间
ta = TradingAgentsGraph(
    debug=True,
    config=config,
    timeout=120  # 120秒超时
)
```

### 问题 4: Too Many Requests (429 错误)

**错误信息**：`Too Many Requests. Rate limited.`

**说明**：这是 API 限流错误，通常是因为短时间内请求过于频繁。

**解决方法**：

1. **自动重试（推荐）**：
   TradingAgents 现已内置自动重试机制，默认会自动重试 3 次：

   ```python
   config = DEFAULT_CONFIG.copy()
   config["llm_provider"] = "zhipu"
   config["max_llm_retries"] = 3  # 默认值，可调整为其他次数

   ta = TradingAgentsGraph(debug=True, config=config)
   ```

2. **增加重试次数**：如果经常遇到限流，可以增加重试次数：

   ```python
   config["max_llm_retries"] = 5  # 增加到 5 次
   ```

3. **降低并发**：减少同时运行的分析任务

4. **等待一段时间**：如果重试仍然失败，请等待几分钟后重试

**技术细节**：
- 自动重试机制适用于所有 LLM 提供商（OpenAI、Google、Anthropic、xAI、Zhipu 等）
- 重试使用指数退避策略，避免加重服务器负担
- 重试次数可以在 `DEFAULT_CONFIG` 中全局配置

### 问题 5: 余额不足

**错误信息**：`Insufficient balance`

**解决方法**：
1. 访问 https://open.bigmodel.cn/
2. 进入控制台
3. 充值账户
4. 查看余额是否充足

## 与其他模型对比

### GLM 4.7 vs GPT-5

| 特性 | GLM 4.7 | GPT-5 |
|------|---------|-------|
| 中文能力 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 推理能力 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 速度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 成本 | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 英文能力 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

### 推荐场景

**使用 GLM 4.7**：
- ✅ 分析 A 股、港股、中概股
- ✅ 成本敏感的项目
- ✅ 需要快速响应
- ✅ 中文财经文本分析

**使用 GPT-5**：
- ✅ 分析美股（非中概股）
- ✅ 需要最强的推理能力
- ✅ 复杂的衍生品分析
- ✅ 英文财报分析

## 高级用法

### 自定义端点

如果你的 GLM API 部署在其他位置：

```python
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "zhipu"
config["deep_think_llm"] = "glm-4.7-plus"
config["backend_url"] = "https://your-custom-endpoint.com/v1/"
```

### 结合使用多个提供商

```python
# 主分析用 GLM（成本低）
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "zhipu"
config["deep_think_llm"] = "glm-4.7"

# 某些关键步骤用 GPT（质量高）
# 需要修改代码以支持混合使用
```

## 技术细节

### API 端点

GLM 4.7 使用标准的 OpenAI 兼容 API：

```
Base URL: https://open.bigmodel.cn/api/paas/v4/
API 版本: v1 (兼容)
认证方式: Bearer Token
```

### 支持的参数

GLM 4.7 支持以下参数（与 OpenAI 兼容）：

- `temperature` (0-1)
- `top_p` (0-1)
- `max_tokens`
- `stream`
- `stop`

### 不支持的参数

GLM 4.7 不支持以下 OpenAI 特有参数：

- `reasoning_effort` (OpenAI o1 系列)
- `parallel_tool_calls`

## 更新日志

### 2025-03-10
- ✅ 添加 GLM 4.7 系列模型支持
- ✅ 添加 `zhipu` provider
- ✅ 更新模型验证列表
- ✅ 创建使用文档

## 相关链接

- **智谱 AI 官网**：https://zhipuai.cn/
- **开放平台**：https://open.bigmodel.cn/
- **API 文档**：https://open.bigmodel.cn/dev/api
- **定价**：https://open.bigmodel.cn/pricing
- **Python SDK**：https://github.com/MGLM-Dev/GLM

## 社区支持

如果遇到问题：

1. 查看本文档的"故障排查"部分
2. 查看 AGENTS.md 了解开发细节
3. 在 GitHub 提交 Issue
4. 加入智谱 AI 开发者社区

## 免责声明

- GLM 4.7 模型由智谱 AI 提供
- TradingAgents 框架不保证分析结果的准确性
- 投资有风险，决策需谨慎
- 本文档内容仅供参考，以智谱 AI 官方文档为准
