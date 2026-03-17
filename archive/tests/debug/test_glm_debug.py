#!/usr/bin/env python3
"""
GLM 4.7 诊断测试脚本 - 分步执行，便于定位问题
"""

import os
os.environ['YFINANCE_NO_CURL'] = '1'

from datetime import datetime
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv

def test_step_by_step():
    """分步测试每个组件"""
    load_dotenv()

    print("="*60)
    print("🔍 GLM 4.7 诊断测试")
    print("="*60)

    # 检查1: API Key
    print("\n✅ 检查1: API Key")
    if not os.environ.get("ZHIPU_API_KEY"):
        print("❌ 错误: 未找到 ZHIPU_API_KEY")
        return False
    print(f"✅ ZHIPU_API_KEY 已配置")

    # 检查2: 配置
    print("\n✅ 检查2: 配置")
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "zhipu"
    config["deep_think_llm"] = "glm-4.5-air"
    config["quick_think_llm"] = "glm-4.5-air"
    config["max_debate_rounds"] = 0  # 暂时禁用辩论
    config["max_risk_discuss_rounds"] = 0  # 暂时禁用风险讨论
    config["max_llm_retries"] = 3
    print(f"✅ 配置完成: {config['llm_provider']}/{config['deep_think_llm']}")

    # 检查3: LLM 客户端
    print("\n✅ 检查3: LLM 客户端")
    try:
        from tradingagents.llm_clients import create_llm_client
        llm = create_llm_client(
            provider="zhipu",
            model="glm-4.5-air"
        )
        print(f"✅ LLM 客户端创建成功")

        # 测试简单的 LLM 调用
        print("\n✅ 检查4: 测试 LLM 调用")
        from langchain_core.messages import HumanMessage
        result = llm.get_llm().invoke([HumanMessage(content="你好，请回复'测试成功'")])
        print(f"✅ LLM 调用成功: {result.content[:50]}")
    except Exception as e:
        print(f"❌ LLM 客户端失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 检查5: 数据获取
    print("\n✅ 检查5: 数据获取")
    try:
        from tradingagents.dataflows.interface import route_to_vendor
        data = route_to_vendor("get_stock_data", "sh600519", "2025-12-16", "2026-03-16")
        print(f"✅ 数据获取成功: {len(data)} 字符")
    except Exception as e:
        print(f"❌ 数据获取失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 检查6: TradingAgentsGraph 初始化
    print("\n✅ 检查6: TradingAgentsGraph 初始化")
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        ta = TradingAgentsGraph(debug=True, config=config)
        print(f"✅ TradingAgentsGraph 初始化成功")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 检查7: 简单分析（无辩论）
    print("\n✅ 检查7: 运行简单分析")
    try:
        ticker = "sh600519"
        trade_date = "2026-03-16"
        print(f"📊 分析 {ticker} ({trade_date})...")
        print("⏳ 这可能需要 1-2 分钟...")

        import time
        start_time = time.time()

        state, decision = ta.propagate(ticker, trade_date)

        duration = time.time() - start_time
        print(f"\n✅ 分析完成! 耗时: {duration:.1f}秒")
        print(f"\n📊 最终决策: {decision}")

        # 检查 state 内容
        print(f"\n📋 State 包含的字段:")
        for key in state.keys():
            value = state[key]
            if isinstance(value, str):
                print(f"  - {key}: {len(value)} 字符")
            else:
                print(f"  - {key}: {type(value).__name__}")

        return True

    except Exception as e:
        print(f"\n❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_step_by_step()
    print("\n" + "="*60)
    if success:
        print("✅ 所有检查通过")
    else:
        print("❌ 部分检查失败")
    print("="*60)
