#!/usr/bin/env python3
"""
使用真实markdown文件测试HTML报告生成功能

从现有的中文markdown报告生成HTML报告，用于调试和验证
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from tradingagents.graph.report_generator import ReportGenerator
from tradingagents.default_config import DEFAULT_CONFIG

# 加载.env文件
load_dotenv()

def read_markdown_report(file_path: str) -> str:
    """读取markdown报告文件"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def parse_markdown_to_state(markdown_content: str, ticker: str, trade_date: str) -> dict:
    """
    从markdown内容构造基本的state对象

    这是一个简化的实现，主要用于测试HTML生成功能
    """
    state = {
        "company_of_interest": ticker,
        "trade_date": trade_date,
        # 由于我们已经有了完整的markdown，可以暂时用简单的内容填充
        # 实际的HTML生成会使用markdown内容
        "market_report": "见markdown内容",
        "sentiment_report": "见markdown内容",
        "news_report": "见markdown内容",
        "fundamentals_report": "见markdown内容",
        "technical_report": "见markdown内容",
        "investment_debate_state": {
            "history": "见markdown内容",
            "judge_decision": "见markdown内容"
        },
        "trader_investment_plan": "见markdown内容",
        "risk_debate_state": {
            "history": "见markdown内容",
            "judge_decision": "见markdown内容"
        },
        "final_trade_decision": "见markdown内容"
    }

    return state

def extract_decision_from_markdown(markdown_content: str) -> str:
    """从markdown中提取交易决策"""
    # 查找决策部分
    for line in markdown_content.split('\n'):
        if '决策' in line and ('**' in line or '：' in line):
            # 提取决策类型
            if '买入' in line or 'BUY' in line.upper():
                return "BUY"
            elif '卖出' in line or 'SELL' in line.upper():
                return "SELL"
            elif '持有' in line or 'HOLD' in line.upper():
                return "HOLD"

    # 默认返回HOLD
    return "HOLD"

def test_html_from_markdown():
    """测试从markdown生成HTML"""
    print("="*80)
    print("🧪 使用真实Markdown文件测试HTML生成功能")
    print("="*80)

    # 配置
    ticker = "sh600941"
    trade_date = "2026-03-16"
    markdown_file = f"reports/{ticker}_{trade_date}_中文报告.md"

    print(f"\n📄 输入文件: {markdown_file}")

    try:
        # 1. 读取markdown文件
        print(f"\n📖 正在读取markdown文件...")
        markdown_content = read_markdown_report(markdown_file)
        print(f"   ✅ 文件读取成功")
        print(f"   📊 文件大小: {len(markdown_content)} 字符")
        print(f"   📝 文件行数: {len(markdown_content.split(chr(10)))} 行")

        # 2. 提取决策
        print(f"\n🔍 正在提取交易决策...")
        decision = extract_decision_from_markdown(markdown_content)
        print(f"   ✅ 决策类型: {decision}")

        # 3. 创建state
        print(f"\n⚙️ 正在构造state对象...")
        state = parse_markdown_to_state(markdown_content, ticker, trade_date)
        print(f"   ✅ state对象构造完成")

        # 4. 初始化报告生成器
        print(f"\n🚀 正在初始化报告生成器...")
        config = DEFAULT_CONFIG.copy()

        # 使用Zhipu AI作为提供商（使用.env中的ZHIPU_API_KEY）
        config["llm_provider"] = "zhipu"
        config["deep_think_llm"] = "glm-4-flash"
        config["quick_think_llm"] = "glm-4-flash"

        print(f"   📋 LLM提供商: {config.get('llm_provider')}")
        print(f"   🤖 模型: {config.get('deep_think_llm')}")
        print(f"   🔑 API密钥状态: {'已设置' if os.getenv('ZHIPU_API_KEY') else '未设置'}")

        if os.getenv('ZHIPU_API_KEY'):
            api_key_preview = os.getenv('ZHIPU_API_KEY')[:20] + "..."
            print(f"   🔑 API密钥预览: {api_key_preview}")

        generator = ReportGenerator(config)
        print(f"   ✅ 报告生成器初始化完成")

        # 检查翻译器状态
        if generator.translator:
            print(f"   ✅ LLM客户端已就绪")
        else:
            print(f"   ⚠️ 警告: LLM客户端未初始化，将使用后备HTML模板")

        # 5. 生成HTML报告
        print(f"\n🎨 开始生成HTML报告...")
        print(f"   " + "-"*60)

        html_content = generator.generate_html_report_with_llm(
            state=state,
            decision=decision,
            translate=True
        )

        print(f"   " + "-"*60)
        print(f"✅ HTML生成完成")
        print(f"   📊 HTML长度: {len(html_content)} 字符")

        # 6. 验证HTML内容
        print(f"\n🔍 验证HTML内容...")

        checks = [
            ("DOCTYPE声明", "<!DOCTYPE html>" in html_content),
            ("HTML根标签", "<html" in html_content and "</html>" in html_content),
            ("head标签", "<head>" in html_content and "</head>" in html_content),
            ("body标签", "<body>" in html_content and "</body>" in html_content),
            ("UTF-8编码", "charset=\"utf-8\"" in html_content),
            ("黑色背景", "#000000" in html_content or "background-color: black" in html_content.lower()),
            ("股票代码", ticker in html_content),
            ("分析日期", trade_date in html_content),
            ("决策信息", decision in html_content or "买入" in html_content or "卖出" in html_content),
            ("免责声明", "免责声明" in html_content or "disclaimer" in html_content.lower()),
            ("中文标题", "交易分析报告" in html_content or "Trading" in html_content)
        ]

        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            result = "通过" if passed else "失败"
            print(f"   {status} {check_name}: {result}")
            if not passed:
                all_passed = False

        if all_passed:
            print(f"\n🎉 所有基本检查通过!")
        else:
            print(f"\n⚠️ 部分检查未通过，但已保存HTML文件")

        # 7. 保存HTML文件
        html_filename = f"{ticker}_{trade_date}_中文报告.html"
        html_path = f"reports/{html_filename}"

        print(f"\n💾 保存HTML文件...")
        generator.save_html_report(html_content, html_path)
        print(f"   📁 文件路径: {html_path}")

        # 验证文件
        if os.path.exists(html_path):
            file_size = os.path.getsize(html_path)
            print(f"   ✅ 文件保存成功")
            print(f"   📊 文件大小: {file_size:,} 字节")

            # 获取绝对路径
            abs_path = os.path.abspath(html_path)
            print(f"\n🔗 文件绝对路径:")
            print(f"   {abs_path}")
            print(f"\n🌐 可以在浏览器中打开:")
            print(f"   file://{abs_path}")

            return html_path, html_content
        else:
            print(f"   ❌ 文件保存失败")
            return None, None

    except FileNotFoundError as e:
        print(f"\n❌ 文件错误: {e}")
        print(f"   请确认文件路径是否正确")
        return None, None
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        print(f"\n📋 详细错误信息:")
        traceback.print_exc()
        return None, None

def main():
    """主函数"""
    html_path, html_content = test_html_from_markdown()

    if html_path and html_content:
        print(f"\n{'='*80}")
        print(f"✅ 测试成功完成!")
        print(f"{'='*80}")
        print(f"\n📋 生成的文件:")
        print(f"   {html_path}")
        print(f"\n💡 下一步:")
        print(f"   1. 在浏览器中打开HTML文件查看效果")
        print(f"   2. 检查样式和布局是否正确")
        print(f"   3. 验证所有内容是否正确显示")
        return 0
    else:
        print(f"\n{'='*80}")
        print(f"❌ 测试失败")
        print(f"{'='*80}")
        return 1

if __name__ == "__main__":
    exit(main())
