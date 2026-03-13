import pandas as pd
import yfinance as yf
from stockstats import wrap
from typing import Annotated
import os
from .config import get_config
from io import StringIO


def _is_a_share_symbol(symbol: str) -> bool:
    """检测是否为A股代码"""
    symbol_clean = symbol.split('.')[0].upper()

    if symbol_clean.isdigit() and len(symbol_clean) == 6:
        return True

    if symbol_clean.startswith(('SH', 'SZ')):
        code = symbol_clean[2:]
        if code.isdigit() and len(code) == 6:
            return True

    return False


def _convert_to_sina_format(symbol: str) -> str:
    """将股票代码转换为新浪财经格式"""
    symbol_clean = symbol.split('.')[0].upper()

    if symbol_clean.startswith(('SH', 'SZ')):
        return symbol_clean.lower()

    if symbol_clean.isdigit() and len(symbol_clean) == 6:
        if symbol_clean.startswith('6'):
            return f"sh{symbol_clean}"
        else:
            return f"sz{symbol_clean}"

    return symbol


class StockstatsUtils:
    @staticmethod
    def get_stock_stats(
        symbol: Annotated[str, "ticker symbol for the company"],
        indicator: Annotated[
            str, "quantitative indicators based off of the stock data for the company"
        ],
        curr_date: Annotated[
            str, "curr date for retrieving stock price data, YYYY-mm-dd"
        ],
    ):
        config = get_config()

        today_date = pd.Timestamp.today()
        curr_date_dt = pd.to_datetime(curr_date)

        end_date = today_date
        start_date = today_date - pd.DateOffset(years=15)
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        # Ensure cache directory exists
        os.makedirs(config["data_cache_dir"], exist_ok=True)

        # Check if this is an A-share symbol
        is_a_share = _is_a_share_symbol(symbol)

        # Use different data sources and file naming for A-shares vs others
        if is_a_share:
            data_file = os.path.join(
                config["data_cache_dir"],
                f"{symbol}-sina-data-{start_date_str}-{end_date_str}.csv",
            )

            if os.path.exists(data_file):
                data = pd.read_csv(data_file)
                data["Date"] = pd.to_datetime(data["Date"])
            else:
                # Use sina_finance for A-shares
                from .sina_finance import get_sina_data_online

                sina_symbol = _convert_to_sina_format(symbol)

                # Get data from sina_finance
                csv_data = get_sina_data_online(sina_symbol, start_date_str, end_date_str)

                # Parse CSV data
                if csv_data.startswith("Error:") or csv_data.startswith("No data"):
                    raise Exception(f"Sina Finance API error: {csv_data}")

                # Extract CSV lines from response
                lines = csv_data.split('\n')
                csv_lines = []
                for line in lines:
                    if not line.startswith('#') and line.strip():
                        csv_lines.append(line)

                if not csv_lines:
                    raise Exception(f"No valid data from Sina Finance for {symbol}")

                # Parse CSV
                data = pd.read_csv(StringIO('\n'.join(csv_lines)))

                # Cache the data
                data.to_csv(data_file, index=False)
        else:
            # Use yfinance for non-A-shares
            data_file = os.path.join(
                config["data_cache_dir"],
                f"{symbol}-YFin-data-{start_date_str}-{end_date_str}.csv",
            )

            if os.path.exists(data_file):
                data = pd.read_csv(data_file)
                data["Date"] = pd.to_datetime(data["Date"])
            else:
                data = yf.download(
                    symbol,
                    start=start_date_str,
                    end=end_date_str,
                    multi_level_index=False,
                    progress=False,
                    auto_adjust=True,
                )
                data = data.reset_index()
                data.to_csv(data_file, index=False)

        df = wrap(data)
        # Convert Date to string if it's datetime, otherwise keep as is
        if pd.api.types.is_datetime64_any_dtype(df["Date"]):
            df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
        curr_date_str = curr_date_dt.strftime("%Y-%m-%d")

        df[indicator]  # trigger stockstats to calculate the indicator
        matching_rows = df[df["Date"].str.startswith(curr_date_str)]

        if not matching_rows.empty:
            indicator_value = matching_rows[indicator].values[0]
            return indicator_value
        else:
            return "N/A: Not a trading day (weekend or holiday)"
