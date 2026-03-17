"""
新浪财经数据获取模块

提供从新浪财经获取股票数据的功能，作为 yfinance 的替代方案
"""

import requests
import pandas as pd
import logging
import time
from datetime import datetime
from typing import Annotated, Optional

try:
    import baostock as bs
    BAOSTOCK_AVAILABLE = True
except ImportError:
    BAOSTOCK_AVAILABLE = False

logger = logging.getLogger(__name__)

# 新浪财经 API 配置
SINA_BASE_URL = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php"
SINA_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://finance.sina.com.cn/'
}


def get_sina_data_online(
    symbol: Annotated[str, "股票代码（中国股市格式，如 sh600519 或 sz000001）"],
    start_date: Annotated[str, "开始日期 yyyy-mm-dd 格式"],
    end_date: Annotated[str, "结束日期 yyyy-mm-dd 格式"],
    scale: int = 240,  # 240=日线, 60=60分钟, 30=30分钟, 15=15分钟, 5=5分钟
) -> str:
    """
    从新浪财经获取股票历史数据
    
    Args:
        symbol: 股票代码（sh6位数字 或 sz6位数字）
        start_date: 开始日期
        end_date: 结束日期
        scale: 数据周期（默认240=日线）
    
    Returns:
        str: CSV 格式的股票数据，或错误消息
    """
    
    logger.info(f"[API_CALL] sina | symbol={symbol} | start={start_date} | end={end_date}")
    start_time = time.time()
    
    try:
        # 验证日期格式
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
        
        # 计算需要的数据条数（近似计算：交易日约为总天数的 70%）
        from datetime import timedelta
        delta = timedelta(days=30)  # 默认获取 30 天数据
        if start_date and end_date:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            delta = end - start
        
        datalen = max(10, int(delta.days * 0.7))  # 至少 10 条
        
        # 新浪财经 API 调用
        params = {
            'symbol': symbol,
            'scale': str(scale),
            'ma': 'no',
            'datalen': str(datalen)
        }
        
        logger.debug(f"[SINA] Requesting {datalen} records from {SINA_BASE_URL}")
        
        response = requests.get(
            SINA_BASE_URL + "/CN_MarketData.getKLineData",
            params=params,
            headers=SINA_HEADERS,
            timeout=30
        )
        
        duration = time.time() - start_time
        
        if response.status_code != 200:
            logger.error(f"[API_ERROR] sina | HTTP {response.status_code} | duration={duration:.2f}s")
            return f"Error: HTTP {response.status_code} from Sina Finance"
        
        # 解析 JSON 响应
        try:
            data = response.json()
        except ValueError:
            logger.error(f"[API_ERROR] sina | Invalid JSON response | duration={duration:.2f}s")
            return f"Error: Invalid JSON response from Sina Finance"
        
        # 检查数据
        if not isinstance(data, list) or len(data) == 0:
            logger.warning(f"[API_EMPTY] sina | No data found for {symbol}")
            return f"No data found for symbol '{symbol}' between {start_date} and {end_date}"
        
        # 转换为 DataFrame
        df_data = []
        for item in reversed(data):  # 新浪返回的数据是倒序的，需要反转
            try:
                df_data.append({
                    'Date': item['day'],
                    'Open': float(item['open']),
                    'High': float(item['high']),
                    'Low': float(item['low']),
                    'Close': float(item['close']),
                    'Adj Close': float(item['close']),  # 新浪没有复权价，使用收盘价
                    'Volume': int(item['volume'])
                })
            except (KeyError, ValueError) as e:
                logger.warning(f"[SINA] Skipping invalid data item: {e}")
                continue
        
        if not df_data:
            logger.warning(f"[API_EMPTY] sina | No valid data items")
            return f"No valid data found for symbol '{symbol}'"
        
        # 创建 DataFrame
        df = pd.DataFrame(df_data)
        df.set_index('Date', inplace=True)
        
        # 过滤日期范围
        df.index = pd.to_datetime(df.index)
        mask = (df.index >= start_date) & (df.index <= end_date)
        df = df[mask]
        
        if df.empty:
            logger.warning(f"[API_EMPTY] sina | No data in date range for {symbol}")
            return f"No data found for symbol '{symbol}' between {start_date} and {end_date}"
        
        # 转换为 CSV 格式（与 yfinance 格式一致）
        csv_string = df.to_csv()
        
        # 添加 header
        header = f"# Stock data for {symbol.upper()} from {start_date} to {end_date} (Sina Finance)\n"
        header += f"# Total records: {len(df)}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        logger.info(f"[API_SUCCESS] sina | {symbol} | records={len(df)} | duration={duration:.2f}s")
        
        return header + csv_string
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"[API_ERROR] sina | symbol={symbol} | error_type={type(e).__name__} | error={str(e)} | duration={duration:.2f}s")
        raise


def convert_symbol_to_sina_format(symbol: str) -> str:
    """
    将股票代码转换为新浪财经格式
    
    Args:
        symbol: 股票代码（如 AAPL, 600519, 000001）
    
    Returns:
        str: 新浪财经格式的股票代码（sh600519, sz000001）
    """
    symbol = symbol.upper().strip()
    
    # 已经是新浪格式
    if symbol.startswith(('SH', 'SZ')):
        return symbol.lower()
    
    # 纯数字，中国股票
    if symbol.isdigit():
        if len(symbol) == 6:
            # 6 位数字，判断上海或深圳
            if symbol.startswith('6'):
                return f"sh{symbol}"
            else:
                return f"sz{symbol}"
    
    # 美股或其他市场
    # 暂时返回原样，后续可以添加映射逻辑
    return symbol


def _get_baostock_financial_data(
    ticker: str,
    data_type: str,
    freq: str = "quarterly"
) -> Optional[str]:
    """
    使用 baostock 获取真实财务数据
    
    Args:
        ticker: 股票代码（如 sh600519 或 sz000001）
        data_type: 数据类型 ('profit', 'balance', 'cash_flow', 'growth', 'operation')
        freq: 报告频率（暂只支持 quarterly）
    
    Returns:
        Optional[str]: Markdown 格式的财务表格，失败返回 None
    """
    if not BAOSTOCK_AVAILABLE:
        logger.warning(f"[BAOSTOCK] baostock not available, skipping financial data fetch")
        return None
    
    # 支持的数据类型映射到 baostock API
    api_map = {
        'profit': bs.query_profit_data,
        'balance': bs.query_balance_data,
        'cash_flow': bs.query_cash_flow_data,
        'growth': bs.query_growth_data,
        'operation': bs.query_operation_data,
    }
    
    if data_type not in api_map:
        logger.error(f"[BAOSTOCK] Unsupported data_type: {data_type}")
        return None
    
    query_func = api_map[data_type]
    
    try:
        # 登录 baostock
        lg = bs.login()
        if lg.error_code != '0':
            logger.error(f"[BAOSTOCK] Login failed: {lg.error_msg}")
            return None
        
        # 转换股票代码格式：sh600519 -> sh.600519
        symbol = ticker.lower()
        if symbol.startswith('sh') or symbol.startswith('sz'):
            baostock_code = f"{symbol[:2]}.{symbol[2:]}"
        else:
            logger.error(f"[BAOSTOCK] Invalid ticker format: {ticker}")
            bs.logout()
            return None
        
        # 获取最近 4 个季度的数据
        # 如果当前年 Q3 没有数据，使用上一年
        from datetime import datetime
        current_year = datetime.now().year
        
        # 先尝试当前年 Q3，如果无数据则使用上一年
        test_rs = query_func(code=baostock_code, year=current_year, quarter=3)
        has_current_year_data = False
        while (test_rs.error_code == '0') & test_rs.next():
            has_current_year_data = True
            break
        
        if has_current_year_data:
            quarters = [
                (current_year, 3),
                (current_year, 2),
                (current_year, 1),
                (current_year - 1, 4),
            ]
        else:
            # 当前年无数据，使用上一年
            quarters = [
                (current_year - 1, 4),
                (current_year - 1, 3),
                (current_year - 1, 2),
                (current_year - 1, 1),
            ]
        
        # 收集数据
        all_data = []
        for year, quarter in quarters:
            rs = query_func(code=baostock_code, year=year, quarter=quarter)
            if rs.error_code != '0':
                logger.warning(f"[BAOSTOCK] Query failed for {year}-Q{quarter}: {rs.error_msg}")
                continue
            
            # 获取第一行数据
            while (rs.next()):
                row_data = rs.get_row_data()
                all_data.append({
                    'period': f"{year}Q{quarter}",
                    'data': row_data
                })
                break  # 只取第一行
        
        # 登出
        bs.logout()
        
        if not all_data:
            logger.warning(f"[BAOSTOCK] No data found for {ticker} ({data_type})")
            return None
        
        # 构建 Markdown 表格
        fields = rs.fields  # 列名
        
        # 表头
        header_row = "| 项目 | " + " | ".join([item['period'] for item in all_data]) + " |"
        separator_row = "|" + "|".join(["------" for _ in range(len(all_data) + 1)]) + "|"
        
        # 数据行
        data_rows = []
        for i, field in enumerate(fields):
            row_cells = [field]
            for item in all_data:
                row_cells.append(item['data'][i])
            data_rows.append("| " + " | ".join(row_cells) + " |")
        
        markdown_table = "\n".join([header_row, separator_row] + data_rows)
        
        # 添加标题
        data_type_map = {
            'profit': '利润表',
            'balance': '资产负债表',
            'cash_flow': '现金流量表',
            'growth': '成长能力指标',
            'operation': '营运能力指标',
        }
        
        title = f"# {ticker.upper()} {data_type_map.get(data_type, data_type)}（来自 baostock）\n\n"
        result = title + markdown_table
        
        logger.info(f"[BAOSTOCK_SUCCESS] {ticker} | {data_type} | records={len(all_data)}")
        return result
        
    except Exception as e:
        logger.error(f"[BAOSTOCK_ERROR] {ticker} | {data_type} | error={str(e)}")
        try:
            bs.logout()
        except:
            pass
        return None


def get_sina_fundamentals(
    ticker: Annotated[str, "股票代码（如 sh600519 或 sz000001）"],
    curr_date: Optional[str] = None
) -> str:
    """
    获取公司基本面信息和财务摘要

    使用baostock获取真实数据，如果不可用则返回错误提示

    Args:
        ticker: 股票代码
        curr_date: 当前日期（可选）

    Returns:
        str: Markdown格式的公司基本面信息
    """
    logger.info(f"[API_CALL] sina_fundamentals | symbol={ticker}")

    try:
        symbol = convert_symbol_to_sina_format(ticker)

        # Try baostock first for profit data
        result = _get_baostock_financial_data(symbol, 'profit', freq='quarterly')
        if result:
            logger.info(f"[API_SUCCESS] sina_fundamentals | {symbol} | from baostock")
            return result

        logger.warning(f"[API_UNAVAILABLE] sina_fundamentals | {symbol} | no data available")
        return (
            f"⚠️ 无法获取 {ticker} 的基本面数据\n"
            f"   原因：数据源暂无该股票的财务数据\n"
            f"   建议：\n"
            f"   - 确认股票代码是否正确\n"
            f"   - 尝试使用其他数据源（如 akshare_fundamentals）\n"
            f"   - 检查该股票是否已上市"
        )

    except Exception as e:
        logger.error(f"[API_ERROR] sina_fundamentals | {ticker} | error={str(e)}")
        return f"Error getting fundamentals for {ticker}: {str(e)}"


def get_sina_balance_sheet(
    ticker: Annotated[str, "股票代码（如 sh600519 或 sz000001）"],
    freq: Annotated[str, "报告频率：quarterly（季度）或 annual（年度）"] = "quarterly",
    curr_date: Optional[str] = None
) -> str:
    """
    获取资产负债表数据

    使用baostock获取真实数据，如果不可用则返回错误提示

    Args:
        ticker: 股票代码
        freq: 报告频率（quarterly或annual）
        curr_date: 当前日期（可选）

    Returns:
        str: Markdown格式的资产负债表或错误提示
    """
    logger.info(f"[API_CALL] sina_balance_sheet | symbol={ticker} | freq={freq}")

    try:
        symbol = convert_symbol_to_sina_format(ticker)

        # Try baostock first for balance data
        result = _get_baostock_financial_data(symbol, 'balance', freq=freq)
        if result:
            logger.info(f"[API_SUCCESS] sina_balance_sheet | {symbol} | from baostock")
            return result

        logger.warning(f"[API_UNAVAILABLE] sina_balance_sheet | {symbol} | no data available")
        return (
            f"⚠️ 无法获取 {ticker} 的资产负债表数据\n"
            f"   原因：数据源暂无该股票的财务数据\n"
            f"   报告频率：{freq}\n"
            f"   建议：\n"
            f"   - 确认股票代码是否正确\n"
            f"   - 尝试使用其他数据源（如 akshare_fundamentals）\n"
            f"   - 检查该股票是否已上市"
        )

    except Exception as e:
        logger.error(f"[API_ERROR] sina_balance_sheet | {ticker} | error={str(e)}")
        return f"Error getting balance sheet for {ticker}: {str(e)}"


def get_sina_income_statement(
    ticker: Annotated[str, "股票代码（如 sh600519 或 sz000001）"],
    freq: Annotated[str, "报告频率：quarterly（季度）或 annual（年度）"] = "quarterly",
    curr_date: Optional[str] = None
) -> str:
    """
    获取利润表数据

    使用baostock获取真实数据，如果不可用则返回错误提示

    Args:
        ticker: 股票代码
        freq: 报告频率（quarterly或annual）
        curr_date: 当前日期（可选）

    Returns:
        str: Markdown格式的利润表或错误提示
    """
    logger.info(f"[API_CALL] sina_income_statement | symbol={ticker} | freq={freq}")

    try:
        symbol = convert_symbol_to_sina_format(ticker)

        # Try baostock first for profit data
        result = _get_baostock_financial_data(symbol, 'profit', freq=freq)
        if result:
            logger.info(f"[API_SUCCESS] sina_income_statement | {symbol} | from baostock")
            return result

        logger.warning(f"[API_UNAVAILABLE] sina_income_statement | {symbol} | no data available")
        return (
            f"⚠️ 无法获取 {ticker} 的利润表数据\n"
            f"   原因：数据源暂无该股票的财务数据\n"
            f"   报告频率：{freq}\n"
            f"   建议：\n"
            f"   - 确认股票代码是否正确\n"
            f"   - 尝试使用其他数据源（如 akshare_fundamentals）\n"
            f"   - 检查该股票是否已上市"
        )

    except Exception as e:
        logger.error(f"[API_ERROR] sina_income_statement | {ticker} | error={str(e)}")
        return f"Error getting income statement for {ticker}: {str(e)}"


def get_sina_cashflow(
    ticker: Annotated[str, "股票代码（如 sh600519 或 sz000001）"],
    freq: Annotated[str, "报告频率：quarterly（季度）或 annual（年度）"] = "quarterly",
    curr_date: Optional[str] = None
) -> str:
    """
    获取现金流量表数据

    使用baostock获取真实数据，如果不可用则返回错误提示

    Args:
        ticker: 股票代码
        freq: 报告频率（quarterly或annual）
        curr_date: 当前日期（可选）

    Returns:
        str: Markdown格式的现金流量表或错误提示
    """
    logger.info(f"[API_CALL] sina_cashflow | symbol={ticker} | freq={freq}")

    try:
        symbol = convert_symbol_to_sina_format(ticker)

        # Try baostock first for cash_flow data
        result = _get_baostock_financial_data(symbol, 'cash_flow', freq=freq)
        if result:
            logger.info(f"[API_SUCCESS] sina_cashflow | {symbol} | from baostock")
            return result

        logger.warning(f"[API_UNAVAILABLE] sina_cashflow | {symbol} | no data available")
        return (
            f"⚠️ 无法获取 {ticker} 的现金流量表数据\n"
            f"   原因：数据源暂无该股票的财务数据\n"
            f"   报告频率：{freq}\n"
            f"   建议：\n"
            f"   - 确认股票代码是否正确\n"
            f"   - 尝试使用其他数据源（如 akshare_fundamentals）\n"
            f"   - 检查该股票是否已上市"
        )

    except Exception as e:
        logger.error(f"[API_ERROR] sina_cashflow | {ticker} | error={str(e)}")
        return f"Error getting cashflow statement for {ticker}: {str(e)}"


# 测试函数
if __name__ == "__main__":
    print("=" * 80)
    print("测试新浪财经数据获取")
    print("=" * 80)

    # 测试代码转换
    test_symbols = ["AAPL", "600519", "000001", "sh600519"]
    print("\n股票代码转换:")
    for sym in test_symbols:
        converted = convert_symbol_to_sina_format(sym)
        print(f"  {sym} -> {converted}")

    print("\n获取历史数据测试:")
    print("-" * 80)

    # 测试获取贵州茅台数据
    symbol = "sh600519"
    result = get_sina_data_online(symbol, "2024-01-01", "2024-01-15")

    print(result[:500])
    print("\n" + "=" * 80)
