# sh600900新闻获取失败问题诊断与修复

## 📋 问题描述

**症状**: 获取股票代码 `sh600900` 的新闻时失败，报错：
```
KeyError: 'code'
```

## 🔍 根本原因

### 问题定位

**akshare的`stock_news_em`函数对股票代码格式有严格要求**：

```python
# ✅ 正确格式 - 纯数字
ak.stock_news_em(symbol="600900")  # 成功

# ❌ 错误格式 - 带前缀
ak.stock_news_em(symbol="sh600900")  # KeyError: 'code'

# ❌ 错误格式 - 带后缀
ak.stock_news_em(symbol="600900.SS")  # 可能失败
```

### 代码分析

在 `tradingagents/dataflows/akshare_news.py` 中：

```python
def get_akshare_stock_news(symbol: Annotated[str, "A股代码，如 600519"]):
    try:
        logger.info(f"[AKSHARE] 获取股票 {symbol} 新闻")
        
        # 直接使用symbol调用akshare API
        df = ak.stock_news_em(symbol=symbol)  # ⚠️ 问题所在
```

而在 `interface.py` 中，ticker可能带有各种格式：

```python
"get_news": {
    "akshare": lambda ticker, start, end: get_akshare_stock_news(symbol=ticker, limit=20),
    # ticker可能是: "sh600900", "600900", "600900.SS" 等
},
```

### 错误日志

```
[2026-03-16 20:34:11] [ERROR] [tradingagents.dataflows.akshare_news] [AKSHARE_ERROR] 获取新闻失败: 'code'
```

## ✅ 解决方案

### 修复代码

在 `get_akshare_stock_news` 函数中添加股票代码格式转换：

```python
def get_akshare_stock_news(symbol: Annotated[str, "A股代码，如 600519"], ...):
    try:
        logger.info(f"[AKSHARE] 获取股票 {symbol} 新闻")

        # 转换股票代码格式为akshare期望的格式（纯数字）
        cleaned_symbol = symbol
        if isinstance(symbol, str):
            cleaned_symbol = symbol.upper()
            # 移除上海/深圳前缀
            if cleaned_symbol.startswith(('SH', 'SZ')):
                cleaned_symbol = cleaned_symbol[2:]
            # 移除交易所后缀
            cleaned_symbol = cleaned_symbol.replace('.SS', '').replace('.SZ', '')

        logger.info(f"[AKSHARE] 代码转换: {symbol} -> {cleaned_symbol}")

        # 使用转换后的代码
        df = ak.stock_news_em(symbol=cleaned_symbol)
```

### 转换逻辑

| 输入格式 | 转换后 | 说明 |
|---------|--------|------|
| `sh600900` | `600900` | 移除sh前缀 |
| `SH600900` | `600900` | 移除SH前缀 |
| `sz000001` | `000001` | 移除sz前缀 |
| `SZ000001` | `000001` | 移除SZ前缀 |
| `600900.SS` | `600900` | 移除.SS后缀 |
| `000001.SZ` | `000001` | 移除.SZ后缀 |
| `600900` | `600900` | 保持不变 |

## ✅ 验证测试

### 测试结果

所有格式的股票代码现在都能成功获取新闻：

```python
✅ sh600900  -> 成功（之前失败）
✅ 600900    -> 成功
✅ 600900.SS -> 成功
```

### 测试代码

```bash
python3 << 'EOF'
from tradingagents.dataflows.akshare_news import get_akshare_stock_news

# 测试各种格式
for symbol in ["sh600900", "600900", "600900.SS"]:
    result = get_akshare_stock_news(symbol=symbol, limit=3)
    print(f"{symbol}: {'成功' if '获取新闻失败' not in result else '失败'}")
