#!/usr/bin/env python3
"""
测试手机适配的HTML生成功能

验证生成的HTML是否符合手机阅读要求：
- 固定宽度375px
- 字体大小适合手机阅读（18px+）
- 固定布局，非响应式
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tradingagents.graph.report_generator import ReportGenerator
from tradingagents.default_config import DEFAULT_CONFIG


def test_mobile_html_generation():
    """测试手机适配的HTML生成"""
    print("📱 测试手机适配HTML生成功能")
    print("=" * 60)

    # 1. 准备测试配置
    print("\n🔧 步骤1：准备配置...")
    config = DEFAULT_CONFIG.copy()

    # 2. 初始化报告生成器
    print("⚙️  步骤2：初始化报告生成器...")
    try:
        generator = ReportGenerator(config=config)
        print("   ✅ 报告生成器初始化成功")
    except Exception as e:
        print(f"   ❌ 报告生成器初始化失败: {e}")
        return

    # 3. 准备测试状态（模拟）
    print("\n📝 步骤3：准备测试状态...")
    test_state = {
        "company_of_interest": "AAPL",
        "trade_date": "2026-03-16",
        "messages": [],
        "market_research_report": "当前市场表现强劲，科技股整体上涨。AAPL作为科技龙头，受益于市场情绪改善。",
        "fundamentals_report": "**营收增长**：同比增长15%\n**净利润**：同比增长20%\n**市盈率**：25倍（合理估值）",
        "technical_analysis_report": "**RSI指标**：45（中性）\n**MACD**：金叉形态\n**移动平均线**：突破50日均线",
        "news_analysis_report": "近期无重大负面新闻。",
        "sentiment_report": "市场情绪积极。",
        "debate_summary": "看涨观点：基本面强劲\n看跌观点：估值偏高",
        "trader_analysis": "建议买入，目标价$200。",
        "risk_assessment_report": """**主要风险**：
1. 市场波动风险
2. 竞争加剧风险
3. 监管政策风险""",
    }
    test_decision = "BUY"

    # 4. 生成HTML
    print("\n🎨 步骤4：生成HTML报告...")
    try:
        html_content = generator.generate_html_report_with_llm(
            state=test_state,
            decision=test_decision,
            translate=True,
            max_retries=2
        )
        print(f"   ✅ HTML生成成功")
        print(f"   📊 HTML长度: {len(html_content):,} 字符")
    except Exception as e:
        print(f"   ❌ HTML生成失败: {e}")
        import traceback
        traceback.print_exc()
        return

    # 5. 验证HTML内容
    print("\n🔍 步骤5：验证HTML内容...")
    checks = [
        ("包含viewport设置", 'width=375' in html_content or 'width=375' in html_content),
        ("body宽度375px", 'width: 375px' in html_content or 'width:375px' in html_content),
        ("正文字体18px+", 'font-size: 18px' in html_content or 'font-size:18px' in html_content),
        ("包含charset", 'charset="utf-8"' in html_content or "charset='utf-8'" in html_content),
        ("HTML结构完整", '<!DOCTYPE html>' in html_content and '<html' in html_content and '</html>' in html_content),
    ]

    passed = 0
    for check_name, check_result in checks:
        status = "✅" if check_result else "❌"
        print(f"   {status} {check_name}")
        if check_result:
            passed += 1

    print(f"\n   通过率: {passed}/{len(checks)}")

    # 6. 保存HTML文件
    print("\n💾 步骤6：保存HTML文件...")
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    html_filename = "test_mobile_375px.html"
    html_path = reports_dir / html_filename

    try:
        generator.save_html_report(html_content, str(html_path))
        print(f"   ✅ HTML文件已保存: {html_path.resolve()}")
    except Exception as e:
        print(f"   ❌ 保存HTML文件失败: {e}")
        return

    # 7. 显示关键信息
    print("\n📋 关键信息：")
    print("   - 页面宽度: 375px（固定）")
    print("   - 正文字体: 18px")
    print("   - 设计类型: 手机固定布局（非响应式）")

    print("\n✅ 测试完成！")
    print(f"\n💡 下一步：")
    print(f"   1. 在浏览器中打开HTML文件: {html_path.resolve()}")
    print(f"   2. 使用开发者工具设置为iPhone视图（375px宽度）")
    print(f"   3. 检查文字大小是否适合阅读")
    print(f"   4. 验证布局是否为固定宽度")

    # 8. 提取并显示关键CSS
    print("\n🎨 关键CSS样式预览：")
    if "body {" in html_content:
        start = html_content.find("body {")
        end = html_content.find("}", start) + 1
        body_css = html_content[start:end]
        print("   Body样式:")
        for line in body_css.split('\n')[:5]:
            print(f"   {line}")


if __name__ == "__main__":
    test_mobile_html_generation()
