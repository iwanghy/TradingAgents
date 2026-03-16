#!/usr/bin/env python3
"""
测试并行翻译的性能对比

验证 ThreadPoolExecutor 并行翻译相比串行翻译的性能提升
"""
import time
from datetime import datetime
from tradingagents.graph.report_generator import ReportGenerator
from tradingagents.default_config import DEFAULT_CONFIG


def create_mock_state():
    """创建模拟的 state 数据用于测试"""
    mock_reports = {
        "market_report": """
        Market Analysis Report

        The current market conditions show a strong upward trend in the technology sector.
        Major indices have reached new highs, driven by positive earnings reports and
        strong economic indicators. Investor sentiment remains bullish despite concerns
        about inflation and interest rates.

        Key observations:
        - S&P 500 up 2.5% this week
        - NASDAQ showing strongest performance
        - Volatility indices at near-term lows
        """,

        "fundamentals_report": """
        Fundamental Analysis Report

        Company XYZ demonstrates strong financial health with consistent revenue growth.
        Key metrics analysis reveals:

        Revenue: $15.2B (up 12% YoY)
        Net Income: $3.8B (up 15% YoY)
        P/E Ratio: 28.5 (slightly above sector average)
        Debt-to-Equity: 0.35 (healthy level)

        The company maintains strong competitive advantages in its core markets,
        with a robust R&D pipeline and expanding market share.
        """,

        "news_report": """
        News Analysis Report

        Recent news flow has been predominantly positive:

        1. Product Launch Success: New product line exceeded sales expectations
        2. Strategic Partnership: Major collaboration announcement with industry leader
        3. Analyst Upgrades: Three major firms upgraded ratings to "Buy"
        4. Market Expansion: Entry into two new international markets

        No significant negative news or regulatory concerns identified.
        """,

        "sentiment_report": """
        Sentiment Analysis Report

        Social media and market sentiment analysis indicates:

        Overall Sentiment Score: 8.2/10 (Positive)
        Twitter Mentions: 45,000 (up 20% from last week)
        Reddit Discussion Volume: High positive correlation
        News Sentiment: 75% positive articles

        Key themes in discussions:
        - Innovation leadership
        - Strong management team
        - Growth potential in AI sector
        """,

        "investment_debate_state": {
            "history": """
            Bullish View:
            - Strong technical indicators pointing upward
            - Institutional accumulation observed
            - Positive sector rotation trends

            Bearish View:
            - Market may be overextended
            - Valuation concerns at current levels
            - Potential headwinds from macroeconomic factors

            Judge Conclusion:
            After weighing both arguments, the bullish perspective appears
            more compelling given the fundamental strength and market positioning.
            """,
            "judge_decision": "Decision: Bullish case prevails based on technical and fundamental strength."
        },

        "trader_investment_plan": """
        Trader Investment Plan

        Recommended Action: BUY
        Entry Price: Current market price
        Target Price: $285.00 (15% upside potential)
        Stop Loss: $235.00 (5% downside protection)

        Position Sizing: 5% of portfolio
        Time Horizon: 3-6 months

        Rationale:
        - Strong momentum indicators
        - Positive earnings expectations
        - Favorable risk/reward ratio (3:1)
        """,

        "risk_debate_state": {
            "history": """
            Risk Discussion:

            Market Risk: Moderate - sector-specific volatility expected
            Liquidity Risk: Low - high trading volume ensures easy exit
            Concentration Risk: Medium - tech sector exposure

            Risk Mitigation:
            - Diversified entry points
            - Trailing stop loss implementation
            - Position size management

            Risk Conclusion:
            Risk level acceptable given expected returns. Proceed with caution.
            """,
            "judge_decision": "Risk Assessment: MODERATE risk level - approved with standard safeguards."
        },

        "final_trade_decision": """
        Final Trade Decision: BUY

        Decision Rationale:
        1. Strong fundamental momentum with earnings growth
        2. Positive technical setup with key breakouts
        3. Favorable market sentiment and news flow
        4. Acceptable risk profile with proper safeguards

        Confidence Level: HIGH (85%)

        The convergence of positive factors across all analysis dimensions
        supports a strong buy recommendation. Proper risk management protocols
        should be implemented to protect against market volatility.
        """
    }

    return mock_reports


def test_serial_translation(report_generator: ReportGenerator, state: dict):
    """测试串行翻译（原始方法）"""
    print("\n" + "="*60)
    print("🐌 测试串行翻译（原始方法）")
    print("="*60 + "\n")

    start_time = time.time()

    # 模拟原始的串行翻译过程
    reports = {}
    for key, value in state.items():
        if isinstance(value, str) and value:
            print(f"正在翻译: {key}...")
            translated = report_generator.translate_to_chinese(value)
            reports[key] = translated

    end_time = time.time()
    elapsed = end_time - start_time

    print(f"\n✅ 串行翻译完成")
    print(f"   总耗时: {elapsed:.2f} 秒")
    print(f"   翻译部分数: {len(reports)}")
    print(f"   平均每部分: {elapsed/len(reports):.2f} 秒")

    return elapsed, reports


def test_parallel_translation(report_generator: ReportGenerator, state: dict):
    """测试并行翻译（优化方法）"""
    print("\n" + "="*60)
    print("🚀 测试并行翻译（优化方法）")
    print("="*60 + "\n")

    start_time = time.time()

    # 使用并行翻译
    translated_reports = report_generator._translate_reports_parallel(
        state,
        max_workers=5
    )

    end_time = time.time()
    elapsed = end_time - start_time

    print(f"\n✅ 并行翻译完成")
    print(f"   总耗时: {elapsed:.2f} 秒")
    print(f"   翻译部分数: {len(translated_reports)}")
    print(f"   平均每部分: {elapsed/len(translated_reports):.2f} 秒")

    return elapsed, translated_reports


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("🧪 ReportGenerator 并行翻译性能测试")
    print("="*60)

    # 初始化配置
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "openai"  # 根据你的配置更改
    config["quick_think_llm"] = "gpt-4o-mini"  # 使用快速模型进行测试

    # 创建 ReportGenerator 实例
    print("\n正在初始化 ReportGenerator...")
    report_gen = ReportGenerator(config=config)

    if not report_gen.translator:
        print("❌ 翻译器初始化失败，请检查配置")
        return

    print("✅ ReportGenerator 初始化成功\n")

    # 创建模拟数据
    print("正在创建测试数据...")
    mock_state = create_mock_state()
    print(f"✅ 测试数据创建完成 ({len(mock_state)} 个报告部分)\n")

    # 测试串行翻译
    try:
        serial_time, serial_reports = test_serial_translation(report_gen, mock_state)
    except Exception as e:
        print(f"❌ 串行翻译测试失败: {e}")
        serial_time = None

    print("\n" + "💤 "*15 + "\n")

    # 测试并行翻译
    try:
        parallel_time, parallel_reports = test_parallel_translation(report_gen, mock_state)
    except Exception as e:
        print(f"❌ 并行翻译测试失败: {e}")
        parallel_time = None

    # 性能对比
    if serial_time and parallel_time:
        print("\n" + "="*60)
        print("📊 性能对比结果")
        print("="*60)
        print(f"\n串行翻译耗时: {serial_time:.2f} 秒")
        print(f"并行翻译耗时: {parallel_time:.2f} 秒")
        print(f"时间节省: {serial_time - parallel_time:.2f} 秒")
        print(f"性能提升: {(serial_time / parallel_time - 1) * 100:.1f}%")
        print(f"加速比: {serial_time / parallel_time:.2f}x\n")

        # 验证翻译结果一致性
        print("="*60)
        print("🔍 翻译结果验证")
        print("="*60)

        all_keys = set(serial_reports.keys()) | set(parallel_reports.keys())
        consistent = True

        for key in sorted(all_keys):
            serial_result = serial_reports.get(key, "")
            parallel_result = parallel_reports.get(key, "")

            # 简单验证：检查长度是否接近（允许小差异）
            if abs(len(serial_result) - len(parallel_result)) > 100:
                print(f"⚠️  {key}: 结果可能不一致")
                print(f"   串行长度: {len(serial_result)}, 并行长度: {len(parallel_result)}")
                consistent = False

        if consistent:
            print("✅ 所有翻译结果基本一致\n")

    print("="*60)
    print("测试完成")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
