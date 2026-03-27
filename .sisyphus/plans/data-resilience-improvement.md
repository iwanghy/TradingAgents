# 数据获取稳定性改进计划

## TL;DR

> **核心目标**: 增强数据获取层的稳定性，实现重试、超时和熔断机制
> 
> **范围**: Phase 1+2+3（重试 + 超时 + 熔断）
> 
> **关键交付物**:
> - 新建 `resilience.py` 稳定性模块
> - 修改 `interface.py` 集成重试和熔断
> - 修改供应商实现添加超时控制
> - 更新 `default_config.py` 添加配置项
> 
> **预计工作量**: 中等（3-4个文件修改，1个新文件）

---

## Context

### 原始请求
用户希望改善整个链条的稳定性，特别关注数据获取环节。

### 问题分析
当前 `tradingagents/dataflows/interface.py` 的 `route_to_vendor()` 函数存在以下问题：

1. **Fallback 触发条件过窄**
   ```python
   # 当前：只有 AlphaVantageRateLimitError 触发 fallback
   except AlphaVantageRateLimitError as e:
       continue  # Only rate limits trigger fallback
   except Exception as e:
       # 其他错误直接抛出
       raise
   ```

2. **缺乏重试机制**
   - 网络抖动、瞬时错误不会重试
   - 没有指数退避

3. **缺乏超时控制**
   - `alpha_vantage_common.py` 中的 `requests.get()` 没有 timeout
   - yfinance 调用没有超时保护

4. **缺乏熔断机制**
   - 连续失败的供应商不会被暂停
   - 可能导致雪崩效应

---

## Work Objectives

### Core Objective
为数据获取层添加弹性机制，包括重试、超时和熔断，提高系统可用性。

### Concrete Deliverables
1. **新建** `tradingagents/dataflows/resilience.py` - 稳定性增强模块
2. **修改** `tradingagents/dataflows/interface.py` - 集成重试和熔断
3. **修改** `tradingagents/dataflows/alpha_vantage_common.py` - 添加超时
4. **修改** `tradingagents/dataflows/y_finance.py` - 添加超时
5. **修改** `tradingagents/default_config.py` - 添加配置项

### Definition of Done
- [x] `route_to_vendor()` 对网络错误、超时、rate limit 都会触发 fallback
- [x] 失败的供应商会自动重试（最多3次，指数退避）
- [x] 连续失败5次的供应商会被熔断60秒
- [x] 所有 HTTP 请求都有30秒超时
- [x] 日志包含重试、熔断的详细信息

### Must Have
- 向后兼容：不改变现有 API 接口
- 可配置：重试次数、超时时间、熔断阈值可通过配置调整
- 详细日志：每次重试、熔断都有日志记录

### Must NOT Have
- 不修改供应商实现的核心逻辑
- 不添加新的外部依赖
- 不影响现有功能

---

## Verification Strategy

### 测试方法
1. **单元测试**: 测试 resilience.py 中的重试和熔断逻辑
2. **集成测试**: 模拟网络错误，验证 fallback 触发
3. **日志验证**: 检查日志输出是否包含重试、熔断信息

### QA Scenarios

**Scenario 1: 网络错误触发 fallback**
- 模拟 `requests.ConnectionError`
- 验证自动切换到下一个供应商
- 验证日志包含 `[RETRY]` 和 `[FALLBACK]` 标签

**Scenario 2: Rate limit 触发重试**
- 模拟 `AlphaVantageRateLimitError`
- 验证指数退避重试（1s, 2s, 4s）
- 验证重试3次后 fallback

**Scenario 3: 熔断机制**
- 模拟供应商连续5次失败
- 验证供应商被标记为不可用
- 验证60秒后自动恢复

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately):
├── Task 1: 创建 resilience.py 稳定性模块
└── Task 2: 修改 default_config.py 添加配置项

Wave 2 (After Wave 1):
├── Task 3: 修改 interface.py 集成重试和熔断
├── Task 4: 修改 alpha_vantage_common.py 添加超时
└── Task 5: 修改 y_finance.py 添加超时
```

### Dependency Matrix
- Task 1, 2: 无依赖，可并行
- Task 3: 依赖 Task 1, 2
- Task 4, 5: 无依赖，可并行

---

## TODOs

### Task 1: 创建 resilience.py 稳定性模块

**What to do**:
- 创建 `tradingagents/dataflows/resilience.py`
- 实现 `VendorHealth` 类（健康状态追踪 + 熔断）
- 实现 `retry_with_backoff()` 装饰器（指数退避重试）
- 实现 `is_retryable_error()` 函数（判断错误是否可重试）

**Must NOT do**:
- 不修改现有供应商实现
- 不添加新的外部依赖

**Key Implementation Details**:

```python
# resilience.py 核心代码结构

import time
import logging
import functools
import requests
from typing import Tuple, Type

logger = logging.getLogger(__name__)

# 可重试的错误类型
RETRYABLE_ERRORS: Tuple[Type[Exception], ...] = (
    requests.ConnectionError,
    requests.Timeout,
    TimeoutError,
)

def is_retryable_error(error: Exception) -> bool:
    """判断错误是否可重试"""
    # Rate limit 错误可重试
    if "RateLimitError" in type(error).__name__:
        return True
    # 网络错误可重试
    if isinstance(error, RETRYABLE_ERRORS):
        return True
    # HTTP 5xx 错误可重试
    if isinstance(error, requests.HTTPError):
        if error.response and 500 <= error.response.status_code < 600:
            return True
    return False

class VendorHealth:
    """供应商健康状态追踪和熔断"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.circuit_open = False
        self.circuit_open_until = 0.0
    
    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.circuit_open = True
            self.circuit_open_until = time.time() + self.recovery_timeout
            logger.warning(f"[CIRCUIT_OPEN] Circuit breaker opened for {self.recovery_timeout}s")
    
    def record_success(self):
        self.failure_count = 0
        if self.circuit_open:
            self.circuit_open = False
            logger.info("[CIRCUIT_CLOSED] Circuit breaker closed")
    
    def is_available(self) -> bool:
        if not self.circuit_open:
            return True
        if time.time() > self.circuit_open_until:
            self.circuit_open = False
            self.failure_count = 0
            logger.info("[CIRCUIT_CLOSED] Circuit breaker auto-closed after timeout")
            return True
        return False

# 全局供应商健康状态
_vendor_health: dict[str, VendorHealth] = {}

def get_vendor_health(vendor: str) -> VendorHealth:
    """获取供应商健康状态"""
    if vendor not in _vendor_health:
        _vendor_health[vendor] = VendorHealth()
    return _vendor_health[vendor]

def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """指数退避重试装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if not is_retryable_error(e):
                        raise
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"[RETRY] Attempt {attempt + 1}/{max_retries} failed, retrying in {delay}s: {e}")
                        time.sleep(delay)
                    else:
                        logger.error(f"[RETRY_EXHAUSTED] All {max_retries} attempts failed: {e}")
            raise last_error
        return wrapper
    return decorator
```

---

### Task 2: 修改 default_config.py 添加配置项

**What to do**:
- 在 `DEFAULT_CONFIG` 中添加 `data_resilience` 配置项
- 包含重试次数、超时时间、熔断阈值等

**配置结构**:
```python
DEFAULT_CONFIG = {
    # ... 现有配置 ...
    "data_resilience": {
        "max_retries": 3,              # 最大重试次数
        "retry_base_delay": 1.0,       # 重试基础延迟（秒）
        "timeout_seconds": 30,         # HTTP 请求超时（秒）
        "circuit_breaker_threshold": 5, # 熔断阈值（连续失败次数）
        "circuit_breaker_timeout": 60,  # 熔断恢复时间（秒）
    }
}
```

---

### Task 3: 修改 interface.py 集成重试和熔断

**What to do**:
- 导入 resilience 模块
- 修改 `route_to_vendor()` 函数：
  1. 检查供应商是否被熔断
  2. 扩展 fallback 触发条件
  3. 集成重试逻辑
  4. 记录成功/失败到健康状态

**关键修改**:
```python
from .resilience import get_vendor_health, is_retryable_error, retry_with_backoff

def route_to_vendor(method: str, *args, **kwargs):
    """Route method calls to appropriate vendor implementation with fallback support."""
    category = get_category_for_method(method)
    vendor_config = get_vendor(category, method)
    primary_vendors = [v.strip() for v in vendor_config.split(',')]
    
    logger = logging.getLogger(__name__)
    logger.info(f"[ROUTE_DECISION] {method} -> {primary_vendors} | category={category}")
    
    if method not in VENDOR_METHODS:
        raise ValueError(f"Method '{method}' not supported")
    
    # Build fallback chain
    all_available_vendors = list(VENDOR_METHODS[method].keys())
    fallback_vendors = primary_vendors.copy()
    for vendor in all_available_vendors:
        if vendor not in fallback_vendors:
            fallback_vendors.append(vendor)
    
    last_error = None
    for vendor in fallback_vendors:
        if vendor not in VENDOR_METHODS[method]:
            continue
        
        # 检查熔断
        health = get_vendor_health(vendor)
        if not health.is_available():
            logger.warning(f"[CIRCUIT_SKIP] Vendor {vendor} is circuit-broken, skipping")
            continue
        
        vendor_impl = VENDOR_METHODS[method][vendor]
        impl_func = vendor_impl[0] if isinstance(vendor_impl, list) else vendor_impl
        
        logger.info(f"[ROUTE_ATTEMPT] Trying vendor: {vendor} for {method}")
        
        try:
            # 使用重试装饰器包装调用
            @retry_with_backoff(max_retries=3, base_delay=1.0)
            def call_with_retry():
                return impl_func(*args, **kwargs)
            
            result = call_with_retry()
            health.record_success()
            logger.info(f"[ROUTE_SUCCESS] {method} via {vendor}")
            return result
        except Exception as e:
            last_error = e
            health.record_failure()
            
            # 判断是否应该 fallback
            if is_retryable_error(e):
                logger.warning(f"[FALLBACK] {vendor} failed with retryable error, trying next: {e}")
                continue
            else:
                # 不可重试的错误直接抛出
                logger.error(f"[VENDOR_ERROR] {vendor} | {method} | {type(e).__name__}: {str(e)}")
                raise
    
    raise RuntimeError(f"No available vendor for '{method}'. Last error: {last_error}")
```

---

### Task 4: 修改 alpha_vantage_common.py 添加超时

**What to do**:
- 在 `_make_api_request()` 中添加 timeout 参数
- 使用配置中的超时时间

**关键修改**:
```python
from .config import get_config

def _make_api_request(function_name: str, params: dict) -> dict | str:
    """Helper function to make API requests with timeout."""
    config = get_config()
    timeout = config.get("data_resilience", {}).get("timeout_seconds", 30)
    
    api_params = params.copy()
    api_params.update({
        "function": function_name,
        "apikey": get_api_key(),
        "source": "trading_agents",
    })
    
    # ... 现有的 entitlement 处理 ...
    
    response = requests.get(API_BASE_URL, params=api_params, timeout=timeout)
    response.raise_for_status()
    
    # ... 现有的响应处理 ...
```

---

### Task 5: 修改 y_finance.py 添加超时

**What to do**:
- 在 `get_YFin_data_online()` 等函数中添加超时保护
- 使用 signal.alarm 或 threading.Timer 实现超时

**关键修改**:
```python
import signal
from .config import get_config

def _timeout_handler(signum, frame):
    """超时处理函数"""
    raise TimeoutError("yfinance call timed out")

def get_YFin_data_online(symbol, start_date, end_date):
    """从 yfinance 获取股票历史数据，带超时保护"""
    config = get_config()
    timeout = config.get("data_resilience", {}).get("timeout_seconds", 30)
    
    # 设置超时
    old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(timeout)
    
    try:
        ticker = yf.Ticker(symbol.upper())
        data = ticker.history(start=start_date, end=end_date)
        # ... 现有处理逻辑 ...
        return data
    except TimeoutError:
        logger.error(f"[TIMEOUT] yfinance call timed out after {timeout}s for {symbol}")
        raise
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)
```

**注意**: signal.SIGALRM 在 Windows 上不可用，需要条件判断：
```python
import platform

if platform.system() != 'Windows':
    # Unix/Linux/macOS 使用 signal
    signal.alarm(timeout)
else:
    # Windows 使用 threading.Timer（需要重构为多线程）
    pass
```

---

## Commit Strategy

- **Commit 1**: `feat(dataflows): 添加稳定性增强模块 resilience.py`
  - 文件: `tradingagents/dataflows/resilience.py`
  
- **Commit 2**: `feat(config): 添加数据弹性配置项`
  - 文件: `tradingagents/default_config.py`
  
- **Commit 3**: `feat(dataflows): 集成重试和熔断到 interface.py`
  - 文件: `tradingagents/dataflows/interface.py`
  
- **Commit 4**: `feat(dataflows): 为 Alpha Vantage 添加超时控制`
  - 文件: `tradingagents/dataflows/alpha_vantage_common.py`
  
- **Commit 5**: `feat(dataflows): 为 yfinance 添加超时控制`
  - 文件: `tradingagents/dataflows/y_finance.py`

---

## Success Criteria

### Verification Commands
```bash
# 运行测试
python test.py

# 检查日志输出
cat logs/tradingagents.log | grep -E "\[RETRY\]|\[CIRCUIT\]|\[FALLBACK\]|\[TIMEOUT\]"
```

### Final Checklist
- [x] 网络错误触发 fallback 并重试
- [x] Rate limit 触发指数退避重试
- [x] 连续失败触发熔断
- [x] HTTP 请求有超时保护
- [x] 所有改进都有详细日志
- [x] 配置项可通过 DEFAULT_CONFIG 调整
