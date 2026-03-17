"""
测试 sina_finance API 是否能正确获取 A 股价格数据
用于技术指标计算
"""

import sys
sys.path.append('/home/why/github/TradingAgents')

from tradingagents.dataflows.sina_finance import get_sina_data_online, convert_symbol_to_sina_format
import pandas as pd
from io import StringIO

def test_sina_api():
    print("=" * 80)
    print("测试新浪财经 API - A股价格数据获取")
    print("=" * 80)

    # 测试用例
    test_cases = [
        ("sh600519", "2024-01-01", "2024-01-31", "贵州茅台"),
        ("sz000001", "2024-01-01", "2024-01-31", "平安银行"),
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

        # 解析 CSV 数据
        lines = result.split('\n')
        data_start = False
        df_data = []

        for line in lines:
            if data_start:
                if line.strip() and not line.startswith('#'):
                    df_data.append(line)
            elif line.startswith('Date,'):
                data_start = True

        if df_data:
            csv_content = '\n'.join(['Date,' + ','.join(lines[0].split(',')[1:]) if 'Date,' in line else line
                                      for line in lines if 'Date,' in line or data_start])

            # 使用 StringIO 转换为 DataFrame
            try:
                # 重新构建 CSV
                csv_lines = [line for line in lines if not line.startswith('#') and line.strip()]
                if csv_lines:
                    df = pd.read_csv(StringIO('\n'.join(csv_lines)))

                    print(f"✅ 成功获取数据:")
                    print(f"   数据行数: {len(df)}")
                    print(f"   日期范围: {df['Date'].min()} 至 {df['Date'].max()}")
                    print(f"   列名: {list(df.columns)}")

                    # 检查必需的列
                    required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
                    missing_cols = [col for col in required_cols if col not in df.columns]

                    if missing_cols:
                        print(f"❌ 缺少必需列: {missing_cols}")
                    else:
                        print(f"✅ 所有必需列都存在")

                        # 显示前5行数据
                        print(f"\n前5行数据:")
                        print(df.head().to_string(index=False))

                        # 验证数据质量
                        print(f"\n数据质量检查:")
                        print(f"   Open 范围: {df['Open'].min():.2f} - {df['Open'].max():.2f}")
                        print(f"   Close 范围: {df['Close'].min():.2f} - {df['Close'].max():.2f}")
                        print(f"   Volume 范围: {df['Volume'].min()} - {df['Volume'].max()}")

                        if (df['Open'] > 0).all() and (df['Close'] > 0).all():
                            print(f"✅ 价格数据有效")
                        else:
                            print(f"❌ 价格数据包含无效值")

            except Exception as e:
                print(f"❌ 解析数据失败: {e}")
                print(f"原始数据:\n{result[:500]}")
        else:
            print(f"❌ 未获取到有效数据")

    print(f"\n{'=' * 80}")
    print("测试完成")
    print(f"{'=' * 80}")

if __name__ == "__main__":
    test_sina_api()
