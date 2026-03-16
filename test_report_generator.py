#!/usr/bin/env python3
"""
测试报告生成器功能

验证翻译和Markdown生成是否正常工作
"""

import sys
sys.path.append('/home/why/github/TradingAgents')

from tradingagents.graph.report_generator import ReportGenerator
from tradingagents.default_config import DEFAULT_CONFIG

def test_report_generator():
    """测试报告生成器"""

    print("="*60)
    print("测试报告生成器")
    print("="*60)

    # 模拟一个简单的state
    mock_state = {
        "company_of_interest": "sh600519",
        "trade_date": "2026-03-13",
        "market_report": "The market is showing strong bullish trends with increasing volume.",
        "sentiment_report": "Social media sentiment is positive with 75% bullish comments.",
        "news_report": "Recent news indicates strong earnings and growth prospects.",
        "fundamentals_report": "Company shows strong fundamentals with P/E ratio of 35.5 and ROE of 28.5%.",
        "investment_debate_state": {
            "history": "Bull analyst argues for strong growth potential.\nBear analyst concerns about valuation.",
            "judge_decision": "Recommend BUY based on strong fundamentals and growth outlook."
        },
        "trader_investment_plan": "Based on comprehensive analysis, recommend BUY with 5% position.",
        "risk_debate_state": {
            "history": "Aggressive: Low risk, high reward.\nConservative: Valuation concerns.\nNeutral: Balanced approach.",
            "judge_decision": "Risk level: Medium. Suitable for moderate risk investors."
        },
        "final_trade_decision": "FINAL TRANSACTION PROPOSAL: **BUY**"
    }

    decision = "BUY"

    # 测试1: 不翻译
    print("\n测试1: 生成英文报告")
    print("-"*60)

    try:
        generator = ReportGenerator(DEFAULT_CONFIG.copy())
        report_en = generator.generate_markdown_report(
            mock_state,
            decision,
            translate=False
        )

        print("✅ 英文报告生成成功")
        print(f"报告长度: {len(report_en)} 字符")
        print(f"\n报告预览(前500字符):")
        print("-"*60)
        print(report_en[:500])

        # 保存英文报告
        generator.save_report(report_en, "test_report_en.md")
        print("\n✅ 英文报告已保存: test_report_en.md")

    except Exception as e:
        print(f"❌ 英文报告生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 测试2: 翻译
    print("\n" + "="*60)
    print("测试2: 生成中文报告")
    print("-"*60)

    try:
        generator_zh = ReportGenerator(DEFAULT_CONFIG.copy())
        report_zh = generator_zh.generate_markdown_report(
            mock_state,
            decision,
            translate=True
        )

        print("✅ 中文报告生成成功")
        print(f"报告长度: {len(report_zh)} 字符")
        print(f"\n报告预览(前500字符):")
        print("-"*60)
        print(report_zh[:500])

        # 保存中文报告
        generator_zh.save_report(report_zh, "test_report_zh.md")
        print("\n✅ 中文报告已保存: test_report_zh.md")

    except Exception as e:
        print(f"❌ 中文报告生成失败: {e}")
        print("   可能原因: API密钥未配置或网络问题")
        print("   建议: 检查 .env 文件中的 ZHIPU_API_KEY")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "="*60)
    print("✅ 测试完成")
    print("="*60)

    print("\n生成的报告文件:")
    print("  - test_report_en.md (英文报告)")
    print("  - test_report_zh.md (中文报告)")

    return True

if __name__ == "__main__":
    success = test_report_generator()
    sys.exit(0 if success else 1)
