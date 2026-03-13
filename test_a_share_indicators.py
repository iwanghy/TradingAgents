"""
测试A股技术指标修复
验证sh600519的技术指标能否正确计算
"""

import sys
sys.path.append('/home/why/github/TradingAgents')

from tradingagents.dataflows.y_finance import _get_stock_stats_bulk, _is_a_share_symbol, _convert_to_sina_format
from datetime import datetime, timedelta

def test_a_share_detection():
    print("=" * 80)
    print("测试1: A股代码检测")
    print("=" * 80)

    test_symbols = [
        ("sh600519", True, "茅台-前缀格式"),
        ("600519", True, "茅台-纯数字"),
        ("600519.SS", True, "茅台-带后缀"),
        ("sz000001", True, "平安银行-前缀格式"),
        ("000001", True, "平安银行-纯数字"),
        ("AAPL", False, "苹果美股"),
        ("NVDA", False, "英伟达美股"),
    ]

    all_passed = True
    for symbol, expected, desc in test_symbols:
        result = _is_a_share_symbol(symbol)
        status = "✅" if result == expected else "❌"
        if result != expected:
            all_passed = False
        print(f"{status} {symbol:15} -> {result:5} (预期: {expected:5}) - {desc}")

    print(f"\n{'=' * 80}")
    if all_passed:
        print("✅ 所有A股检测测试通过")
    else:
        print("❌ 部分A股检测测试失败")
    print(f"{'=' * 80}\n")

    return all_passed


def test_sina_format_conversion():
    print("=" * 80)
    print("测试2: 新浪格式转换")
    print("=" * 80)

    test_cases = [
        ("sh600519", "sh600519"),
        ("600519", "sh600519"),
        ("600519.SS", "sh600519"),
        ("sz000001", "sz000001"),
        ("000001", "sz000001"),
        ("AAPL", "AAPL"),
    ]

    all_passed = True
    for input_symbol, expected in test_cases:
        result = _convert_to_sina_format(input_symbol)
        status = "✅" if result == expected else "❌"
        if result != expected:
            all_passed = False
        print(f"{status} {input_symbol:15} -> {result:10} (预期: {expected:10})")

    print(f"\n{'=' * 80}")
    if all_passed:
        print("✅ 所有格式转换测试通过")
    else:
        print("❌ 部分格式转换测试失败")
    print(f"{'=' * 80}\n")

    return all_passed


def test_technical_indicators():
    print("=" * 80)
    print("测试3: A股技术指标计算")
    print("=" * 80)

    test_cases = [
        ("sh600519", "close_50_sma", "贵州茅台-50日均线"),
        ("sh600519", "rsi", "贵州茅台-RSI"),
        ("600519", "macd", "贵州茅台-MACD"),
        ("sz000001", "close_200_sma", "平安银行-200日均线"),
    ]

    all_passed = True
    for symbol, indicator, desc in test_cases:
        print(f"\n测试: {desc} ({symbol})")
        print(f"指标: {indicator}")
        print(f"{'-' * 80}")

        try:
            curr_date = datetime.now().strftime('%Y-%m-%d')
            result_dict = _get_stock_stats_bulk(symbol, indicator, curr_date)

            if not result_dict:
                print(f"❌ 返回空字典")
                all_passed = False
                continue

            # 检查结果
            na_count = sum(1 for v in result_dict.values() if v == "N/A")
            valid_count = len(result_dict) - na_count

            print(f"✅ 成功获取数据:")
            print(f"   总记录数: {len(result_dict)}")
            print(f"   有效值: {valid_count}")
            print(f"   N/A值: {na_count}")

            if valid_count == 0:
                print(f"❌ 没有有效指标值")
                all_passed = False
            else:
                # 显示前5个有效值
                print(f"\n前5个有效值:")
                count = 0
                for date, value in result_dict.items():
                    if value != "N/A" and count < 5:
                        try:
                            val_float = float(value)
                            print(f"   {date}: {value}")
                            count += 1
                        except ValueError:
                            pass

                if valid_count > 5:
                    print(f"   ... (还有 {valid_count - 5} 个有效值)")

        except Exception as e:
            print(f"❌ 计算失败: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False

    print(f"\n{'=' * 80}")
    if all_passed:
        print("✅ 所有技术指标测试通过")
    else:
        print("❌ 部分技术指标测试失败")
    print(f"{'=' * 80}\n")

    return all_passed


def main():
    print("\n" + "=" * 80)
    print("A股技术指标修复验证")
    print("=" * 80 + "\n")

    results = []

    # 运行测试
    results.append(("A股代码检测", test_a_share_detection()))
    results.append(("新浪格式转换", test_sina_format_conversion()))
    results.append(("技术指标计算", test_technical_indicators()))

    # 总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)

    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} - {test_name}")

    all_passed = all(passed for _, passed in results)

    print(f"\n{'=' * 80}")
    if all_passed:
        print("✅✅✅ 所有测试通过! A股技术指标修复成功!")
    else:
        print("❌ 部分测试失败,需要进一步调试")
    print(f"{'=' * 80}\n")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
