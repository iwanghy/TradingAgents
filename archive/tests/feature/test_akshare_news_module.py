#!/usr/bin/env python3
"""
AKShare 新闻模块使用示例

演示如何使用新创建的 akshare_news.py 模块
"""

import sys
sys.path.insert(0, '/home/why/github/TradingAgents')

# 注意：需要在 conda 环境中运行
# conda activate tradingagents

try:
    from tradingagents.dataflows.akshare_news import get_akshare_stock_news, get_akshare_global_news

    print("="*70)
    print("AKShare 新闻模块测试")
    print("="*70)

    # 测试 1: 获取个股新闻
    print("\n1️⃣ 测试获取贵州茅台(600519)的新闻")
    print("-"*70)

    stock_news = get_akshare_stock_news.invoke({
        "symbol": "600519",
        "limit": 5
    })

    print(stock_news[:500] + "..." if len(stock_news) > 500 else stock_news)

    # 测试 2: 获取全球新闻
    print("\n2️⃣ 测试获取宏观经济新闻")
    print("-"*70)

    from datetime import datetime
    today = datetime.now().strftime("%Y%m%d")

    global_news = get_akshare_global_news.invoke({
        "curr_date": today,
        "limit": 5
    })

    print(global_news[:500] + "..." if len(global_news) > 500 else global_news)

    print("\n" + "="*70)
    print("✅ 测试完成")
    print("="*70)

except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("\n请确保已在 conda 环境中运行:")
    print("  conda activate tradingagents")
    sys.exit(1)
except Exception as e:
    print(f"❌ 运行错误: {e}")
    sys.exit(1)
