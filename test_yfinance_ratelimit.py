#!/usr/bin/env python3
"""
测试 yfinance API 速率限制规律

目标：
1. 测试连续调用 yfinance 的行为
2. 找出速率限制的触发条件
3. 确定安全的请求间隔
4. 测试重试策略
"""

import yfinance as yf
import time
import os
from datetime import datetime
from collections import defaultdict

# 设置环境变量（如果需要）
os.environ['YFINANCE_NO_CURL'] = '1'

# 测试配置
TEST_SYMBOL = "AAPL"
TEST_START = "2024-01-01"
TEST_END = "2024-01-15"

results = {
    "successful": 0,
    "rate_limited": 0,
    "other_errors": 0,
    "durations": [],
    "timestamps": []
}

def test_yfinance_call(test_num):
    """执行单次 yfinance 调用并记录结果"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    start_time = time.time()

    try:
        ticker = yf.Ticker(TEST_SYMBOL)
        data = ticker.history(start=TEST_START, end=TEST_END, progress=False)

        duration = time.time() - start_time

        if data.empty:
            print(f"[{timestamp}] Test {test_num}: ⚠️  EMPTY DATA | Duration: {duration:.2f}s")
            results["other_errors"] += 1
        else:
            print(f"[{timestamp}] Test {test_num}: ✅ SUCCESS | Records: {len(data)} | Duration: {duration:.2f}s")
            results["successful"] += 1
            results["durations"].append(duration)

    except Exception as e:
        duration = time.time() - start_time
        error_msg = str(e)

        if "Too Many Requests" in error_msg or "Rate limited" in error_msg:
            print(f"[{timestamp}] Test {test_num}: ❌ RATE LIMIT | Duration: {duration:.2f}s")
            results["rate_limited"] += 1
        else:
            print(f"[{timestamp}] Test {test_num}: ❌ ERROR: {error_msg[:50]}... | Duration: {duration:.2f}s")
            results["other_errors"] += 1

    results["timestamps"].append(timestamp)
    return duration

print("=" * 80)
print("🧪 yfinance 速率限制测试")
print("=" * 80)
print(f"📊 测试参数:")
print(f"  - 股票: {TEST_SYMBOL}")
print(f"  - 日期范围: {TEST_START} 到 {TEST_END}")
print(f"  - YFINANCE_NO_CURL: {os.environ.get('YFINANCE_NO_CURL', 'not set')}")
print("=" * 80)

# 测试 1: 快速连续调用（5 次，无延迟）
print("\n📋 测试 1: 快速连续调用（5 次，无延迟）")
print("-" * 80)
for i in range(1, 6):
    test_yfinance_call(i)

print(f"\n结果: ✅ {results['successful']} | ❌ 速率限制: {results['rate_limited']} | ⚠️  其他: {results['other_errors']}")

# 等待一段时间
print("\n⏳ 等待 10 秒...")
time.sleep(10)

# 测试 2: 带延迟的调用（5 次，每次间隔 2 秒）
print("\n📋 测试 2: 带延迟的调用（5 次，间隔 2 秒）")
print("-" * 80)
for i in range(6, 11):
    test_yfinance_call(i)
    if i < 11:  # 最后一次不需要等待
        time.sleep(2)

print(f"\n结果: ✅ {results['successful']} | ❌ 速率限制: {results['rate_limited']} | ⚠️  其他: {results['other_errors']}")

# 等待
print("\n⏳ 等待 10 秒...")
time.sleep(10)

# 测试 3: 测试重试策略（失败后等待 5 秒重试）
print("\n📋 测试 3: 重试策略测试（失败后等待 5 秒重试）")
print("-" * 80)

retry_count = 0
max_retries = 3
retry_delay = 5

for attempt in range(1, max_retries + 1):
    print(f"\n🔄 重试尝试 {attempt}/{max_retries}")
    duration = test_yfinance_call(11 + attempt)

    if duration and "RATE LIMIT" not in str(duration):
        print(f"✅ 重试成功！")
        break
    else:
        print(f"⏳ 等待 {retry_delay} 秒后重试...")
        time.sleep(retry_delay)

# 统计结果
print("\n" + "=" * 80)
print("📊 测试总结")
print("=" * 80)
print(f"总调用次数: {len(results['timestamps'])}")
print(f"✅ 成功: {results['successful']}")
print(f"❌ 速率限制: {results['rate_limited']}")
print(f"⚠️  其他错误: {results['other_errors']}")

if results['durations']:
    avg_duration = sum(results['durations']) / len(results['durations'])
    print(f"⏱️  平均响应时间: {avg_duration:.2f}s")
    print(f"⏱️  最快响应: {min(results['durations']):.2f}s")
    print(f"⏱️  最慢响应: {max(results['durations']):.2f}s")

print("\n💡 建议:")
if results['rate_limited'] > 0:
    rate_limit_rate = results['rate_limited'] / len(results['timestamps'])
    print(f"  - 速率限制发生率: {rate_limit_rate:.1%}")
    print(f"  - 建议：添加 {2} 秒以上的请求延迟")
    print(f"  - 建议：实现指数退避重试机制（2s, 4s, 8s...）")
else:
    print(f"  - ✅ 所有调用成功！")
    print(f"  - 当前网络状态良好")

print("=" * 80)
