"""
使用 akshare 获取 A 股基本面数据

提供真实的 A 股基本面数据获取功能，包括：
- 公司基本信息
- 资产负债表
- 利润表
- 现金流量表
"""

import akshare as ak
import pandas as pd
import logging
from typing import Annotated, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def normalize_symbol(symbol: str) -> str:
    """标准化股票代码，移除 sh/sz 前缀

    Args:
        symbol: 股票代码（如 sh600900, sz000001）

    Returns:
        纯数字代码（如 600900, 000001）
    """
    return symbol.replace("sh", "").replace("sz", "").replace("SH", "").replace("SZ", "")


def get_akshare_fundamentals(
    ticker: Annotated[str, "股票代码（如 sh600900 或 sz000001）"],
    curr_date: Optional[str] = None
) -> str:
    """
    使用 akshare 获取公司基本面综合信息

    Args:
        ticker: 股票代码
        curr_date: 当前日期（可选，用于日志记录）

    Returns:
        str: Markdown 格式的公司基本面信息
    """
    logger.info(f"[API_CALL] akshare_fundamentals | symbol={ticker}")

    try:
        code = normalize_symbol(ticker)

        # 获取公司基本信息
        info_df = ak.stock_individual_info_em(symbol=code)

        # 获取最新行情数据
        try:
            spot_df = ak.stock_zh_a_spot_em()
            stock_data = spot_df[spot_df['代码'] == code]
            if not stock_data.empty:
                latest_price = stock_data.iloc[0]['最新价']
                market_cap = stock_data.iloc[0]['总市值']
                pe_ratio = stock_data.iloc[0]['市盈率-动态']
                pb_ratio = stock_data.iloc[0]['市净率']
            else:
                latest_price = market_cap = pe_ratio = pb_ratio = "N/A"
        except Exception as e:
            logger.warning(f"[API_WARNING] akshare | 获取行情数据失败: {e}")
            latest_price = market_cap = pe_ratio = pb_ratio = "N/A"

        # 构建 Markdown 格式的报告
        result = f"# {ticker.upper()} 基本面信息\n\n"

        # 基本信息
        result += "## 公司基本信息\n\n"
        result += "| 项目 | 内容 |\n"
        result += "|------|------|\n"

        for _, row in info_df.iterrows():
            item = row['item']
            value = row['value']
            result += f"| {item} | {value} |\n"

        # 市场数据
        result += f"\n## 市场数据（最新）\n\n"
        result += "| 指标 | 数值 |\n"
        result += "|------|------|\n"
        result += f"| 最新价 | {latest_price} |\n"
        result += f"| 总市值 | {market_cap} |\n"
        result += f"| 市盈率（动态） | {pe_ratio} |\n"
        result += f"| 市净率 | {pb_ratio} |\n"

        result += f"\n*数据来源：东方财富（akshare）*  \n"
        result += f"*获取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        logger.info(f"[API_SUCCESS] akshare_fundamentals | {ticker}")
        return result

    except Exception as e:
        logger.error(f"[API_ERROR] akshare_fundamentals | {ticker} | error={str(e)}")
        return f"Error getting fundamentals for {ticker}: {str(e)}"


def get_akshare_balance_sheet(
    ticker: Annotated[str, "股票代码（如 sh600900 或 sz000001）"],
    freq: Annotated[str, "报告频率：quarterly（季度）或 annual（年度）"] = "quarterly",
    curr_date: Optional[str] = None
) -> str:
    """
    使用 akshare 获取资产负债表数据

    Args:
        ticker: 股票代码
        freq: 报告频率（quarterly 或 annual）
        curr_date: 当前日期（可选）

    Returns:
        str: Markdown 格式的资产负债表
    """
    logger.info(f"[API_CALL] akshare_balance_sheet | symbol={ticker} | freq={freq}")

    try:
        code = normalize_symbol(ticker)

        # 使用 akshare 获取资产负债表数据
        # akshare 只有 stock_balance_sheet_by_report_em，没有 quarterly 专用函数
        df = ak.stock_balance_sheet_by_report_em(symbol=code)

        if df.empty:
            return f"No balance sheet data found for {ticker}"

        # 取最近 4 期数据
        df_recent = df.iloc[:, :5]  # 取前5列（报告期+最近4期数据）

        # 转置数据以便显示
        df_display = df_recent.T
        df_display.columns = df_display.iloc[0]  # 使用第一行作为列名
        df_display = df_display[1:]  # 移除第一行

        # 构建 Markdown 报告
        result = f"# {ticker.upper()} 资产负债表\n\n"
        result += f"## 报告频率: {freq}\n\n"
        result += df_display.to_markdown()

        result += f"\n*单位：元*  \n"
        result += f"*数据来源：东方财富（akshare）*  \n"
        result += f"*获取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        logger.info(f"[API_SUCCESS] akshare_balance_sheet | {ticker} | freq={freq}")
        return result

    except Exception as e:
        logger.error(f"[API_ERROR] akshare_balance_sheet | {ticker} | error={str(e)}")
        return f"Error getting balance sheet for {ticker}: {str(e)}"


def get_akshare_income_statement(
    ticker: Annotated[str, "股票代码（如 sh600900 或 sz000001）"],
    freq: Annotated[str, "报告频率：quarterly（季度）或 annual（年度）"] = "quarterly",
    curr_date: Optional[str] = None
) -> str:
    """
    使用 akshare 获取利润表数据

    Args:
        ticker: 股票代码
        freq: 报告频率（quarterly 或 annual）
        curr_date: 当前日期（可选）

    Returns:
        str: Markdown 格式的利润表
    """
    logger.info(f"[API_CALL] akshare_income_statement | symbol={ticker} | freq={freq}")

    try:
        code = normalize_symbol(ticker)

        # 使用 akshare 获取利润表数据
        df = ak.stock_profit_sheet_by_report_em(symbol=code)

        if df.empty:
            return f"No income statement data found for {ticker}"

        # 取最近 4 期数据
        df_recent = df.iloc[:, :5]

        # 转置数据以便显示
        df_display = df_recent.T
        df_display.columns = df_display.iloc[0]
        df_display = df_display[1:]

        # 构建 Markdown 报告
        result = f"# {ticker.upper()} 利润表\n\n"
        result += f"## 报告频率: {freq}\n\n"
        result += df_display.to_markdown()

        result += f"\n*单位：元*  \n"
        result += f"*数据来源：东方财富（akshare）*  \n"
        result += f"*获取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        logger.info(f"[API_SUCCESS] akshare_income_statement | {ticker} | freq={freq}")
        return result

    except Exception as e:
        logger.error(f"[API_ERROR] akshare_income_statement | {ticker} | error={str(e)}")
        return f"Error getting income statement for {ticker}: {str(e)}"


def get_akshare_cashflow(
    ticker: Annotated[str, "股票代码（如 sh600900 或 sz000001）"],
    freq: Annotated[str, "报告频率：quarterly（季度）或 annual（年度）"] = "quarterly",
    curr_date: Optional[str] = None
) -> str:
    """
    使用 akshare 获取现金流量表数据

    Args:
        ticker: 股票代码
        freq: 报告频率（quarterly 或 annual）
        curr_date: 当前日期（可选）

    Returns:
        str: Markdown 格式的现金流量表
    """
    logger.info(f"[API_CALL] akshare_cashflow | symbol={ticker} | freq={freq}")

    try:
        code = normalize_symbol(ticker)

        # 使用 akshare 获取现金流量表数据
        df = ak.stock_cash_flow_sheet_by_report_em(symbol=code)

        if df.empty:
            return f"No cash flow statement data found for {ticker}"

        # 取最近 4 期数据
        df_recent = df.iloc[:, :5]

        # 转置数据以便显示
        df_display = df_recent.T
        df_display.columns = df_display.iloc[0]
        df_display = df_display[1:]

        # 构建 Markdown 报告
        result = f"# {ticker.upper()} 现金流量表\n\n"
        result += f"## 报告频率: {freq}\n\n"
        result += df_display.to_markdown()

        result += f"\n*单位：元*  \n"
        result += f"*数据来源：东方财富（akshare）*  \n"
        result += f"*获取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        logger.info(f"[API_SUCCESS] akshare_cashflow | {ticker} | freq={freq}")
        return result

    except Exception as e:
        logger.error(f"[API_ERROR] akshare_cashflow | {ticker} | error={str(e)}")
        return f"Error getting cash flow statement for {ticker}: {str(e)}"
