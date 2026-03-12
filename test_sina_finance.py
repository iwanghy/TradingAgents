#!/usr/bin/env python3
"""
使用新浪财经数据源的测试脚本

分析最近一个月的A股数据，避开 yfinance 速率限制
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 添加路径
sys.path.insert(0, '.')

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

def main():
    print("=" * 80)
    print("🚀 TradingAgents - 新浪财经数据源测试")
    print("=" * 80)
    
    # 加载环境变量
    load_dotenv()
    
    # 使用最近一个月的数据
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # 选择 A 股代码
    # sh600519 = 贵州茅台，sz000001 = 平安银行
    ticker = "sh600519"
    
    print(f"\n📊 配置:")
    print(f"  - 数据源: 新浪财经 (sina_finance)")
    print(f"  - 股票代码: {ticker} (贵州茅台)")
    print(f"  - 分析日期: {start_date} 到 {end_date}")
    print(f"  - 数据范围: 最近 30 天")
    print()
    
    # 配置 TradingAgentsGraph
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "zhipu"
    config["deep_think_llm"] = "glm-4.7"
    config["quick_think_llm"] = "glm-4.7"
    config["max_debate_rounds"] = 1
    config["max_llm_retries"] = 3
    config["debug"] = True
    
    # 数据源已经配置为使用新浪财经（在 default_config.py 中）
    print(f"⚙️  数据源配置:")
    print(f"  - core_stock_apis: {config['data_vendors']['core_stock_apis']}")
    print(f"  - technical_indicators: {config['data_vendors']['technical_indicators']}")
    print()
    
    # 创建 TradingAgentsGraph
    try:
        print("⏳ 初始化 TradingAgentsGraph...")
        ta = TradingAgentsGraph(debug=True, config=config)
        print("✅ 初始化成功")
        print()
        
        print(f"📈 开始分析 {ticker}...")
        print("-" * 80)
        
        # 执行分析
        final_state, decision = ta.propagate(ticker, end_date)
        
        print("-" * 80)
        print()
        print(f"✅ 分析完成！")
        print(f"📊 最终决策: {decision}")
        print()
        print("=" * 80)
        
    except Exception as e:
        print()
        print("-" * 80)
        print(f"❌ 分析失败: {str(e)}")
        print()
        print("故障排查:")
        print("  1. 检查是否正确设置了 ZHIPU_API_KEY")
        print("  2. 检查网络连接")
        print("  3. 查看日志了解详细错误信息")
        print("=" * 80)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
