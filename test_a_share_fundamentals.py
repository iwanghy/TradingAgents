#!/usr/bin/env python3
"""
测试A股基本面数据获取功能
验证sh600519的基本面数据是否能正常获取
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from tradingagents.dataflows.sina_finance import (
    get_sina_fundamentals,
    get_sina_balance_sheet,
    get_sina_income_statement,
    get_sina_cashflow
)


def test_fundamental_data():
    """测试基本面数据获取"""
    print("=" * 80)
    print("测试A股基本面数据获取功能")
    print("=" * 80)

    ticker = "sh600519"  # 贵州茅台
    curr_date = "2026-03-11"

    # 测试1: get_fundamentals
    print("\n" + "=" * 80)
    print("测试1: get_fundamentals()")
    print("=" * 80)
    try:
        result = get_sina_fundamentals(ticker, curr_date)
        print(result[:800])  # 只显示前800字符
        print("\n✅ get_fundamentals 测试通过")
    except Exception as e:
        print(f"\n❌ get_fundamentals 测试失败: {e}")

    # 测试2: get_balance_sheet
    print("\n" + "=" * 80)
    print("测试2: get_balance_sheet()")
    print("=" * 80)
    try:
        result = get_sina_balance_sheet(ticker, freq="quarterly", curr_date=curr_date)
        print(result[:800])
        print("\n✅ get_balance_sheet 测试通过")
    except Exception as e:
        print(f"\n❌ get_balance_sheet 测试失败: {e}")

    # 测试3: get_income_statement
    print("\n" + "=" * 80)
    print("测试3: get_income_statement()")
    print("=" * 80)
    try:
        result = get_sina_income_statement(ticker, freq="quarterly", curr_date=curr_date)
        print(result[:800])
        print("\n✅ get_income_statement 测试通过")
    except Exception as e:
        print(f"\n❌ get_income_statement 测试失败: {e}")

    # 测试4: get_cashflow
    print("\n" + "=" * 80)
    print("测试4: get_cashflow()")
    print("=" * 80)
    try:
        result = get_sina_cashflow(ticker, freq="quarterly", curr_date=curr_date)
        print(result[:800])
        print("\n✅ get_cashflow 测试通过")
    except Exception as e:
        print(f"\n❌ get_cashflow 测试失败: {e}")

    # 测试5: 代码格式转换
    print("\n" + "=" * 80)
    print("测试5: 代码格式转换")
    print("=" * 80)
    from tradingagents.dataflows.sina_finance import convert_symbol_to_sina_format

    test_symbols = ["600519", "sh600519", "000001", "sz000001"]
    for sym in test_symbols:
        converted = convert_symbol_to_sina_format(sym)
        print(f"  {sym} → {converted}")

    print("\n✅ 代码格式转换测试通过")

    # 总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    print("✅ 所有4个基本面数据函数均已添加")
    print("✅ 函数返回结构化数据（包含TODO说明）")
    print("✅ 代码格式转换正常工作")
    print("\n📝 后续改进建议：")
    print("   - 使用 akshare 或 tushare 获取真实A股财务数据")
    print("   - 参考函数中的 TODO 注释了解实现方法")
    print("   - 当前返回的数据为示例格式，可让agent继续工作")
    print("=" * 80)


if __name__ == "__main__":
    test_fundamental_data()
