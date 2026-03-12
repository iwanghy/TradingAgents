#!/usr/bin/env python3
"""
测试 yfinance 速率限制恢复时间

目标：确定需要等待多久才能恢复
"""

import yfinance as yf
import time
import os
from datetime import datetime

os.environ['YFINANCE_NO_CURL'] = '1'

TEST_SYMBOL = "AAPL"
TEST_START = "2024-01-01"
TEST_END = "2024-01-15"

def test_single_call():
    """执行单次测试调用"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    start_time = time.time()

    try:
        ticker = yf.Ticker(TEST_SYMBOL)
        data = ticker.history(start=TEST_START, end=TEST_END, progress=False)
        duration = time.time() - start_time

        if data.empty:
            return {"success": False, "error": "empty_data", "duration": duration}
        else:
            return {"success": True, "records": len(data), "duration": duration}

    except Exception as e:
        duration = time.time() - start_time
        error_msg = str(e)

        if "Too Many Requests" in error_msg or "Rate limited" in error_msg:
            return {"success": False, "error": "rate_limit", "duration": duration}
        else:
            return {"success": False, "error": f"other: {error_msg[:30]}", "duration": duration}

print("=" * 80)
print("🧪 yfinance 速率限制恢复测试")
print("=" * 80)
print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# 测试不同的等待时间
wait_times = [10, 30, 60, 120]  # 秒

for wait_time in wait_times:
    print(f"\n⏳ 等待 {wait_time} 秒后测试...")
    print("-" * 80)

    # 等待
    for remaining in range(wait_time, 0, -10):
        if remaining >= 10:
            print(f"  ⏰ 还剩 {remaining} 秒...", end='\r')
            time.sleep(10)
        else:
            print(f"  ⏰ 还剩 {remaining} 秒...")
            time.sleep(remaining)

    print(f"\n  🔄 测试调用...")
    result = test_single_call()

    if result["success"]:
        print(f"  ✅ SUCCESS | Records: {result['records']} | Duration: {result['duration']:.2f}s")
        print(f"\n🎉 恢复！需要等待约 {wait_time} 秒")
        break
    else:
        print(f"  ❌ {result['error'].upper()} | Duration: {result['duration']:.2f}s")
        if result['error'] == 'rate_limit':
            print(f"  ⏳ 仍然被限制，继续等待...")
        else:
            print(f"  ⚠️  不同错误: {result['error']}")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
