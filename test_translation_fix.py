#!/usr/bin/env python3
"""
快速测试翻译功能
"""

import os
from dotenv import load_dotenv
from tradingagents.graph.report_generator import ReportGenerator
from tradingagents.default_config import DEFAULT_CONFIG

def main():
    # 加载环境变量
    load_dotenv()

    # 检查 API Key
    if not os.environ.get("ZHIPU_API_KEY"):
        print("❌ 错误: 未找到 ZHIPU_API_KEY")
        return

    print("="*60)
    print("🧪 翻译功能测试")
    print("="*60)

    # 配置
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "zhipu"
    config["deep_think_llm"] = "glm-4.5-air"
    config["quick_think_llm"] = "glm-4.5-air"

    print(f"\n📊 配置:")
    print(f"  - 提供商: {config['llm_provider']}")
    print(f"  - 翻译模型: {config['quick_think_llm']}")

    # 初始化翻译器
    generator = ReportGenerator(config)

    # 测试文本
    test_text = """
    Technical Analysis Report for NVDA

    The stock is currently showing a strong bullish trend based on the following indicators:

    1. MACD (Moving Average Convergence Divergence): The MACD line has crossed above the signal line, indicating strong upward momentum.

    2. RSI (Relative Strength Index): Currently at 65, suggesting the stock is approaching overbought territory but still has room for growth.

    3. Volume Analysis: Trading volume has increased significantly over the past week, confirming strong investor interest.

    Recommendation: BUY with a target price of $950 and a stop-loss at $880.
    """

    print(f"\n📝 原文 (英文):")
    print("-"*60)
    print(test_text[:200] + "...")
    print("-"*60)

    print(f"\n🔄 正在翻译...")
    print("-"*60)

    try:
        # 执行翻译
        translated = generator.translate_to_chinese(test_text)

        print(f"\n✅ 翻译成功!")
        print("-"*60)
        print(translated)
        print("-"*60)

        print(f"\n📊 翻译质量检查:")
        print(f"  - 原文长度: {len(test_text)} 字符")
        print(f"  - 译文长度: {len(translated)} 字符")
        print(f"  - 包含中文: {'是' if generator._contains_chinese(translated) else '否'}")

        if generator._contains_chinese(translated):
            print(f"\n✅ 翻译功能正常!")
        else:
            print(f"\n⚠️ 警告: 翻译可能失败")

    except Exception as e:
        print(f"\n❌ 翻译失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
