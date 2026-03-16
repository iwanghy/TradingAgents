#!/usr/bin/env python3
"""
快速修复脚本：将新闻数据源切换到 AKShare

自动修改配置文件，启用 AKShare 作为新闻数据源
"""

import os
import sys
from pathlib import Path

def backup_file(filepath):
    """备份文件"""
    if os.path.exists(filepath):
        backup_path = f"{filepath}.backup"
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 已备份: {backup_path}")
        return True
    return False

def modify_default_config():
    """修改默认配置文件"""
    print("\n" + "="*70)
    print("步骤 1: 修改 default_config.py")
    print("="*70 + "\n")

    config_file = "tradingagents/default_config.py"

    if not os.path.exists(config_file):
        print(f"❌ 文件不存在: {config_file}")
        return False

    # 备份
    backup_file(config_file)

    # 读取文件
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 修改新闻数据源
    old_line = '"news_data": "yfinance",'
    new_line = '"news_data": "akshare",  # 改用 AKShare（中文财经新闻）'

    if old_line in content:
        content = content.replace(old_line, new_line)
        print("✅ 找到配置行，已修改为 AKShare")
    else:
        print("⚠️  未找到原配置行，尝试添加新配置")
        # 查找 data_vendors 配置块
        if '"data_vendors": {' in content:
            # 在 data_vendors 块中添加
            content = content.replace(
                '"data_vendors": {',
                '"data_vendors": {\n        "news_data": "akshare",  # 中文财经新闻'
            )
            print("✅ 已添加 AKShare 配置")
        else:
            print("❌ 无法找到 data_vendors 配置块")
            return False

    # 写回文件
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ 已修改: {config_file}\n")
    return True


def create_akshare_news_module():
    """创建 AKShare 新闻模块"""
    print("\n" + "="*70)
    print("步骤 2: 创建 AKShare 新闻模块")
    print("="*70 + "\n")

    module_file = "tradingagents/dataflows/akshare_news.py"

    # 如果文件已存在，跳过
    if os.path.exists(module_file):
        print(f"⚠️  文件已存在: {module_file}")
        print("   跳过创建\n")
        return True

    # 创建模块内容
    module_content = '''"""
AKShare 财经新闻数据获取模块

提供 A 股财经新闻、宏观经济新闻等数据获取功能
数据来源：东方财富网、百度股市通、财新网等
"""

import akshare as ak
import logging
import pandas as pd
from typing import Annotated
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def get_akshare_stock_news(
    symbol: Annotated[str, "A 股代码，如 600519"],
    limit: Annotated[int, "返回新闻条数"] = 20,
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
        Markdown 格式的新闻列表
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
    look_back_days: Annotated[int, "回溯天数"] = 7,
    limit: Annotated[int, "返回条数"] = 10,
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
'''

    # 写入文件
    with open(module_file, 'w', encoding='utf-8') as f:
        f.write(module_content)

    print(f"✅ 已创建: {module_file}\n")
    return True


def modify_interface():
    """修改 interface.py 添加路由"""
    print("\n" + "="*70)
    print("步骤 3: 修改 interface.py 添加路由")
    print("="*70 + "\n")

    interface_file = "tradingagents/dataflows/interface.py"

    if not os.path.exists(interface_file):
        print(f"❌ 文件不存在: {interface_file}")
        return False

    # 备份
    backup_file(interface_file)

    # 读取文件
    with open(interface_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 添加导入（如果还没有）
    if 'from .akshare_news import' not in content:
        # 查找导入部分
        import_section = "from .yfinance_news import"
        if import_section in content:
            new_import = '''from .akshare_news import (
    get_akshare_stock_news,
    get_akshare_global_news
)
from .yfinance_news import'''
            content = content.replace(import_section, new_import)
            print("✅ 已添加 AKShare 导入")
        else:
            print("⚠️  未找到合适的导入位置")

    # 添加到 VENDOR_FUNCTIONS（简化处理，提供手动指导）
    print("\n⚠️  需要手动添加路由配置")
    print("   请在 interface.py 的 VENDOR_FUNCTIONS 中添加:")
    print('''
    "get_news": {
        "akshare": lambda ticker, start, end: get_akshare_stock_news(ticker, limit=20),
        # ... 保留其他配置
    },
    ''')

    # 写回文件
    with open(interface_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ 已修改导入部分: {interface_file}\n")
    return True


def test_akshare_installation():
    """测试 AKShare 是否安装"""
    print("\n" + "="*70)
    print("步骤 0: 检查 AKShare 安装")
    print("="*70 + "\n")

    try:
        import akshare as ak
        print(f"✅ AKShare 已安装")
        print(f"   版本: {ak.__version__}")
        print(f"   GitHub: https://github.com/akfamily/akshare\n")
        return True
    except ImportError:
        print("❌ AKShare 未安装")
        print("\n请运行以下命令安装:")
        print("   pip install akshare --upgrade\n")
        return False


def main():
    """主函数"""
    print("\n" + "="*70)
    print("🚀 TradingAgents 新闻数据源迁移到 AKShare")
    print("="*70)
    print("\n此脚本将:")
    print("1. 检查 AKShare 安装")
    print("2. 修改 default_config.py 配置")
    print("3. 创建 akshare_news.py 模块")
    print("4. 修改 interface.py 路由")
    print("="*70)

    # 检查安装
    if not test_akshare_installation():
        print("\n⚠️  请先安装 AKShare，然后重新运行此脚本")
        return 1

    # 执行修改
    success = True

    success &= modify_default_config()
    success &= create_akshare_news_module()
    success &= modify_interface()

    # 汇总
    print("\n" + "="*70)
    print("✅ 配置完成！")
    print("="*70 + "\n")

    print("后续步骤:")
    print("1. 运行测试:")
    print("   python test_akshare_news.py\n")
    print("2. 运行完整测试:")
    print("   python test_glm.py\n")
    print("3. 查看生成的报告:")
    print("   ls -lh reports/\n")

    print("\n预期效果:")
    print("✅ 新闻分析师可以获取中文财经新闻")
    print("✅ 不再受 yfinance 限流影响")
    print("✅ 分析报告包含中文新闻内容\n")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
