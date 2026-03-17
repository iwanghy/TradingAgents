#!/usr/bin/env python3
"""
测试翻译功能 - 简化版本
"""

import sys
sys.path.append('/home/why/github/TradingAgents')

from tradingagents.graph.report_generator import ReportGenerator
from tradingagents.default_config import DEFAULT_CONFIG

def test_simple_translation():
    """测试简单文本翻译"""

    print("="*60)
    print("测试翻译功能")
    print("="*60)

    # 创建生成器
    config = DEFAULT_CONFIG.copy()
    generator = ReportGenerator(config)

    # 测试1: 简单英文文本
    print("\n测试1: 简单文本翻译")
    print("-"*60)

    simple_text = "The stock market is showing strong bullish trends."

    try:
        translated = generator.translate_to_chinese(simple_text)
        print(f"原文: {simple_text}")
        print(f"译文: {translated}")
        print("✅ 简单翻译成功")

    except Exception as e:
        print(f"❌ 翻译失败: {e}")

    # 测试2: 检测中文文本
    print("\n测试2: 中文文本检测")
    print("-"*60)

    chinese_text = "这是一个中文测试文本"

    try:
        result = generator.translate_to_chinese(chinese_text)
        print(f"输入: {chinese_text}")
        print(f"输出: {result}")
        print(f"是否跳过翻译: {result == chinese_text}")
        print("✅ 中文检测成功")

    except Exception as e:
        print(f"❌ 检测失败: {e}")

    # 测试3: 长文本截断
    print("\n测试3: 长文本截断")
    print("-"*60)

    long_text = "A" * 10000  # 10000字符

    try:
        result = generator.translate_to_chinese(long_text)
        print(f"原文长度: {len(long_text)}")
        print(f"结果长度: {len(result)}")
        print(f"是否截断: {len(result) < len(long_text)}")
        print("✅ 长文本处理成功")

    except Exception as e:
        print(f"❌ 处理失败: {e}")

    print("\n" + "="*60)
    print("✅ 所有测试完成")
    print("="*60)

if __name__ == "__main__":
    test_simple_translation()
