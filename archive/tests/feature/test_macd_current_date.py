"""
使用当前日期测试 sh600900 的 MACD 指标

这个测试使用真实的当前日期（2026年3月），而不是硬编码的 2024 年
"""
import sys
sys.path.insert(0, '/home/why/github/TradingAgents')

from datetime import datetime
from tradingagents.dataflows.y_finance import get_stock_stats_indicators_window

def test_macd_with_current_date():
    """使用当前日期测试 MACD"""
    print("=" * 80)
    print(f"测试 sh600900（长江电力）MACD 指标 - 使用当前日期")
    print("=" * 80)

    # 使用当前日期
    curr_date = datetime.now().strftime('%Y-%m-%d')
    symbol = "sh600900"
    look_back_days = 10

    print(f"\n当前系统日期: {curr_date}")
    print(f"股票代码: {symbol}")
    print(f"回看天数: {look_back_days}")
    print("-" * 80)

    # 测试 MACD
    print(f"\n【MACD 指标】")
    try:
        result = get_stock_stats_indicators_window(symbol, "macd", curr_date, look_back_days)
        print(result)
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

    # 测试 MACD Signal
    print(f"\n{'=' * 80}")
    print(f"【MACD Signal 指标】")
    print("-" * 80)
    try:
        result = get_stock_stats_indicators_window(symbol, "macds", curr_date, look_back_days)
        print(result)
    except Exception as e:
        print(f"❌ 错误: {e}")

    # 测试 MACD Histogram
    print(f"\n{'=' * 80}")
    print(f"【MACD Histogram 指标】")
    print("-" * 80)
    try:
        result = get_stock_stats_indicators_window(symbol, "macdh", curr_date, look_back_days)
        print(result)
    except Exception as e:
        print(f"❌ 错误: {e}")

    # 技术分析
    print(f"\n{'=' * 80}")
    print(f"【技术分析】")
    print("-" * 80)
    print(f"✅ 使用了当前日期: {curr_date}")
    print(f"✅ 数据应该是最新的（如果数据源有更新的话）")
    print(f"⚠️  如果显示 N/A，可能是因为：")
    print(f"   - 市场休假日（周末）")
    print(f"   - 数据源还没有更新到最新日期")
    print(f"   - 网络连接问题")

    print(f"\n{'=' * 80}")
    print("测试完成")
    print("=" * 80)


if __name__ == "__main__":
    test_macd_with_current_date()
