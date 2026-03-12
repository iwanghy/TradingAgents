#!/usr/bin/env python3
"""
GLM 4.7 快速测试脚本
 
使用智谱 AI GLM 4.7 模型分析 A 股的示例
"""

# 【重要】在导入 yfinance 之前设置环境变量，禁用 curl_cffi
# 这可以解决 OpenSSL 版本不兼容导致的 TLS 错误
import os
os.environ['YFINANCE_NO_CURL'] = '1'

from datetime import datetime, timedelta
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv

def main():
    # 加载环境变量
    load_dotenv()

    # 检查 API Key
    if not os.environ.get("ZHIPU_API_KEY"):
        print("❌ 错误: 未找到 ZHIPU_API_KEY")
        print("\n请在 .env 文件中设置:")
        print("ZHIPU_API_KEY=your-api-key-here")
        print("\n获取 API Key: https://open.bigmodel.cn/")
        return

    print("="*60)
    print("🚀 TradingAgents - GLM 4.7 股票分析")
    print("="*60)

    # 配置使用 GLM 4.7
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "zhipu"
    config["deep_think_llm"] = "glm-4.5-air"
    config["quick_think_llm"] = "glm-4.5-air"
    config["max_debate_rounds"] = 1
    config["max_llm_retries"] = 3  # 自动重试 3 次，处理 API 限流  # 快速分析

    print(f"\n📊 配置:")
    print(f"  - 提供商: {config['llm_provider']}")
    print(f"  - 主模型: {config['deep_think_llm']}")
    print(f"  - 快速模型: {config['quick_think_llm']}")
    print(f"  - 辩论轮数: {config['max_debate_rounds']}")
    print(f"  - 数据源: {config['data_vendors']['core_stock_apis']}（新浪财经）")
 
    # 选择 A 股典型股票（贵州茅台）
    ticker = "sh600519"  # 贵州茅台
    from datetime import datetime, timedelta
    trade_date = datetime.now().strftime('%Y-%m-%d')  # 使用当前日期

    print(f"\n📈 分析目标:")
    print(f"  - 股票: {ticker} (贵州茅台)")
    print(f"  - 日期: {trade_date} (最近数据)")
    print(f"  - 数据源: 新浪财经（避开 yfinance 速率限制）")
    print(f"  - 分析范围: 最近 30 天")

    print(f"\n⏳ 开始分析...")
    print("-"*60)

    # 初始化并运行
    try:
        ta = TradingAgentsGraph(debug=True, config=config)
        state, decision = ta.propagate(ticker, trade_date)

        print("-"*60)
        print("\n✅ 分析完成!")
        print("\n" + "="*60)
        print("📊 最终决策")
        print("="*60)
        print(f"\n{decision}\n")
        print("="*60)

        print("\n💡 提示:")
        print("  - 这是快速分析（1 轮辩论）")
        print("  - 使用新浪财经数据源分析 A 股")
        print("  - 数据范围：最近 30 天（新浪财经限制）")
        print("  - 如需深度分析，设置 max_debate_rounds=2 或 3")
        print("  - 如需分析其他 A 股，修改 ticker 代码（如 sz000001 平安银行）")

    except Exception as e:
        print(f"\n❌ 分析失败: {e}")
        print("\n故障排查:")
        print("  1. 检查 API Key 是否正确")
        print("  2. 检查账户余额是否充足")
        print("  3. 查看详细文档: GLM_4.7_使用指南.md")

if __name__ == "__main__":
    main()
