from langchain_core.tools import tool
from typing import Annotated
import logging
from tradingagents.dataflows.interface import route_to_vendor

logger = logging.getLogger(__name__)

@tool
def get_stock_data(
    symbol: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """
    Retrieve stock price data (OHLCV) for a given ticker symbol.
    Uses the configured core_stock_apis vendor.
    Args:
        symbol (str): Ticker symbol of the company, e.g. AAPL, TSM
        start_date (str): Start date in yyyy-mm-dd format
        end_date (str): End date in yyyy-mm-dd format
    Returns:
        str: A formatted dataframe containing the stock price data for the specified ticker symbol in the specified date range.
    """
    logger.info(f"[TOOL_ENTRY] get_stock_data | symbol={symbol} start={start_date} end={end_date}")
    
    try:
        result = route_to_vendor("get_stock_data", symbol, start_date, end_date)
        logger.info(f"[TOOL_SUCCESS] get_stock_data | symbol={symbol}")
        return result
    except Exception as e:
        logger.error(f"[TOOL_ERROR] get_stock_data | symbol={symbol} | error={str(e)}")
        raise
