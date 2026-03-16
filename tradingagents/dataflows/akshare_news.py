"""AKShare-based Chinese financial news fetching functions.

This module provides tools for fetching Chinese financial news using AKShare,
which serves as an alternative to yfinance for A-share market news.
"""

import logging
from datetime import datetime
from typing import Annotated

import akshare as ak
import pandas as pd

logger = logging.getLogger(__name__)


def get_akshare_stock_news(
    symbol: Annotated[str, "A股代码，如 600519"],
    limit: Annotated[int, "返回新闻条数"] = 20,
) -> str:
    """使用 AKShare 获取 A 股财经新闻（东方财富网数据源）。

    数据来源：东方财富网
    更新频率：实时更新
    数据范围：最近 100 条新闻

    Args:
        symbol: A 股代码（6 位数字）
        limit: 返回新闻条数（最多 100 条，默认 20）

    Returns:
        Markdown 格式的新闻列表，包含标题、来源、时间、摘要和链接

    Examples:
        >>> news = get_akshare_stock_news("600519", limit=10)
        >>> print(news)
    """
    try:
        logger.info(f"[AKSHARE] 获取股票 {symbol} 新闻")

        df = ak.stock_news_em(symbol=symbol)

        if df is None or len(df) == 0:
            return f"⚠️ 未找到股票 {symbol} 的新闻"

        if len(df) > limit:
            df = df.head(limit)

        news_md = f"## {symbol} 最新财经新闻\n\n"
        news_md += f"**数据来源**: 东方财富网 via AKShare\n"
        news_md += f"**更新时间**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        news_md += f"**新闻数量**: {len(df)} 条\n\n"

        news_md += "---\n\n"

        for idx, row in df.iterrows():
            title = row.get('新闻标题', 'N/A')
            news_md += f"### {title}\n\n"

            source = row.get('文章来源', '东方财富网')
            publish_time = row.get('发布时间', 'N/A')
            news_md += f"**来源**: {source}\n"
            news_md += f"**时间**: {publish_time}\n\n"

            content = row.get('新闻内容', '')
            if content:
                summary = content[:300] if len(content) > 300 else content
                news_md += f"{summary}...\n\n"

            link = row.get('文章链接', '')
            if link:
                news_md += f"**链接**: {link}\n\n"

            news_md += "---\n\n"

        logger.info(f"[AKSHARE] 成功获取 {len(df)} 条新闻")
        return news_md

    except Exception as e:
        error_msg = f"获取新闻失败: {str(e)}"
        logger.error(f"[AKSHARE_ERROR] {error_msg}")
        return error_msg


def get_akshare_global_news(
    curr_date: Annotated[str, "当前日期，格式 YYYYMMDD"],
    look_back_days: Annotated[int, "回溯天数"] = 7,
    limit: Annotated[int, "返回条数"] = 10,
) -> str:
    """获取全球宏观经济新闻（百度股市通数据源）。

    数据来源：百度股市通
    更新频率：每日更新

    Args:
        curr_date: 当前日期（格式 YYYYMMDD）
        look_back_days: 回溯天数（默认 7）
        limit: 返回条数（默认 10）

    Returns:
        Markdown 格式的经济新闻列表

    Examples:
        >>> news = get_akshare_global_news("20240424", look_back_days=7)
        >>> print(news)
    """
    try:
        logger.info(f"[AKSHARE] 获取 {curr_date} 经济日历")

        df = ak.news_economic_baidu(date=curr_date)

        if df is None or len(df) == 0:
            return "⚠️ 未找到该日期的经济数据"

        if len(df) > limit:
            df = df.head(limit)

        news_md = f"## 全球宏观经济新闻\n\n"
        news_md += f"**数据来源**: 百度股市通\n"
        news_md += f"**日期**: {curr_date}\n"
        news_md += f"**数据数量**: {len(df)} 条\n\n"

        for idx, row in df.iterrows():
            news_md += f"### {row.get('名称', 'N/A')}\n\n"
            news_md += f"**时间**: {row.get('日期', 'N/A')}\n"
            news_md += f"**重要性**: {row.get('重要性', 'N/A')}\n\n"
            news_md += f"**前值**: {row.get('前值', 'N/A')}\n"
            news_md += f"**预期**: {row.get('预期', 'N/A')}\n"
            news_md += f"**公布值**: {row.get('公布值', 'N/A')}\n\n"
            news_md += "---\n\n"

        return news_md

    except Exception as e:
        error_msg = f"获取经济新闻失败: {str(e)}"
        logger.error(f"[AKSHARE_ERROR] {error_msg}")
        return error_msg
