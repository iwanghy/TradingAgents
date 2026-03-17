#!/usr/bin/env python3
"""
最小化测试 - 只测试核心流程，不包含辩论和风险管理
"""

import os
os.environ['YFINANCE_NO_CURL'] = '1'

from datetime import datetime
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv
import sys

def minimal_test():
    """最小化测试"""
    load_dotenv()

    print("🔍 最小化测试开始\n")

    # 最简单的配置
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "zhipu"
    config["deep_think_llm"] = "glm-4.5-air"
    config["quick_think_llm"] = "glm-4.5-air"
    config["max_debate_rounds"] = 0  # 禁用辩论
    config["max_risk_discuss_rounds"] = 0  # 禁用风险讨论
    config["max_llm_retries"] = 2  # 减少重试次数

    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph

        print("✅ 模块导入成功")
        print(f"📊 配置: {config['llm_provider']}/{config['deep_think_llm']}")

        # 创建图实例（不启用 debug，减少输出）
        print("\n⏳ 创建 TradingAgentsGraph...")
        ta = TradingAgentsGraph(debug=False, config=config)
        print("✅ TradingAgentsGraph 创建成功")

        # 运行分析
        print("\n⏳ 开始分析 sh600519...")
        print("⚠️  这可能需要 2-3 分钟，请耐心等待...\n")

        import time
        start_time = time.time()

        # 运行前向传播
        state, decision = ta.propagate("sh600519", "2026-03-16")

        duration = time.time() - start_time

        print(f"\n{'='*60}")
        print(f"✅ 分析完成! 耗时: {duration:.1f}秒")
        print(f"{'='*60}\n")

        print(f"📊 最终决策: {decision}\n")

        # 检查 state 内容
        print(f"📋 State 包含的字段:")
        for key, value in state.items():
            if isinstance(value, str):
                print(f"  ✅ {key}: {len(value)} 字符")
            elif isinstance(value, dict):
                print(f"  ✅ {key}: dict with {len(value)} keys")
            elif isinstance(value, list):
                print(f"  ✅ {key}: list with {len(value)} items")
            else:
                print(f"  ✅ {key}: {type(value).__name__}")

        return True

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = minimal_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(1)
