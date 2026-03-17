#!/usr/bin/env python3
"""
快速验证脚本 - 只测试 LLM 和数据获取，不运行完整流程
"""

import os
os.environ['YFINANCE_NO_CURL'] = '1'

from dotenv import load_dotenv
import json

def quick_test():
    """快速测试核心组件"""
    load_dotenv()

    print("="*60)
    print("🔍 快速验证测试")
    print("="*60)

    results = {}

    # 测试1: 环境变量
    print("\n1️⃣  检查环境变量...")
    if os.environ.get("ZHIPU_API_KEY"):
        print("✅ ZHIPU_API_KEY 已配置")
        results["api_key"] = True
    else:
        print("❌ ZHIPU_API_KEY 未配置")
        results["api_key"] = False

    # 测试2: LLM 客户端
    print("\n2️⃣  测试 LLM 客户端...")
    try:
        from tradingagents.llm_clients import create_llm_client
        from langchain_core.messages import HumanMessage

        llm_client = create_llm_client(
            provider="zhipu",
            model="glm-4.5-air"
        )

        # 简单测试
        result = llm_client.get_llm().invoke([
            HumanMessage(content="请回复'测试成功'")
        ])

        if "测试成功" in result.content or "成功" in result.content:
            print(f"✅ LLM 响应: {result.content}")
            results["llm"] = True
        else:
            print(f"⚠️  LLM 响应异常: {result.content}")
            results["llm"] = False
    except Exception as e:
        print(f"❌ LLM 测试失败: {e}")
        results["llm"] = False

    # 测试3: 数据获取
    print("\n3️⃣  测试新浪财经数据获取...")
    try:
        from tradingagents.dataflows.interface import route_to_vendor

        data = route_to_vendor("get_stock_data", "sh600519", "2025-12-01", "2026-03-16")

        if data and "SH600519" in data and len(data) > 1000:
            lines = data.count('\n')
            print(f"✅ 数据获取成功: {lines} 行数据")
            results["data"] = True
        else:
            print(f"⚠️  数据获取可能有问题")
            results["data"] = False
    except Exception as e:
        print(f"❌ 数据获取失败: {e}")
        results["data"] = False

    # 测试4: TradingAgentsGraph 创建
    print("\n4️⃣  测试 TradingAgentsGraph 创建...")
    try:
        from tradingagents.default_config import DEFAULT_CONFIG
        from tradingagents.graph.trading_graph import TradingAgentsGraph

        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "zhipu"
        config["deep_think_llm"] = "glm-4.5-air"
        config["quick_think_llm"] = "glm-4.5-air"

        ta = TradingAgentsGraph(debug=False, config=config)
        print("✅ TradingAgentsGraph 创建成功")
        results["graph"] = True
    except Exception as e:
        print(f"❌ Graph 创建失败: {e}")
        results["graph"] = False

    # 汇总结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)

    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name:15s}: {status}")

    all_passed = all(results.values())
    print("\n" + "="*60)
    if all_passed:
        print("✅ 所有核心组件测试通过!")
        print("\n💡 完整流程测试预计需要 5-10 分钟")
        print("   可以运行: python test_glm.py")
    else:
        print("❌ 部分测试失败，请检查上述错误")
    print("="*60)

    return all_passed

if __name__ == "__main__":
    import sys
    try:
        success = quick_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(1)
