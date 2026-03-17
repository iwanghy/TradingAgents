# 日志系统升级说明

## 📋 升级概述

本次升级实现了日志输出的分离，使终端显示更加简洁清爽，同时在日志文件中保留详细的调试信息。

## ✨ 升级内容

### 修改的文件

1. **`tradingagents/dataflows/logging_config.py`**
   - 根logger级别改为 `DEBUG`（允许所有消息通过）
   - Console handler级别改为 `INFO`（终端只显示重要信息）
   - File handler级别改为 `DEBUG`（文件记录详细调试信息）

2. **`tradingagents/default_config.py`**
   - 启用日志文件输出：`"file": "./logs/tradingagents.log"`

## 📊 效果对比

### 修改前（所有日志都输出到终端）

```
[终端输出 - 杂乱且信息量大]
[2026-03-11 15:30:00] [DEBUG   ] [tradingagents.dataflows.interface] ROUTE_DECISION: get_stock_data -> yfinance
[2026-03-11 15:30:00] [DEBUG   ] [tradingagents.dataflows.interface] ROUTE_ATTEMPT: Trying vendor 'yfinance'
[2026-03-11 15:30:00] [DEBUG   ] [tradingagents.dataflows.y_finance] YFINANCE: Created Ticker object for AAPL
[2026-03-11 15:30:00] [DEBUG   ] [tradingagents.dataflows.y_finance] API_CALL: yfinance | symbol=AAPL | start=2024-01-01
[2026-03-11 15:30:01] [INFO    ] [tradingagents.dataflows.interface] ROUTE_SUCCESS: get_stock_data via yfinance
[2026-03-11 15:30:01] [INFO    ] [tradingagents.dataflows.y_finance] API_SUCCESS: yfinance | AAPL | records: 252
...
```

**问题**:
- ❌ 终端输出过于冗长，难以快速找到关键信息
- ❌ 调试信息与重要信息混在一起
- ❌ 没有持久化的日志记录

### 修改后（终端简洁，文件详细）

#### 终端输出（清爽简洁）

```
[2026-03-11 15:30:00] [INFO    ] [tradingagents.dataflows.interface] ROUTE_SUCCESS: get_stock_data via yfinance
[2026-03-11 15:30:01] [INFO    ] [tradingagents.dataflows.y_finance] API_SUCCESS: yfinance | AAPL | records: 252
[2026-03-11 15:30:02] [WARNING ] [tradingagents.dataflows.interface] RATE_LIMIT: Approaching API limit
```

**优势**:
- ✅ 只显示重要信息（INFO、WARNING、ERROR）
- ✅ 快速了解处理阶段和结果
- ✅ AI响应信息通过 LangGraph debug 模式保留

#### 日志文件（完整调试信息）

`./logs/tradingagents.log`:

```
[2026-03-11 15:30:00] [DEBUG   ] [tradingagents.dataflows.interface] ROUTE_DECISION: get_stock_data -> yfinance
[2026-03-11 15:30:00] [DEBUG   ] [tradingagents.dataflows.interface] ROUTE_ATTEMPT: Trying vendor 'yfinance'
[2026-03-11 15:30:00] [DEBUG   ] [tradingagents.dataflows.y_finance] YFINANCE: Created Ticker object for AAPL
[2026-03-11 15:30:00] [DEBUG   ] [tradingagents.dataflows.y_finance] API_CALL: yfinance | symbol=AAPL | start=2024-01-01
[2026-03-11 15:30:01] [INFO    ] [tradingagents.dataflows.interface] ROUTE_SUCCESS: get_stock_data via yfinance
[2026-03-11 15:30:01] [INFO    ] [tradingagents.dataflows.y_finance] API_SUCCESS: yfinance | AAPL | records: 252
```

**优势**:
- ✅ 记录所有DEBUG级别的详细调试信息
- ✅ 包含API调用参数、路由决策等
- ✅ 文件轮转管理（10MB/文件，保留5个备份）
- ✅ 持久化存储，方便事后分析

## 🎯 适用场景

### 终端输出（INFO级别）
适合以下信息：
- ✅ 处理阶段开始/完成
- ✅ 操作成功/失败
- ✅ 警告和错误信息
- ✅ AI响应（通过 LangGraph debug 模式）

### 日志文件（DEBUG级别）
适合以下信息：
- ✅ API调用详细参数
- ✅ 路由决策过程
- ✅ 数据获取细节
- ✅ 性能指标（耗时等）
- ✅ 调试所需的上下文信息

## 🔧 技术原理

Python logging 的两级过滤机制：

```
日志消息 (DEBUG级别)
    ↓
[根 logger 级别过滤] ← 第一道关卡（设置为DEBUG，全部通过）
    ↓
[Handler 级别过滤] ← 第二道关卡（各自独立设置）
    ├─ Console Handler (INFO) → 过滤掉DEBUG
    └─ File Handler (DEBUG) → 记录所有消息
```

## 📝 使用示例

### 查看实时日志
```bash
# 终端运行（只看重要信息）
conda activate tradingagents
python test_glm.py

# 同时查看详细日志（另开终端）
tail -f ./logs/tradingagents.log
```

### 搜索日志
```bash
# 查看特定股票的日志
grep "sh600519" ./logs/tradingagents.log

# 查看所有API调用
grep "\[API_CALL\]" ./logs/tradingagents.log

# 查看错误信息
grep "\[ERROR\]" ./logs/tradingagents.log
```

## ⚙️ 配置调整

如果需要调整日志级别，可以修改 `default_config.py`:

```python
"logging": {
    "level": "INFO",                    # 默认级别
    "console": True,                    # 终端输出
    "file": "./logs/tradingagents.log", # 日志文件
}
```

或者在使用时自定义：
```python
from tradingagents.dataflows.logging_config import setup_logging

# 终端显示WARNING，文件记录DEBUG
setup_logging(
    level="WARNING",
    log_file="./logs/custom.log"
)
```

## ✅ 验证测试

运行测试脚本验证功能：
```bash
conda activate tradingagents
python test_log_separation.py
```

预期输出：
- ✅ 终端只显示 INFO、WARNING、ERROR
- ✅ 日志文件包含 DEBUG、INFO、WARNING、ERROR

## 🎉 总结

本次升级实现了：
1. ✅ 终端输出更加简洁清爽
2. ✅ 调试信息持久化到文件
3. ✅ 便于问题排查和性能分析
4. ✅ 保持向后兼容
5. ✅ 自动文件轮转，避免日志文件过大

**现在你可以享受更清爽的终端输出，同时在需要时查看详细的调试日志！**
