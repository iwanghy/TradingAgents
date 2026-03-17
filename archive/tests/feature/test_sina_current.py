"""
测试 sina_finance API 使用当前日期范围
"""

import sys
sys.path.append('/home/why/github/TradingAgents')

from tradingagents.dataflows.sina_finance import get_sina_data_online
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta

def test_sina_api_current():
    print("=" * 80)
    print("测试新浪财经 API - 当前日期数据获取")
    print("=" * 80)

    # 使用当前日期
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    test_cases = [
        ("sh600519", start_date, end_date, "贵州茅台"),
    ]

    for symbol, start, end, name in test_cases:
        print(f"\n{'=' * 80}")
        print(f"测试: {name} ({symbol})")
        print(f"日期范围: {start} 至 {end}")
        print(f"{'=' * 80}")

        # 调用 API
        result = get_sina_data_online(symbol, start, end)

        # 检查是否返回错误
        if result.startswith("Error:") or result.startswith("No data"):
            print(f"❌ API 调用失败:")
            print(f"   {result}")
            continue

        # 解析数据
        lines = result.split('\n')

        # 找到数据开始的位置
        data_start_idx = -1
        for i, line in enumerate(lines):
            if line.startswith('Date,'):
                data_start_idx = i
                break

        if data_start_idx >= 0:
            csv_lines = lines[data_start_idx:]

            try:
                df = pd.read_csv(StringIO('\n'.join(csv_lines)))

                print(f"✅ 成功获取数据:")
                print(f"   数据行数: {len(df)}")
                print(f"   列名: {list(df.columns)}")

                # 检查必需的列
                required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
                missing_cols = [col for col in required_cols if col not in df.columns]

                if missing_cols:
                    print(f"❌ 缺少必需列: {missing_cols}")
                else:
                    print(f"✅ 所有必需列都存在")

                    # 显示前5行和后5行数据
                    print(f"\n前5行数据:")
                    print(df.head().to_string(index=False))

                    print(f"\n后5行数据:")
                    print(df.tail().to_string(index=False))

                    # 验证数据质量
                    print(f"\n数据质量检查:")
                    print(f"   日期范围: {df['Date'].min()} 至 {df['Date'].max()}")
                    print(f"   Open 范围: {df['Open'].min():.2f} - {df['Open'].max():.2f}")
                    print(f"   Close 范围: {df['Close'].min():.2f} - {df['Close'].max():.2f}")
                    print(f"   Volume 范围: {df['Volume'].min()} - {df['Volume'].max()}")

                    # 检查是否有空值
                    null_counts = df.isnull().sum()
                    if null_counts.sum() == 0:
                        print(f"✅ 无空值")
                    else:
                        print(f"⚠️ 存在空值:")
                        print(f"   {null_counts[null_counts > 0].to_dict()}")

                    # 测试 stockstats 兼容性
                    print(f"\n测试 stockstats 兼容性:")
                    try:
                        from stockstats import wrap
                        df_copy = df.copy()
                        df_wrapped = wrap(df_copy)

                        # 测试计算一些指标
                        df_wrapped['close_10_sma']
                        df_wrapped['rsi']

                        print(f"✅ stockstats 计算成功")
                        print(f"   SMA(10) 范围: {df_wrapped['close_10_sma'].min():.2f} - {df_wrapped['close_10_sma'].max():.2f}")
                        print(f"   RSI 范围: {df_wrapped['rsi'].min():.2f} - {df_wrapped['rsi'].max():.2f}")

                    except Exception as e:
                        print(f"❌ stockstats 计算失败: {e}")

            except Exception as e:
                print(f"❌ 解析数据失败: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"❌ 未找到CSV数据")
            print(f"原始数据 (前500字符):")
            print(result[:500])

    print(f"\n{'=' * 80}")
    print("测试完成")
    print(f"{'=' * 80}")

if __name__ == "__main__":
    test_sina_api_current()
