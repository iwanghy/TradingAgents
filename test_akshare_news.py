#!/usr/bin/env python3
"""
AKShare 中文财经新闻获取测试脚本

测试 AKShare 的新闻功能，验证其作为 yfinance 替代方案的可行性
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import sys

def print_section(title):
    """打印分节标题"""
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70 + "\n")

def test_akshare_news():
    """测试 AKShare 新闻功能"""

    print_section("AKShare 中文财经新闻功能测试")

    results = {}

    # 测试1: 东方财富个股新闻
    print("1️⃣  测试: 东方财富个股新闻")
    try:
        symbol = "600519"  # 贵州茅台
        news_df = ak.stock_news_em(symbol=symbol)

        if news_df is not None and len(news_df) > 0:
            print(f"✅ 成功获取 {len(news_df)} 条新闻")
            print(f"   列名: {list(news_df.columns)}")

            # 显示前3条新闻标题
            print("\n   最新新闻:")
            for idx, row in news_df.head(3).iterrows():
                title = row.get('新闻标题', 'N/A')
                source = row.get('发布时间', 'N/A')
                print(f"   • {title[:60]}... ({source})")

            results['stock_news_em'] = True
        else:
            print("❌ 未获取到新闻")
            results['stock_news_em'] = False

    except Exception as e:
        print(f"❌ 失败: {e}")
        results['stock_news_em'] = False

    # 测试2: 财新网新闻
    print("\n2️⃣  测试: 财新网新闻")
    try:
        cx_news = ak.stock_news_main_cx()

        if cx_news is not None and len(cx_news) > 0:
            print(f"✅ 成功获取 {len(cx_news)} 条新闻")
            print(f"   列名: {list(cx_news.columns)}")

            # 显示前3条
            print("\n   财新新闻:")
            for idx, row in cx_news.head(3).iterrows():
                summary = row.get('summary', 'N/A')
                print(f"   • {summary[:80]}...")

            results['stock_news_main_cx'] = True
        else:
            print("❌ 未获取到新闻")
            results['stock_news_main_cx'] = False

    except Exception as e:
        print(f"❌ 失败: {e}")
        results['stock_news_main_cx'] = False

    # 测试3: CCTV新闻联播
    print("\n3️⃣  测试: CCTV新闻联播")
    try:
        date_str = "20240424"
        cctv_news = ak.news_cctv(date=date_str)

        if cctv_news is not None and len(cctv_news) > 0:
            print(f"✅ 成功获取 {len(cctv_news)} 条新闻")
            print(f"   列名: {list(cctv_news.columns)}")

            results['news_cctv'] = True
        else:
            print("❌ 未获取到新闻")
            results['news_cctv'] = False

    except Exception as e:
        print(f"❌ 失败: {e}")
        results['news_cctv'] = False

    # 测试4: 百度经济数据
    print("\n4️⃣  测试: 百度经济日历")
    try:
        date_str = "20251126"
        economic_data = ak.news_economic_baidu(date=date_str)

        if economic_data is not None and len(economic_data) > 0:
            print(f"✅ 成功获取 {len(economic_data)} 条数据")
            print(f"   列名: {list(economic_data.columns)}")

            results['news_economic_baidu'] = True
        else:
            print("❌ 未获取到数据")
            results['news_economic_baidu'] = False

    except Exception as e:
        print(f"❌ 失败: {e}")
        results['news_economic_baidu'] = False

    # 汇总结果
    print_section("测试结果汇总")

    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    print(f"通过: {success_count}/{total_count}\n")

    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {test_name:25s}: {status}")

    # 判断是否适合作为替代方案
    print_section("评估结论")

    if results.get('stock_news_em'):
        print("✅ AKShare 的东方财富新闻功能正常")
        print("✅ 可以作为 yfinance 的替代方案")
        print("\n建议:")
        print("  1. 主要使用 stock_news_em() 获取个股新闻")
        print("  2. 补充使用 stock_news_main_cx() 获取财新深度分析")
        print("  3. 配合使用其他数据源构建完整的新闻分析系统")
        return True
    else:
        print("❌ AKShare 新闻功能测试失败")
        print("⚠️  需要进一步调查或寻找其他替代方案")
        return False


def generate_integration_example():
    """生成集成示例代码"""

    print_section("TradingAgents 集成示例代码")

    code_example = '''
# ============================================================
# AKShare 新闻模块集成示例
# 文件: tradingagents/dataflows/akshare_news.py
# ============================================================

import akshare as ak
from langchain_core.tools import tool
from typing import Annotated
import logging
import pandas as pd

logger = logging.getLogger(__name__)

@tool
def get_akshare_stock_news(
    symbol: Annotated[str, "A股代码，如 600519"],
    limit: Annotated[int, "返回新闻条数", "可选"] = 20,
) -> str:
    """
    使用 AKShare 获取 A 股财经新闻（东方财富网数据源）

    数据来源：东方财富网
    更新频率：实时更新
    数据范围：最近 100 条新闻

    Args:
        symbol: A 股代码（6 位数字）
        limit: 返回新闻条数（最多 100 条）

    Returns:
        Markdown 格式的新闻列表，包含标题、来源、时间、摘要和链接

    Examples:
        >>> news = get_akshare_stock_news("600519", limit=10)
        >>> print(news)
    """
    try:
        logger.info(f"[AKSHARE] 获取股票 {symbol} 新闻")

        # 获取新闻数据
        df = ak.stock_news_em(symbol=symbol)

        if df is None or len(df) == 0:
            return f"⚠️ 未找到股票 {symbol} 的新闻"

        # 限制返回条数
        if len(df) > limit:
            df = df.head(limit)

        # 构建 Markdown 报告
        news_md = f"## {symbol} 最新财经新闻\\n\\n"
        news_md += f"**数据来源**: 东方财富网 via AKShare\\n"
        news_md += f"**更新时间**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\\n"
        news_md += f"**新闻数量**: {len(df)} 条\\n\\n"

        news_md += "---\\n\\n"

        for idx, row in df.iterrows():
            # 新闻标题
            title = row.get('新闻标题', 'N/A')
            news_md += f"### {title}\\n\\n"

            # 元数据
            source = row.get('文章来源', '东方财富网')
            publish_time = row.get('发布时间', 'N/A')
            news_md += f"**来源**: {source}\\n"
            news_md += f"**时间**: {publish_time}\\n\\n"

            # 新闻摘要
            content = row.get('新闻内容', '')
            if content:
                # 限制摘要长度
                summary = content[:300] if len(content) > 300 else content
                news_md += f"{summary}...\\n\\n"

            # 文章链接
            link = row.get('文章链接', '')
            if link:
                news_md += f"**链接**: {link}\\n\\n"

            news_md += "---\\n\\n"

        logger.info(f"[AKSHARE] 成功获取 {len(df)} 条新闻")
        return news_md

    except Exception as e:
        error_msg = f"获取新闻失败: {str(e)}"
        logger.error(f"[AKSHARE_ERROR] {error_msg}")
        return error_msg


@tool
def get_akshare_global_news(
    curr_date: Annotated[str, "当前日期，格式 YYYYMMDD"],
    look_back_days: Annotated[int, "回溯天数", "可选"] = 7,
    limit: Annotated[int, "返回条数", "可选"] = 10,
) -> str:
    """
    获取全球宏观经济新闻（百度股市通数据源）

    数据来源：百度股市通
    更新频率：每日更新

    Args:
        curr_date: 当前日期（格式 YYYYMMDD）
        look_back_days: 回溯天数
        limit: 返回条数

    Returns:
        Markdown 格式的经济新闻列表
    """
    try:
        logger.info(f"[AKSHARE] 获取 {curr_date} 经济日历")

        # 获取经济数据
        df = ak.news_economic_baidu(date=curr_date)

        if df is None or len(df) == 0:
            return "⚠️ 未找到该日期的经济数据"

        # 限制返回条数
        if len(df) > limit:
            df = df.head(limit)

        # 构建 Markdown 报告
        news_md = f"## 全球宏观经济新闻\\n\\n"
        news_md += f"**数据来源**: 百度股市通\\n"
        news_md += f"**日期**: {curr_date}\\n"
        news_md += f"**数据数量**: {len(df)} 条\\n\\n"

        for idx, row in df.iterrows():
            news_md += f"### {row.get('名称', 'N/A')}\\n\\n"
            news_md += f"**时间**: {row.get('日期', 'N/A')}\\n"
            news_md += f"**重要性**: {row.get('重要性', 'N/A')}\\n\\n"
            news_md += f"**前值**: {row.get('前值', 'N/A')}\\n"
            news_md += f"**预期**: {row.get('预期', 'N/A')}\\n"
            news_md += f"**公布值**: {row.get('公布值', 'N/A')}\\n\\n"
            news_md += "---\\n\\n"

        return news_md

    except Exception as e:
        error_msg = f"获取经济新闻失败: {str(e)}"
        logger.error(f"[AKSHARE_ERROR] {error_msg}")
        return error_msg


# ============================================================
# 配置路由（在 interface.py 中添加）
# ============================================================

# 在 tradingagents/dataflows/interface.py 中：

VENDOR_FUNCTIONS = {
    # ... 现有配置 ...

    "get_news": {
        "akshare": lambda ticker, start, end: get_akshare_stock_news(ticker, limit=20),
        "yfinance": get_news_yfinance,  # 保留作为 fallback
        "alpha_vantage": get_news_alpha_vantage,
    },

    "get_global_news": {
        "akshare": lambda curr_date, days, limit: get_akshare_global_news(curr_date, limit=10),
        "yfinance": get_global_news_yfinance,
        "alpha_vantage": get_global_news_alpha_vantage,
    },
}

# ============================================================
# 配置默认数据源（在 default_config.py 中修改）
# ============================================================

DEFAULT_CONFIG = {
    "data_vendors": {
        "news_data": "akshare",  # 改为 akshare
        # ... 其他配置 ...
    },
}
'''

    print(code_example)


def main():
    """主函数"""
    print("\n🔍 AKShare 中文财经新闻测试")
    print("测试时间:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("目标: 验证 AKShare 作为新闻数据源的可行性\n")

    # 运行测试
    success = test_akshare_news()

    # 生成集成示例
    generate_integration_example()

    # 最终建议
    print_section("实施建议")

    if success:
        print("✅ **AKShare 可以作为新闻数据源**\n")
        print("立即执行以下步骤:\n")
        print("1. 安装 AKShare（如果未安装）:")
        print("   pip install akshare --upgrade\n")
        print("2. 在 default_config.py 中修改配置:")
        print('   config["data_vendors"]["news_data"] = "akshare"\n')
        print("3. 运行测试验证:")
        print("   python test_akshare_news.py\n")
        print("4. 运行完整测试:")
        print("   python test_glm.py\n")
        print("\n预期结果:")
        print("  - 新闻分析师可以获取中文财经新闻")
        print("  - 不再受 yfinance 限流影响")
        print("  - 分析报告包含中文新闻内容")
    else:
        print("❌ **需要进一步调查**\n")
        print("建议:")
        print("1. 检查网络连接")
        print("2. 查看 AKShare 官方文档")
        print("3. 考虑使用 Alpha Vantage 作为替代")
        print("4. 实现多数据源 fallback 机制")

    print("\n" + "="*70)
    print("测试完成")
    print("="*70 + "\n")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
