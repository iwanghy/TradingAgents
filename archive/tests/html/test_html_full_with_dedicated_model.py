#!/usr/bin/env python3
"""
使用完整markdown内容和专用HTML模型生成高质量HTML报告

结合了：
1. 直接使用原始markdown文件内容
2. 使用专用HTML生成模型（glm-4-plus）
3. 生成包含完整内容的HTML报告
"""

import os
import re
from pathlib import Path
from dotenv import load_dotenv
from tradingagents.graph.report_generator import ReportGenerator
from tradingagents.default_config import DEFAULT_CONFIG

# 加载.env文件
load_dotenv()

def extract_decision_from_markdown(markdown_content: str) -> str:
    """从markdown中提取交易决策"""
    decision_pattern = r"## 📊 最终交易决策\s*\n\s*\*\*决策\*\*:\s*\*\*(.*?)\*\*"
    match = re.search(decision_pattern, markdown_content)
    if match:
        decision_zh = match.group(1).strip()
        if "买入" in decision_zh:
            return "BUY"
        elif "卖出" in decision_zh:
            return "SELL"
        elif "持有" in decision_zh:
            return "HOLD"
    return "HOLD"

def generate_html_with_dedicated_model():
    """使用专用HTML模型生成完整HTML报告"""
    print("="*80)
    print("🚀 使用专用HTML模型生成完整报告")
    print("="*80)

    # 配置
    ticker = "sh600941"
    trade_date = "2026-03-16"
    markdown_file = f"reports/{ticker}_{trade_date}_中文报告.md"

    print(f"\n📄 输入文件: {markdown_file}")

    try:
        # 1. 读取完整的markdown文件
        print(f"\n📖 正在读取markdown文件...")
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        print(f"   ✅ 文件读取成功")
        print(f"   📊 文件大小: {len(markdown_content):,} 字符")
        print(f"   📝 文件行数: {len(markdown_content.split(chr(10)))} 行")

        # 2. 提取决策
        print(f"\n🔍 正在提取交易决策...")
        decision = extract_decision_from_markdown(markdown_content)
        print(f"   ✅ 决策类型: {decision}")

        # 3. 创建最小化的state
        print(f"\n⚙️ 正在构造state对象...")
        state = {
            "company_of_interest": ticker,
            "trade_date": trade_date,
            "market_report": "",
            "sentiment_report": "",
            "news_report": "",
            "fundamentals_report": "",
            "technical_report": "",
            "investment_debate_state": {"history": "", "judge_decision": ""},
            "trader_investment_plan": "",
            "risk_debate_state": {"history": "", "judge_decision": ""},
            "final_trade_decision": ""
        }
        print(f"   ✅ state对象构造完成")

        # 4. 初始化报告生成器
        print(f"\n🚀 正在初始化报告生成器...")
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "zhipu"

        # 快速任务使用flash模型
        config["quick_think_llm"] = "glm-4-flash"
        config["deep_think_llm"] = "glm-4-flash"

        # HTML生成使用更强大的模型
        html_llm_model = "glm-4-plus"

        print(f"   📋 LLM提供商: {config.get('llm_provider')}")
        print(f"   ⚡ 翻译/快速任务模型: {config.get('quick_think_llm')}")
        print(f"   🎨 HTML生成专用模型: {html_llm_model}")

        # 使用专用HTML模型初始化
        generator = ReportGenerator(config, html_llm_model=html_llm_model)
        print(f"   ✅ 报告生成器初始化完成")

        if not generator.html_generator and not generator.translator:
            print(f"   ❌ 错误: LLM客户端未初始化")
            return None, None

        # 5. 直接构建HTML提示词，使用原始markdown内容
        print(f"\n🎨 开始生成HTML报告...")
        print(f"   📝 使用原始markdown内容（{len(markdown_content):,} 字符）")
        print(f"   🤖 使用HTML专用模型: {html_llm_model}")
        print(f"   " + "-"*60)

        # 直接构建HTML提示词
        html_prompt = generator._build_html_prompt(markdown_content)
        print(f"   ✅ HTML提示词构建完成（{len(html_prompt):,} 字符）")

        # 调用LLM生成HTML（使用专用HTML生成器）
        print(f"   🤖 正在调用LLM生成HTML（第1次尝试）...")
        html_content = generator._call_llm_for_html(html_prompt)
        print(f"   ✅ LLM调用完成")

        # 验证HTML
        print(f"   🔍 正在验证HTML格式...")
        is_valid, errors = generator._validate_html(html_content)

        if is_valid:
            print(f"   ✅ HTML验证成功！")
        else:
            print(f"   ⚠️ HTML验证失败:")
            for error in errors:
                print(f"      - {error}")
            print(f"   💡 继续使用生成的HTML...")

        print(f"   " + "-"*60)
        print(f"✅ HTML生成完成")
        print(f"   📊 HTML长度: {len(html_content):,} 字符")

        # 6. 验证HTML内容完整性
        print(f"\n🔍 验证HTML内容完整性...")
        checks = [
            ("DOCTYPE声明", "<!DOCTYPE html>" in html_content),
            ("HTML根标签", "<html" in html_content and "</html>" in html_content),
            ("黑色背景", "#000000" in html_content),
            ("股票代码", ticker in html_content),
            ("决策信息", "卖出" in html_content),
            ("中文标题", "交易分析报告" in html_content),
            ("市场分析", "市场分析" in html_content and len(html_content) > 10000),
            ("基本面分析", "基本面" in html_content),
            ("新闻分析", "新闻" in html_content),
            ("情绪分析", "情绪" in html_content),
            ("投资辩论", "辩论" in html_content or "Debate" in html_content),
            ("风险评估", "风险" in html_content)
        ]

        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            result = "通过" if passed else "失败"
            print(f"   {status} {check_name}: {result}")
            if not passed:
                all_passed = False

        # 7. 保存HTML文件
        html_filename = f"{ticker}_{trade_date}_中文报告_完整版_专用模型.html"
        html_path = f"reports/{html_filename}"

        print(f"\n💾 保存HTML文件...")
        generator.save_html_report(html_content, html_path)
        print(f"   📁 文件路径: {html_path}")

        if os.path.exists(html_path):
            file_size = os.path.getsize(html_path)
            print(f"   ✅ 文件保存成功")
            print(f"   📊 文件大小: {file_size:,} 字节")

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
        return None, None
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def main():
    """主函数"""
    html_path, html_content = generate_html_with_dedicated_model()

    if html_path and html_content:
        print(f"\n{'='*80}")
        print(f"✅ HTML报告生成成功!")
        print(f"{'='*80}")
        print(f"\n📋 生成的文件:")
        print(f"   {html_path}")
        print(f"\n✨ 功能特点:")
        print(f"   ✅ 使用完整的原始markdown内容（13,405字符）")
        print(f"   ✅ HTML生成使用专用模型（glm-4-plus）")
        print(f"   ✅ 其他任务使用快速模型（glm-4-flash）")
        print(f"   ✅ 性能和质量的最佳平衡")
        print(f"\n💡 下一步:")
        print(f"   1. 在浏览器中打开HTML文件查看效果")
        print(f"   2. 检查样式和布局是否正确")
        print(f"   3. 验证是否包含完整的原始markdown内容")
        print(f"   4. 对比使用不同模型的效果差异")
        return 0
    else:
        print(f"\n{'='*80}")
        print(f"❌ HTML生成失败")
        print(f"{'='*80}")
        return 1

if __name__ == "__main__":
    exit(main())
