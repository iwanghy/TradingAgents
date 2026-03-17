"""
测试 sh600900（长江电力）的技术面数据获取功能

特别关注 MACD 指标的问题
"""
import sys
sys.path.insert(0, '/home/why/github/TradingAgents')

from tradingagents.dataflows.y_finance import get_stock_stats_indicators_window
from tradingagents.dataflows.interface import route_to_vendor

def test_sh600900_macd():
    """测试 sh600900 的 MACD 指标获取"""
    print("=" * 80)
    print("测试 sh600900（长江电力）MACD 技术指标")
    print("=" * 80)

    symbol = "sh600900"
    indicator = "macd"
    curr_date = "2024-12-01"
    look_back_days = 30

    # 测试 1: 直接调用 y_finance 函数
    print("\n【测试 1】直接调用 y_finance.get_stock_stats_indicators_window")
    print(f"股票代码: {symbol}")
    print(f"指标: {indicator}")
    print(f"日期: {curr_date}")
    print(f"回看天数: {look_back_days}")
    print("-" * 80)

    try:
        result = get_stock_stats_indicators_window(symbol, indicator, curr_date, look_back_days)
        print(result[:1000] if len(result) > 1000 else result)
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

    # 测试 2: 通过 route_to_vendor 调用
    print("\n" + "=" * 80)
    print("【测试 2】通过 route_to_vendor 调用")
    print("-" * 80)

    try:
        result2 = route_to_vendor("get_indicators", symbol, indicator, curr_date, look_back_days)
        print(result2[:1000] if len(result2) > 1000 else result2)
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

    # 测试 3: 测试其他指标
    print("\n" + "=" * 80)
    print("【测试 3】测试其他技术指标（RSI）")
    print("-" * 80)

    try:
        result3 = get_stock_stats_indicators_window(symbol, "rsi", curr_date, 10)
        print(result3[:500] if len(result3) > 500 else result3)
    except Exception as e:
        print(f"❌ 错误: {e}")

    # 测试 4: 测试代码转换
    print("\n" + "=" * 80)
    print("【测试 4】测试股票代码转换")
    print("-" * 80)

    from tradingagents.dataflows.y_finance import _is_a_share_symbol, _convert_to_sina_format

    test_symbols = ["sh600900", "600900", "SH600900", "AAPL"]
    for s in test_symbols:
        is_a_share = _is_a_share_symbol(s)
        sina_format = _convert_to_sina_format(s)
        print(f"{s:15} -> A股: {is_a_share:5} -> 新浪格式: {sina_format}")

    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)


if __name__ == "__main__":
    test_sh600900_macd()
