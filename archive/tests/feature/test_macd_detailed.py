"""
详细分析 sh600900 的 MACD 指标数据

检查 MACD、MACD Signal、MACD Histogram 三个指标
"""
import sys
sys.path.insert(0, '/home/why/github/TradingAgents')

from tradingagents.dataflows.y_finance import get_stock_stats_indicators_window

def test_macd_detailed():
    """详细测试 MACD 相关指标"""
    print("=" * 80)
    print("详细分析 sh600900 的 MACD 指标")
    print("=" * 80)

    symbol = "sh600900"
    curr_date = "2024-11-29"  # 选择一个交易日
    look_back_days = 10

    # 测试所有 MACD 相关指标
    indicators = ["macd", "macds", "macdh"]

    for indicator in indicators:
        print(f"\n{'=' * 80}")
        print(f"测试指标: {indicator}")
        print(f"{'=' * 80}")

        try:
            result = get_stock_stats_indicators_window(symbol, indicator, curr_date, look_back_days)
            print(result)
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()

    # 分析 MACD 数据质量
    print(f"\n{'=' * 80}")
    print("MACD 数据质量分析")
    print(f"{'=' * 80}")

    # 获取最近的数据
    try:
        result = get_stock_stats_indicators_window(symbol, "macd", "2024-11-29", 5)

        # 解析数据
        lines = result.split('\n')
        values = []
        for line in lines:
            if ':' in line and 'N/A' not in line:
                parts = line.split(':')
                if len(parts) == 2:
                    try:
                        value = float(parts[1].strip())
                        values.append(value)
                    except ValueError:
                        pass

        if values:
            print(f"✅ 成功获取 {len(values)} 个数据点")
            print(f"最新值: {values[0]:.6f}")
            print(f"最小值: {min(values):.6f}")
            print(f"最大值: {max(values):.6f}")
            print(f"平均值: {sum(values)/len(values):.6f}")

            # 检查数据异常
            if abs(values[0]) > 10:
                print(f"⚠️  警告: MACD 值异常大 ({values[0]:.6f})")
            if all(v < 0 for v in values):
                print(f"📉 所有值均为负数，表示强劲下跌趋势")
            elif all(v > 0 for v in values):
                print(f"📈 所有值均为正数，表示强劲上涨趋势")
        else:
            print("❌ 没有获取到有效数据")

    except Exception as e:
        print(f"❌ 分析失败: {e}")

    # 对比标准值
    print(f"\n{'=' * 80}")
    print("MACD 标准值参考")
    print(f"{'=' * 80}")
    print("正常范围: -2 到 +2")
    print("强买入信号: MACD 上穿 Signal 且为正")
    print("强卖出信号: MACD 下穿 Signal 且为负")
    print("当前状态需要查看 MACD 与 Signal 的交叉情况")

    print(f"\n{'=' * 80}")
    print("测试完成")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    test_macd_detailed()
