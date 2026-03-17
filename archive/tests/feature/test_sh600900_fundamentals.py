"""
测试 sh600900（长江证券）的基本面数据获取功能

用于调试和验证基本面数据获取是否正常工作
"""
import sys
sys.path.insert(0, '/home/why/github/TradingAgents')

from tradingagents.dataflows.sina_finance import (
    get_sina_fundamentals,
    get_sina_balance_sheet,
    get_sina_cashflow,
    get_sina_income_statement,
)

def test_sh600900_fundamentals():
    """测试 sh600900 的基本面数据获取"""
    print("=" * 80)
    print("测试 sh600900（长江证券）基本面数据获取")
    print("=" * 80)

    ticker = "sh600900"
    curr_date = "2024-12-01"

    # 测试 1: 获取基本面综合数据
    print("\n【测试 1】获取基本面综合数据")
    print(f"股票代码: {ticker}")
    print(f"日期: {curr_date}")
    print("-" * 80)

    result = get_sina_fundamentals(ticker, curr_date)
    print(result[:500] + "..." if len(result) > 500 else result)  # 打印前500字符

    # 测试 2: 获取资产负债表
    print("\n" + "=" * 80)
    print("【测试 2】获取资产负债表")
    print(f"股票代码: {ticker}")
    print(f"频率: quarterly")
    print("-" * 80)

    balance_sheet = get_sina_balance_sheet(ticker, freq="quarterly", curr_date=curr_date)
    print(balance_sheet[:500] + "..." if len(balance_sheet) > 500 else balance_sheet)

    # 测试 3: 获取利润表
    print("\n" + "=" * 80)
    print("【测试 3】获取利润表")
    print(f"股票代码: {ticker}")
    print(f"频率: quarterly")
    print("-" * 80)

    income_statement = get_sina_income_statement(ticker, freq="quarterly", curr_date=curr_date)
    print(income_statement[:500] + "..." if len(income_statement) > 500 else income_statement)

    # 测试 4: 获取现金流量表
    print("\n" + "=" * 80)
    print("【测试 4】获取现金流量表")
    print(f"股票代码: {ticker}")
    print(f"频率: quarterly")
    print("-" * 80)

    cashflow = get_sina_cashflow(ticker, freq="quarterly", curr_date=curr_date)
    print(cashflow[:500] + "..." if len(cashflow) > 500 else cashflow)

    # 分析结果
    print("\n" + "=" * 80)
    print("【问题分析】")
    print("=" * 80)

    # 检查是否包含模拟数据的标识
    all_results = [result, balance_sheet, income_statement, cashflow]
    fake_indicators = ["模拟数据", "TODO", "示例数据", "茅台", "600519"]

    for i, r in enumerate(all_results, 1):
        if any(indicator in r for indicator in fake_indicators):
            print(f"❌ 测试 {i}: 返回的是模拟数据，不是真实的 sh600900 数据")
        elif "Error" in r:
            print(f"❌ 测试 {i}: 返回错误信息")
        else:
            print(f"✅ 测试 {i}: 返回真实数据")

    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)


if __name__ == "__main__":
    test_sh600900_fundamentals()
