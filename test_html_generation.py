#!/usr/bin/env python3
"""
HTML报告生成功能测试脚本

使用mock数据进行端到端HTML报告生成测试
"""

import os
from datetime import datetime
from tradingagents.graph.report_generator import ReportGenerator
from tradingagents.default_config import DEFAULT_CONFIG

def create_mock_state():
    """创建模拟的分析状态数据"""
    return {
        "company_of_interest": "AAPL",
        "trade_date": "2026-03-16",
        "market_report": "Market analysis shows strong performance with positive indicators. The technology sector has been performing well overall.",
        "sentiment_report": "Sentiment analysis indicates positive market sentiment towards the stock with strong social media presence.",
        "news_report": "Recent news coverage has been predominantly positive, with several analysts upgrading their price targets.",
        "fundamentals_report": "Company fundamentals remain strong with solid revenue growth and healthy profit margins.",
        "technical_report": "Technical indicators suggest bullish momentum with upward trend continuing.",
        "investment_debate_state": {
            "history": "Bullish arguments emphasize strong growth potential while bearish arguments caution about valuation concerns.",
            "judge_decision": "After considering both perspectives, the investment team leans towards positive outlook with moderate risk."
        },
        "trader_investment_plan": "The trader recommends a position size based on risk management guidelines and market conditions.",
        "risk_debate_state": {
            "history": "Risk discussion includes volatility assessment, market timing concerns, and position sizing considerations.",
            "judge_decision": "Overall risk level is assessed as moderate with appropriate risk mitigation strategies in place."
        },
        "final_trade_decision": "Based on comprehensive analysis, the final recommendation is to proceed with the investment decision."
    }

def test_html_generation():
    """测试HTML报告生成功能"""
    print("="*60)
    print("🧪 HTML报告生成功能测试")
    print("="*60)
    
    # 创建配置（禁用真实API调用，使用mock模式）
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "mock"  # 使用mock提供商避免API调用
    
    # 创建模拟状态
    mock_state = create_mock_state()
    decision = "BUY"  # 测试买入决策
    
    print(f"\n📊 测试配置:")
    print(f"  - 股票代码: {mock_state['company_of_interest']}")
    print(f"  - 分析日期: {mock_state['trade_date']}")
    print(f"  - 交易决策: {decision}")
    print(f"  - 使用mock数据: 是")
    
    try:
        # 初始化报告生成器
        print(f"\n🚀 初始化报告生成器...")
        generator = ReportGenerator(config)
        
        # 生成HTML报告
        print(f"\n📝 生成HTML报告...")
        html_content = generator.generate_html_report_with_llm(
            state=mock_state,
            decision=decision,
            translate=True
        )
        
        # 验证HTML内容
        print(f"\n✅ HTML报告生成完成!")
        print(f"   内容长度: {len(html_content)} 字符")
        
        # 检查基本HTML结构
        checks = [
            ("DOCTYPE声明", "<!DOCTYPE html>" in html_content),
            ("HTML标签", "<html" in html_content and "</html>" in html_content),
            ("head标签", "<head>" in html_content and "</head>" in html_content),
            ("body标签", "<body>" in html_content and "</body>" in html_content),
            ("黑色背景", "#000000" in html_content or "background-color: black" in html_content),
            ("决策内容", decision in html_content),
            ("免责声明", "免责声明" in html_content),
            ("股票代码", mock_state["company_of_interest"] in html_content)
        ]
        
        print(f"\n🔍 HTML内容验证:")
        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"   {status} {check_name}: {'通过' if passed else '失败'}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print(f"\n🎉 所有基本检查通过!")
        else:
            print(f"\n⚠️ 部分检查未通过，但继续测试...")
        
        # 保存HTML文件
        html_filename = f"test_{mock_state['company_of_interest']}_{mock_state['trade_date']}_中文报告.html"
        html_path = f"reports/{html_filename}"
        
        print(f"\n💾 保存HTML文件...")
        generator.save_html_report(html_content, html_path)
        print(f"   文件路径: {html_path}")
        
        # 验证文件存在
        if os.path.exists(html_path):
            file_size = os.path.getsize(html_path)
            print(f"   ✅ 文件存在，大小: {file_size} 字节")
            return html_path, html_content
        else:
            print(f"   ❌ 文件保存失败")
            return None, None
            
    except Exception as e:
        print(f"\n❌ HTML生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    test_html_generation()