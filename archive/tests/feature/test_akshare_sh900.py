"""
测试使用 akshare 获取 sh600900 的真实基本面数据

验证修复后的功能
"""
import sys
sys.path.insert(0, '/home/why/github/TradingAgents')

from tradingagents.dataflows.akshare_fundamentals import (
    get_akshare_fundamentals,
    get_akshare_balance_sheet,
    get_akshare_cashflow,
    get_akshare_income_statement,
)

def test_akshare_sh600900():
    """测试使用 akshare 获取 sh600900 真实数据"""
    print("=" * 80)
    print("测试 akshare 获取 sh600900（长江电力）真实基本面数据")
    print("=" * 80)

    ticker = "sh600900"
    curr_date = "2024-12-01"

    # 测试 1: 获取基本面综合数据
    print("\n【测试 1】获取基本面综合数据（akshare）")
    print(f"股票代码: {ticker}")
    print("-" * 80)

    result = get_akshare_fundamentals(ticker, curr_date)
    print(result[:800] if len(result) > 800 else result)

    # 验证是否为真实数据
    print("\n【验证】")
    if "长江电力" in result and "600900" in result:
        print("✅ 包含正确的公司名称和代码")
    else:
        print("❌ 不包含正确的公司信息")

    if "东方财富" in result:
        print("✅ 数据来源正确（东方财富/akshare）")
    else:
        print("❌ 数据来源不正确")

    # 测试 2: 获取资产负债表（只打印前500字符）
    print("\n" + "=" * 80)
    print("【测试 2】获取资产负债表（akshare）")
    print("-" * 80)

    balance_sheet = get_akshare_balance_sheet(ticker, freq="quarterly", curr_date=curr_date)
    print(balance_sheet[:500] if len(balance_sheet) > 500 else balance_sheet)

    if "Error" not in balance_sheet and "No data" not in balance_sheet:
        print("\n✅ 资产负债表数据获取成功")
    else:
        print(f"\n❌ 资产负债表数据获取失败")

    # 测试 3: 获取利润表
    print("\n" + "=" * 80)
    print("【测试 3】获取利润表（akshare）")
    print("-" * 80)

    income_statement = get_akshare_income_statement(ticker, freq="quarterly", curr_date=curr_date)
    print(income_statement[:500] if len(income_statement) > 500 else income_statement)

    if "Error" not in income_statement and "No data" not in income_statement:
        print("\n✅ 利润表数据获取成功")
    else:
        print(f"\n❌ 利润表数据获取失败")

    # 测试 4: 获取现金流量表
    print("\n" + "=" * 80)
    print("【测试 4】获取现金流量表（akshare）")
    print("-" * 80)

    cashflow = get_akshare_cashflow(ticker, freq="quarterly", curr_date=curr_date)
    print(cashflow[:500] if len(cashflow) > 500 else cashflow)

    if "Error" not in cashflow and "No data" not in cashflow:
        print("\n✅ 现金流量表数据获取成功")
    else:
        print(f"\n❌ 现金流量表数据获取失败")

    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)


if __name__ == "__main__":
    test_akshare_sh600900()
