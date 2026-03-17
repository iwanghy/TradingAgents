"""
调试新浪财经 API - 查看原始响应
"""

import requests
import json

def test_sina_api_raw():
    print("=" * 80)
    print("测试新浪财经 API - 原始响应调试")
    print("=" * 80)

    SINA_BASE_URL = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://finance.sina.com.cn/'
    }

    # 测试不同的参数组合
    test_cases = [
        {
            'name': '贵州茅台 (sh600519)',
            'params': {
                'symbol': 'sh600519',
                'scale': '240',
                'ma': 'no',
                'datalen': '50'
            }
        },
        {
            'name': '平安银行 (sz000001)',
            'params': {
                'symbol': 'sz000001',
                'scale': '240',
                'ma': 'no',
                'datalen': '50'
            }
        },
        {
            'name': '茅台小数据量',
            'params': {
                'symbol': 'sh600519',
                'scale': '240',
                'ma': 'no',
                'datalen': '10'
            }
        }
    ]

    for test in test_cases:
        print(f"\n{'=' * 80}")
        print(f"测试: {test['name']}")
        print(f"参数: {test['params']}")
        print(f"{'=' * 80}")

        try:
            response = requests.get(
                SINA_BASE_URL + "/CN_MarketData.getKLineData",
                params=test['params'],
                headers=headers,
                timeout=30
            )

            print(f"HTTP状态码: {response.status_code}")
            print(f"Content-Type: {response.headers.get('Content-Type')}")

            if response.status_code == 200:
                print(f"\n响应长度: {len(response.text)} 字符")
                print(f"\n原始响应 (前1000字符):")
                print(response.text[:1000])

                # 尝试解析JSON
                try:
                    data = response.json()
                    print(f"\n✅ JSON解析成功")
                    print(f"数据类型: {type(data)}")
                    print(f"数据长度: {len(data) if isinstance(data, list) else 'N/A'}")

                    if isinstance(data, list) and len(data) > 0:
                        print(f"\n第一条数据:")
                        print(json.dumps(data[0], ensure_ascii=False, indent=2))

                        if len(data) > 1:
                            print(f"\n最后一条数据:")
                            print(json.dumps(data[-1], ensure_ascii=False, indent=2))
                    else:
                        print(f"\n⚠️ 数据为空或格式异常")
                        print(f"完整响应: {data}")

                except json.JSONDecodeError as e:
                    print(f"\n❌ JSON解析失败: {e}")
                    print(f"响应内容: {response.text[:500]}")
            else:
                print(f"\n❌ HTTP错误: {response.status_code}")
                print(f"响应内容: {response.text[:500]}")

        except Exception as e:
            print(f"\n❌ 请求异常: {e}")

    print(f"\n{'=' * 80}")
    print("调试完成")
    print(f"{'=' * 80}")

if __name__ == "__main__":
    test_sina_api_raw()
