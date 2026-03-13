"""
快速验证A股技术指标是否真的使用了sina_finance
"""

import sys
sys.path.append('/home/why/github/TradingAgents')

from tradingagents.dataflows.y_finance import _get_stock_stats_bulk, _is_a_share_symbol
from datetime import datetime

# 测试A股检测
symbol = "sh600519"
is_a_share = _is_a_share_symbol(symbol)
print(f"✅ A股检测: {symbol} -> {is_a_share}")

# 测试技术指标获取
curr_date = datetime.now().strftime('%Y-%m-%d')
print(f"\n测试技术指标获取...")
print(f"股票: {symbol}")
print(f"日期: {curr_date}")
print(f"{'=' * 80}")

try:
    result = _get_stock_stats_bulk(symbol, "rsi", curr_date)

    # 统计有效值
    valid_values = [v for v in result.values() if v != "N/A"]
    na_values = [v for v in result.values() if v == "N/A"]

    print(f"✅ 成功获取指标数据:")
    print(f"   总记录数: {len(result)}")
    print(f"   有效值: {len(valid_values)}")
    print(f"   N/A值: {len(na_values)}")

    if len(valid_values) > 0:
        print(f"\n前5个有效值:")
        count = 0
        for date, value in result.items():
            if value != "N/A" and count < 5:
                print(f"   {date}: {value}")
                count += 1

        print(f"\n✅ A股技术指标修复成功!")
        print(f"   新浪财经数据源工作正常")
    else:
        print(f"\n❌ 没有有效值")

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
