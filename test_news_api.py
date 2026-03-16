#!/usr/bin/env python3
"""
新闻API独立测试脚本
测试所有新闻数据源
"""

import os
os.environ['YFINANCE_NO_CURL'] = '1'

from datetime import datetime, timedelta
from dotenv import load_dotenv
import time
import traceback

def test_yfinance_news():
    """测试 yfinance 新闻API"""
    print("="*60)
    print("测试1: yfinance 新闻API")
    print("="*60)

    try:
        from tradingagents.dataflows.yfinance_news import (
            get_news_yfinance,
            get_global_news_yfinance
        )

        # 测试1: 股票新闻
        print("\n1️⃣  测试股票新闻...")
        ticker = "AAPL"
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

        print(f"   获取 {ticker} 新闻 ({start_date} 到 {end_date})...")
        result = get_news_yfinance(ticker, start_date, end_date)

        if "Error" in result and "rate limit" in result.lower():
            print(f"   ❌ 限流错误")
        elif "Error" in result:
            print(f"   ❌ 其他错误: {result[:100]}")
        else:
            lines = result.count('\n')
            print(f"   ✅ 成功获取 {lines} 行数据")

        time.sleep(2)  # 延迟避免限流

        # 测试2: 全局新闻
        print("\n2️⃣  测试全局新闻...")
        curr_date = datetime.now().strftime('%Y-%m-%d')
        print(f"   获取全局新闻 (截止 {curr_date})...")

        result = get_global_news_yfinance(curr_date, look_back_days=7, limit=5)

        if "Error" in result and "rate limit" in result.lower():
            print(f"   ❌ 限流错误")
        elif "Error" in result:
            print(f"   ❌ 其他错误: {result[:100]}")
        else:
            lines = result.count('\n')
            print(f"   ✅ 成功获取 {lines} 行数据")

        return True

    except Exception as e:
        print(f"   ❌ 异常: {e}")
        traceback.print_exc()
        return False


def test_alpha_vantage_news():
    """测试 Alpha Vantage 新闻API"""
    print("\n" + "="*60)
    print("测试2: Alpha Vantage 新闻API")
    print("="*60)

    try:
        from tradingagents.dataflows.alpha_vantage_news import (
            get_news,
            get_global_news
        )

        # 测试1: 股票新闻
        print("\n1️⃣  测试股票新闻...")
        ticker = "IBM"  # Alpha Vantage 支持美股
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

        print(f"   获取 {ticker} 新闻 ({start_date} 到 {end_date})...")

        result = get_news(ticker, start_date, end_date)

        if isinstance(result, dict):
            if "error" in str(result).lower():
                print(f"   ❌ 错误: {result}")
            else:
                print(f"   ✅ 成功获取数据")
                print(f"   📊 返回类型: {type(result)}")
                print(f"   📊 内容预览: {str(result)[:200]}...")
        elif isinstance(result, str):
            if "error" in result.lower() or "Error" in result:
                print(f"   ❌ 错误: {result[:100]}")
            else:
                lines = result.count('\n')
                print(f"   ✅ 成功获取 {lines} 行数据")

        return True

    except Exception as e:
        print(f"   ❌ 异常: {e}")
        traceback.print_exc()
        return False


def test_direct_yfinance():
    """直接测试 yfinance 库"""
    print("\n" + "="*60)
    print("测试3: 直接调用 yfinance 库")
    print("="*60)

    try:
        import yfinance as yf

        print("\n1️⃣  测试 get_news()...")
        ticker = yf.Ticker("AAPL")

        try:
            news = ticker.get_news(count=5)
            print(f"   ✅ 成功获取 {len(news)} 条新闻")
            print(f"   📊 第一条新闻标题: {news[0].get('content', {}).get('title', 'N/A')[:50]}...")
        except Exception as e:
            error_str = str(e).lower()
            if "rate" in error_str or "limit" in error_str or "429" in error_str:
                print(f"   ❌ 限流错误: {e}")
            else:
                print(f"   ❌ 其他错误: {e}")

        time.sleep(2)

        print("\n2️⃣  测试 Search()...")
        try:
            search = yf.Search(query="stock market", news_count=5)
            print(f"   ✅ 搜索成功, 新闻数量: {len(search.news) if search.news else 0}")
        except Exception as e:
            error_str = str(e).lower()
            if "rate" in error_str or "limit" in error_str or "429" in error_str:
                print(f"   ❌ 限流错误: {e}")
            else:
                print(f"   ❌ 其他错误: {e}")

        return True

    except Exception as e:
        print(f"   ❌ 异常: {e}")
        traceback.print_exc()
        return False


def test_rate_limit_pattern():
    """测试限流模式"""
    print("\n" + "="*60)
    print("测试4: 限流模式测试")
    print("="*60)

    print("\n🔍 测试多次快速调用是否会触发限流...")

    try:
        import yfinance as yf

        success_count = 0
        rate_limit_count = 0

        for i in range(5):
            print(f"\n   第 {i+1} 次调用...")
            try:
                ticker = yf.Ticker("AAPL")
                news = ticker.get_news(count=1)
                success_count += 1
                print(f"      ✅ 成功")
            except Exception as e:
                error_str = str(e).lower()
                if "rate" in error_str or "limit" in error_str or "429" in error_str:
                    rate_limit_count += 1
                    print(f"      ❌ 限流")
                else:
                    print(f"      ❌ 其他错误: {e}")

            time.sleep(0.5)  # 短暂延迟

        print(f"\n   📊 结果: 成功 {success_count}/5, 限流 {rate_limit_count}/5")

        return True

    except Exception as e:
        print(f"   ❌ 异常: {e}")
        traceback.print_exc()
        return False


def main():
    """主函数"""
    load_dotenv()

    print("\n🔍 新闻API独立测试")
    print("测试时间:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("目标: 诊断新闻API限流问题\n")

    results = {}

    # 测试1: yfinance新闻
    results["yfinance_news"] = test_yfinance_news()

    # 测试2: Alpha Vantage新闻
    results["alpha_vantage"] = test_alpha_vantage_news()

    # 测试3: 直接调用yfinance
    results["direct_yfinance"] = test_direct_yfinance()

    # 测试4: 限流模式
    results["rate_limit_pattern"] = test_rate_limit_pattern()

    # 汇总
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)

    for test_name, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name:25s}: {status}")

    print("\n" + "="*60)
    print("分析建议")
    print("="*60)
    print("""
1. 如果 yfinance 频繁限流:
   - 减少调用频率
   - 添加延迟
   - 实现重试机制

2. 如果 Alpha Vantage 正常:
   - 配置为默认新闻源
   - 设置 fallback 机制

3. 如果直接调用也限流:
   - 这是 yfinance 库的已知限制
   - 需要使用其他数据源
    """)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试中断")
