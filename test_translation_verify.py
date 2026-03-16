#!/usr/bin/env python3
"""
验证翻译修复效果
"""

import os
from dotenv import load_dotenv
from tradingagents.graph.report_generator import ReportGenerator
from tradingagents.default_config import DEFAULT_CONFIG

def main():
    load_dotenv()

    print("="*60)
    print("🧪 翻译修复验证")
    print("="*60)

    # 配置
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "zhipu"
    config["deep_think_llm"] = "glm-4.5-air"
    config["quick_think_llm"] = "glm-4.5-air"

    # 模拟一个 state
    mock_state = {
        "company_of_interest": "TEST",
        "trade_date": "2026-03-13",
        "market_report": "The market is showing strong bullish trends with increasing volume.",
        "fundamentals_report": "Company shows strong fundamentals with P/E ratio of 35.5 and ROE of 28.5%.",
        "news_report": "Recent news indicates strong earnings and growth prospects.",
        "sentiment_report": "Social media sentiment is positive with 75% bullish comments.",
        "investment_debate_state": {
            "history": "Bull analyst argues for strong growth potential. Bear analyst concerns about valuation.",
            "judge_decision": "Recommend BUY based on strong fundamentals and growth outlook."
        },
        "trader_investment_plan": "Based on comprehensive analysis, recommend BUY with 5% position.",
        "risk_debate_state": {
            "history": "Aggressive: Low risk, high reward. Conservative: Valuation concerns. Neutral: Balanced approach.",
            "judge_decision": "Risk level: Medium. Suitable for moderate risk investors."
        },
        "final_trade_decision": "FINAL TRANSACTION PROPOSAL: BUY"
    }

    print(f"\n📊 配置:")
    print(f"  - 提供商: {config['llm_provider']}")
    print(f"  - 模型: {config['quick_think_llm']}")

    print(f"\n🔧 初始化翻译器...")
    print("-"*60)

    # 初始化报告生成器（会输出翻译器状态）
    generator = ReportGenerator(config)

    print(f"\n📝 生成报告（带翻译）...")
    print("-"*60)

    # 生成中文报告
    report_zh = generator.generate_markdown_report(
        mock_state,
        "BUY",
        translate=True
    )

    print(f"\n✅ 中文报告生成成功!")
    print(f"报告长度: {len(report_zh)} 字符")
    print(f"\n前500字符预览:")
    print("="*60)
    print(report_zh[:500])
    print("="*60)

    # 检查是否还有混合文本
    if "The market is showing" in report_zh and "本报告对" in report_zh:
        print(f"\n❌ 警告: 仍然存在混合文本问题")
    elif "[翻译失败" in report_zh:
        print(f"\n⚠️ 翻译失败标记:")
        for line in report_zh.split('\n'):
            if '[翻译失败' in line:
                print(f"  - {line.strip()}")
    else:
        print(f"\n✅ 报告看起来正常!")

if __name__ == "__main__":
    main()
