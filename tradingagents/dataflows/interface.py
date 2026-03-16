from typing import Annotated
import logging

# Import from vendor-specific modules
from .y_finance import (
    get_YFin_data_online,
    get_stock_stats_indicators_window,
    get_fundamentals as get_yfinance_fundamentals,
    get_balance_sheet as get_yfinance_balance_sheet,
    get_cashflow as get_yfinance_cashflow,
    get_income_statement as get_yfinance_income_statement,
    get_insider_transactions as get_yfinance_insider_transactions,
)
from .yfinance_news import get_news_yfinance, get_global_news_yfinance
from .akshare_news import get_akshare_stock_news, get_akshare_global_news
from .alpha_vantage import (
    get_stock as get_alpha_vantage_stock,
    get_indicator as get_alpha_vantage_indicator,
    get_fundamentals as get_alpha_vantage_fundamentals,
    get_balance_sheet as get_alpha_vantage_balance_sheet,
    get_cashflow as get_alpha_vantage_cashflow,
    get_income_statement as get_alpha_vantage_income_statement,
    get_insider_transactions as get_alpha_vantage_insider_transactions,
    get_news as get_alpha_vantage_news,
    get_global_news as get_alpha_vantage_global_news,
)
from .alpha_vantage_common import AlphaVantageRateLimitError

# Import yfinance exceptions
try:
    from yfinance.exceptions import YFRateLimitError
except ImportError:
    # yfinance not installed or older version
    YFRateLimitError = None

# Import Sina Finance module
try:
    from .sina_finance import (
        get_sina_data_online,
        get_sina_fundamentals,
        get_sina_balance_sheet,
        get_sina_income_statement,
        get_sina_cashflow,
    )
except ImportError:
    # sina_finance module not available
    get_sina_data_online = None
    get_sina_fundamentals = None
    get_sina_balance_sheet = None
    get_sina_income_statement = None
    get_sina_cashflow = None

# Configuration and routing logic
from .config import get_config

# Tools organized by category
TOOLS_CATEGORIES = {
    "core_stock_apis": {
        "description": "OHLCV stock price data",
        "tools": [
            "get_stock_data"
        ]
    },
    "technical_indicators": {
        "description": "Technical analysis indicators",
        "tools": [
            "get_indicators"
        ]
    },
    "fundamental_data": {
        "description": "Company fundamentals",
        "tools": [
            "get_fundamentals",
            "get_balance_sheet",
            "get_cashflow",
            "get_income_statement"
        ]
    },
    "news_data": {
        "description": "News and insider data",
        "tools": [
            "get_news",
            "get_global_news",
            "get_insider_transactions",
        ]
    }
}

VENDOR_LIST = [
    "yfinance",
    "alpha_vantage",
    "sina_finance",  # 新增：新浪财经数据源
]

# Mapping of methods to their vendor-specific implementations
VENDOR_METHODS = {
    # core_stock_apis
    "get_stock_data": {
        "alpha_vantage": get_alpha_vantage_stock,
        "yfinance": get_YFin_data_online,
        "sina_finance": get_sina_data_online,  # 新增：新浪财经
    },
    # technical_indicators
    "get_indicators": {
        "alpha_vantage": get_alpha_vantage_indicator,
        "yfinance": get_stock_stats_indicators_window,
    },
    # fundamental_data
    "get_fundamentals": {
        "alpha_vantage": get_alpha_vantage_fundamentals,
        "yfinance": get_yfinance_fundamentals,
        "sina_finance": get_sina_fundamentals,
    },
    "get_balance_sheet": {
        "alpha_vantage": get_alpha_vantage_balance_sheet,
        "yfinance": get_yfinance_balance_sheet,
        "sina_finance": get_sina_balance_sheet,
    },
    "get_cashflow": {
        "alpha_vantage": get_alpha_vantage_cashflow,
        "yfinance": get_yfinance_cashflow,
        "sina_finance": get_sina_cashflow,
    },
    "get_income_statement": {
        "alpha_vantage": get_alpha_vantage_income_statement,
        "yfinance": get_yfinance_income_statement,
        "sina_finance": get_sina_income_statement,
    },
    # news_data
    "get_news": {
        "akshare": lambda ticker, start, end: get_akshare_stock_news(symbol=ticker, limit=20),
        "alpha_vantage": get_alpha_vantage_news,
        "yfinance": get_news_yfinance,
    },
    "get_global_news": {
        "akshare": lambda curr_date, days, limit: get_akshare_global_news(curr_date=curr_date.replace("-", ""), limit=limit),
        "yfinance": get_global_news_yfinance,
        "alpha_vantage": get_alpha_vantage_global_news,
    },
    "get_insider_transactions": {
        "alpha_vantage": get_alpha_vantage_insider_transactions,
        "yfinance": get_yfinance_insider_transactions,
    },
}

def get_category_for_method(method: str) -> str:
    """Get the category that contains the specified method."""
    for category, info in TOOLS_CATEGORIES.items():
        if method in info["tools"]:
            return category
    raise ValueError(f"Method '{method}' not found in any category")

def get_vendor(category: str, method: str = None) -> str:
    """Get the configured vendor for a data category or specific tool method.
    Tool-level configuration takes precedence over category-level.
    """
    config = get_config()

    # Check tool-level configuration first (if method provided)
    if method:
        tool_vendors = config.get("tool_vendors", {})
        if method in tool_vendors:
            return tool_vendors[method]

    # Fall back to category-level configuration
    return config.get("data_vendors", {}).get(category, "default")

def route_to_vendor(method: str, *args, **kwargs):
    """Route method calls to appropriate vendor implementation with fallback support."""
    category = get_category_for_method(method)
    vendor_config = get_vendor(category, method)
    primary_vendors = [v.strip() for v in vendor_config.split(',')]

    logger = logging.getLogger(__name__)
    logger.info(f"[ROUTE_DECISION] {method} -> {primary_vendors} | category={category}")

    if method not in VENDOR_METHODS:
        raise ValueError(f"Method '{method}' not supported")

    # Build fallback chain: primary vendors first, then remaining available vendors
    all_available_vendors = list(VENDOR_METHODS[method].keys())
    fallback_vendors = primary_vendors.copy()
    for vendor in all_available_vendors:
        if vendor not in fallback_vendors:
            fallback_vendors.append(vendor)

    for vendor in fallback_vendors:
        if vendor not in VENDOR_METHODS[method]:
            continue

        vendor_impl = VENDOR_METHODS[method][vendor]
        impl_func = vendor_impl[0] if isinstance(vendor_impl, list) else vendor_impl

        logger.info(f"[ROUTE_ATTEMPT] Trying vendor: {vendor} for {method}")

        try:
            result = impl_func(*args, **kwargs)
            logger.info(f"[ROUTE_SUCCESS] {method} via {vendor}")
            return result
        except AlphaVantageRateLimitError as e:
            logger.warning(f"[RATE_LIMIT] Alpha Vantage | {method} | {str(e)}")
            continue  # Only rate limits trigger fallback
        except Exception as e:
            # Check if this is yfinance rate limit error
            if YFRateLimitError and isinstance(e, YFRateLimitError):
                logger.error(f"[RATE_LIMIT] yfinance | {method} | {str(e)}")
                # yfinance does not fallback, re-raise immediately
                raise RuntimeError(f"yfinance rate limit: {str(e)}")
            else:
                # Other errors: log and re-raise
                logger.error(f"[VENDOR_ERROR] {vendor} | {method} | {type(e).__name__}: {str(e)}")
                raise

    raise RuntimeError(f"No available vendor for '{method}'")