#!/usr/bin/env python3
"""
使用真实markdown内容生成HTML报告

从现有的中文markdown报告提取各个章节内容，生成完整的HTML报告
"""

import os
import re
from pathlib import Path
from dotenv import load_dotenv
from tradingagents.graph.report_generator import ReportGenerator
from tradingagents.default_config import DEFAULT_CONFIG

# 加载.env文件
load_dotenv()

def parse_markdown_sections(markdown_content: str) -> dict:
    """
    从markdown内容中提取各个章节

    Args:
        markdown_content: markdown报告内容

    Returns:
        包含各个章节内容的字典
    """
    sections = {}

    # 定义章节标题模式
    section_patterns = {
        "market": r"## 🌍 市场分析\s*\n(.*?)(?=##\s|$)",
        "sentiment": r"## 💬 情绪分析\s*\n(.*?)(?=##\s|$)",
        "news": r"## 📰 新闻分析\s*\n(.*?)(?=##\s|$)",
        "fundamentals": r"## 💰 基本面分析\s*\n(.*?)(?=##\s|$)",
        "technical": r"## 📈 技术分析\s*\n(.*?)(?=##\s|$)",
        "debate": r"## 🤔 投资辩论\s*\n(.*?)(?=## 👔|$)",
        "trader": r"## 👔 交易员分析\s*\n(.*?)(?=## ⚠️|$)",
        "risk": r"## ⚠️ 风险评估\s*\n(.*?)(?=## 📝|$)",
        "final_decision": r"## 📝 决策详情\s*\n(.*?)(?=## ⚠️ 免责声明|$)"
    }

    for key, pattern in section_patterns.items():
        match = re.search(pattern, markdown_content, re.DOTALL)
        if match:
            content = match.group(1).strip()
            # 移除子章节标题（如果有）
            content = re.sub(r'###.*?\n', '', content)
            sections[key] = content
        else:
            sections[key] = ""

    return sections

def create_state_from_markdown(markdown_content: str, ticker: str, trade_date: str) -> dict:
    """
    从markdown内容创建完整的state对象

    Args:
        markdown_content: markdown报告内容
        ticker: 股票代码
        trade_date: 分析日期

    Returns:
        完整的state字典
    """
    sections = parse_markdown_sections(markdown_content)

    state = {
        "company_of_interest": ticker,
        "trade_date": trade_date,
        "market_report": sections.get("market", ""),
        "sentiment_report": sections.get("sentiment", ""),
        "news_report": sections.get("news", ""),
        "fundamentals_report": sections.get("fundamentals", ""),
        "technical_report": sections.get("technical", ""),
        "investment_debate_state": {
            "history": sections.get("debate", ""),
            "judge_decision": ""
        },
        "trader_investment_plan": sections.get("trader", ""),
        "risk_debate_state": {
            "history": sections.get("risk", ""),
            "judge_decision": ""
        },
        "final_trade_decision": sections.get("final_decision", "")
    }

    return state

def extract_decision_from_markdown(markdown_content: str) -> str:
    """从markdown中提取交易决策"""
    # 查找决策部分
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

    # 备用方案：搜索关键词
    for line in markdown_content.split('\n'):
        if '决策' in line and ('**' in line or '：' in line):
            if '买入' in line or 'BUY' in line.upper():
                return "BUY"
            elif '卖出' in line or 'SELL' in line.upper():
                return "SELL"
            elif '持有' in line or 'HOLD' in line.upper():
                return "HOLD"

    return "HOLD"

def test_html_with_real_content():
    """使用真实markdown内容生成HTML"""
    print("="*80)
    print("🧪 使用真实Markdown内容生成HTML报告")
    print("="*80)

    # 配置
    ticker = "sh600941"
    trade_date = "2026-03-16"
    markdown_file = f"reports/{ticker}_{trade_date}_中文报告.md"

    print(f"\n📄 输入文件: {markdown_file}")

    try:
        # 1. 读取markdown文件
        print(f"\n📖 正在读取markdown文件...")
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        print(f"   ✅ 文件读取成功")
        print(f"   📊 文件大小: {len(markdown_content)} 字符")

        # 2. 提取决策
        print(f"\n🔍 正在提取交易决策...")
        decision = extract_decision_from_markdown(markdown_content)
        print(f"   ✅ 决策类型: {decision}")

        # 3. 解析markdown内容
        print(f"\n📋 正在解析markdown章节...")
        sections = parse_markdown_sections(markdown_content)
        print(f"   ✅ 成功提取 {len([s for s in sections.values() if s])} 个有效章节")

        # 显示提取的章节
        for key, content in sections.items():
            status = "✅" if content else "⚠️"
            length = f"{len(content)} 字符" if content else "空"
            print(f"      {status} {key}: {length}")

        # 4. 创建完整的state对象
        print(f"\n⚙️ 正在构造完整state对象...")
        state = create_state_from_markdown(markdown_content, ticker, trade_date)
        print(f"   ✅ state对象构造完成")

        # 5. 初始化报告生成器
        print(f"\n🚀 正在初始化报告生成器...")
        config = DEFAULT_CONFIG.copy()

        # 使用Zhipu AI作为提供商
        config["llm_provider"] = "zhipu"
        config["deep_think_llm"] = "glm-4-flash"
        config["quick_think_llm"] = "glm-4-flash"

        print(f"   📋 LLM提供商: {config.get('llm_provider')}")
        print(f"   🤖 模型: {config.get('deep_think_llm')}")
        print(f"   🔑 API密钥状态: {'已设置' if os.getenv('ZHIPU_API_KEY') else '未设置'}")

        generator = ReportGenerator(config)
        print(f"   ✅ 报告生成器初始化完成")

        if not generator.translator:
            print(f"   ⚠️ 警告: LLM客户端未初始化，将使用后备HTML模板")
            return None, None

        # 6. 生成HTML报告
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

        # 7. 验证HTML内容
        print(f"\n🔍 验证HTML内容...")
        checks = [
            ("DOCTYPE声明", "<!DOCTYPE html>" in html_content),
            ("HTML根标签", "<html" in html_content and "</html>" in html_content),
            ("head标签", "<head>" in html_content and "</head>" in html_content),
            ("body标签", "<body>" in html_content and "</body>" in html_content),
            ("UTF-8编码", "charset=\"utf-8\"" in html_content),
            ("黑色背景", "#000000" in html_content),
            ("股票代码", ticker in html_content),
            ("决策信息", decision in html_content or "买入" in html_content or "卖出" in html_content),
            ("免责声明", "免责声明" in html_content),
            ("中文标题", "交易分析报告" in html_content),
            # 检查是否包含真实内容
            ("市场分析", "市场分析" in html_content),
            ("基本面分析", "基本面" in html_content),
            ("新闻分析", "新闻" in html_content),
            ("情绪分析", "情绪" in html_content)
        ]

        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            result = "通过" if passed else "失败"
            print(f"   {status} {check_name}: {result}")
            if not passed:
                all_passed = False

        # 8. 保存HTML文件
        html_filename = f"{ticker}_{trade_date}_中文报告.html"
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
    html_path, html_content = test_html_with_real_content()

    if html_path and html_content:
        print(f"\n{'='*80}")
        print(f"✅ HTML报告生成成功!")
        print(f"{'='*80}")
        print(f"\n📋 生成的文件:")
        print(f"   {html_path}")
        print(f"\n💡 下一步:")
        print(f"   1. 在浏览器中打开HTML文件查看效果")
        print(f"   2. 检查样式和布局是否正确")
        print(f"   3. 验证所有内容是否正确显示")
        print(f"   4. 检查是否包含真实的markdown内容")
        return 0
    else:
        print(f"\n{'='*80}")
        print(f"❌ HTML生成失败")
        print(f"{'='*80}")
        return 1

if __name__ == "__main__":
    exit(main())
