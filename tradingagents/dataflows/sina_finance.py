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


def get_sina_fundamentals(
    ticker: Annotated[str, "股票代码（如 sh600519 或 sz000001）"],
    curr_date: Optional[str] = None
) -> str:
    """
    获取公司基本面信息和财务摘要

    TODO: 当前返回模拟数据，需要实现真实数据获取
    推荐使用以下库之一：
    - akshare: ak.stock_individual_info_em(symbol) - 完整的公司信息
    - tushare: ts.stock_basic(ts_code=...) - 基本信息
    - 新浪财经HTML解析: http://money.finance.sina.com.cn/corp/go.php/vFD_CompanyInfo/stockid/600519/displaytype/4.phtml

    Args:
        ticker: 股票代码
        curr_date: 当前日期（可选）

    Returns:
        str: Markdown格式的公司基本面信息
    """
    logger.info(f"[API_CALL] sina_fundamentals | symbol={ticker}")

    try:
        symbol = convert_symbol_to_sina_format(ticker)
        code = symbol.replace("sh", "").replace("sz", "")

        # 根据代码推断公司信息（模拟数据）
        # 实际应用中应该从API获取
        company_name_map = {
            "600519": "贵州茅台",
            "000001": "平安银行",
            "000002": "万科A",
            "600036": "招商银行",
            "601318": "中国平安"
        }

        company_name = company_name_map.get(code, f"未知公司（代码：{code}）")

        # 构建Markdown格式的基本面信息
        result = f"""# {company_name}（{symbol.upper()}）基本面信息

## 公司基本信息

| 项目 | 内容 |
|------|------|
| 股票代码 | {symbol.upper()} |
| 公司名称 | {company_name} |
| 所属市场 | {'上海证券交易所' if symbol.startswith('sh') else '深圳证券交易所'} |
| 数据日期 | {curr_date or '2024-01-01'} |

*注：以上为示例数据，需从真实API获取*

## 关键财务指标（示例）

| 指标 | 数值 | 单位 |
|------|------|------|
| 总市值 | 2,500,000 | 百万元 |
| 流通市值 | 2,500,000 | 百万元 |
| 市盈率（PE） | 35.5 | - |
| 市净率（PB） | 12.8 | - |
| 净资产收益率（ROE） | 28.5% | - |
| 总资产收益率（ROA） | 22.3% | - |

*数据来源：新浪财经（示例数据，需完善）*

## 主营业务

- 主要业务：白酒生产与销售
- 行业分类：食品饮料 - 白酒
- 主营产品：茅台酒及系列酒

*注：以上为示例数据，需要实现真实的HTML解析或使用专业库*

## TODO: 实现真实数据获取

```python
# 推荐方案1：使用 akshare
import akshare as ak
def get_fundamentals_real(symbol):
    code = symbol.replace('sh', '').replace('sz', '')
    data = ak.stock_individual_info_em(symbol=code)
    return data.to_markdown()

# 推荐方案2：使用 tushare
import tushare as ts
def get_fundamentals_real(symbol):
    ts.set_token('your_token')
    pro = ts.pro_api()
    data = pro.stock_basic(ts_code=symbol.upper())
    return data

# 推荐方案3：新浪财经HTML解析（复杂）
# URL: http://money.finance.sina.com.cn/corp/go.php/vFD_CompanyInfo/stockid/{code}/displaytype/4.phtml
# 需要解析HTML表格结构
```

---
*数据来源：新浪财经*
*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        logger.info(f"[API_SUCCESS] sina_fundamentals | {symbol}")
        return result

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

    TODO: 当前返回模拟数据，需要实现真实数据获取
    推荐使用以下库之一：
    - akshare: ak.stock_balance_sheet_by_yearly_em() / ak.stock_balance_sheet_by_quarterly_em()
    - tushare: pro.balancesheet(ts_code=...)
    - 新浪财经HTML解析: http://money.finance.sina.com.cn/corp/go.php/vFD_BalanceSheet/stockid/600519/displaytype/4.phtml

    Args:
        ticker: 股票代码
        freq: 报告频率（quarterly或annual）
        curr_date: 当前日期（可选）

    Returns:
        str: Markdown格式的资产负债表
    """
    logger.info(f"[API_CALL] sina_balance_sheet | symbol={ticker} | freq={freq}")

    try:
        symbol = convert_symbol_to_sina_format(ticker)
        code = symbol.replace("sh", "").replace("sz", "")

        # 构建模拟的资产负债表数据
        result = f"""# {symbol.upper()} 资产负债表

## 报告频率: {freq}

| 项目 | 2024Q3 | 2024Q2 | 2024Q1 | 2023Q4 |
|------|--------|--------|--------|--------|
| **资产** | | | | |
| 流动资产合计 | 185,230 | 178,450 | 172,890 | 168,500 |
| 货币资金 | 58,900 | 55,200 | 52,100 | 49,800 |
| 应收账款 | 1,250 | 1,180 | 1,120 | 1,050 |
| 存货 | 42,300 | 40,500 | 38,900 | 37,200 |
| 非流动资产合计 | 25,800 | 24,900 | 24,100 | 23,500 |
| 总资产 | 211,030 | 203,350 | 196,990 | 192,000 |
| **负债和股东权益** | | | | |
| 流动负债合计 | 45,600 | 42,300 | 39,800 | 37,500 |
| 非流动负债合计 | 2,100 | 1,980 | 1,850 | 1,700 |
| 总负债 | 47,700 | 44,280 | 41,650 | 39,200 |
| 股东权益合计 | 163,330 | 159,070 | 155,340 | 152,800 |
| 负债和股东权益总计 | 211,030 | 203,350 | 196,990 | 192,000 |

*单位：百万元*

## 关键财务比率（计算得出）

| 指标 | 2024Q3 | 2024Q2 | 2024Q1 | 2023Q4 |
|------|--------|--------|--------|--------|
| 资产负债率 | 22.6% | 21.8% | 21.1% | 20.4% |
| 流动比率 | 4.06 | 4.22 | 4.34 | 4.49 |
| 速动比率 | 3.14 | 3.26 | 3.36 | 3.47 |

## TODO: 实现真实数据获取

```python
# 推荐方案1：使用 akshare（最简单）
import akshare as ak

def get_balance_sheet_real(symbol, freq='quarterly'):
    code = symbol.replace('sh', '').replace('sz', '')
    if freq == 'quarterly':
        df = ak.stock_balance_sheet_by_quarterly_em(symbol=code)
    else:
        df = ak.stock_balance_sheet_by_yearly_em(symbol=code)
    return df.to_markdown()

# 推荐方案2：使用 tushare
import tushare as ts

def get_balance_sheet_real(symbol, freq='quarterly'):
    pro = ts.pro_api('your_token')
    # freq='Q' 季度, 'A' 年度
    df = pro.balancesheet(ts_code=symbol.upper(), period='2024Q3')
    return df

# 推荐方案3：新浪财经HTML解析
# 需要解析多个表格，较复杂
```

---
*数据来源：新浪财经（示例数据，需完善）*
*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        logger.info(f"[API_SUCCESS] sina_balance_sheet | {symbol} | freq={freq}")
        return result

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

    TODO: 当前返回模拟数据，需要实现真实数据获取
    推荐使用以下库之一：
    - akshare: ak.stock_profit_sheet_by_yearly_em() / ak.stock_profit_sheet_by_quarterly_em()
    - tushare: pro.income(ts_code=...)
    - 新浪财经HTML解析: http://money.finance.sina.com.cn/corp/go.php/vFD_ProfitSheet/stockid/600519/displaytype/4.phtml

    Args:
        ticker: 股票代码
        freq: 报告频率（quarterly或annual）
        curr_date: 当前日期（可选）

    Returns:
        str: Markdown格式的利润表
    """
    logger.info(f"[API_CALL] sina_income_statement | symbol={ticker} | freq={freq}")

    try:
        symbol = convert_symbol_to_sina_format(ticker)
        code = symbol.replace("sh", "").replace("sz", "")

        # 构建模拟的利润表数据
        result = f"""# {symbol.upper()} 利润表

## 报告频率: {freq}

| 项目 | 2024Q3 | 2024Q2 | 2024Q1 | 2023Q4 |
|------|--------|--------|--------|--------|
| **营业收入** | 32,500 | 30,800 | 29,200 | 27,500 |
| 营业成本 | 8,900 | 8,400 | 7,900 | 7,500 |
| 毛利润 | 23,600 | 22,400 | 21,300 | 20,000 |
| **利润总额** | | | | |
| 营业利润 | 18,200 | 17,300 | 16,400 | 15,500 |
| 利润总额 | 18,500 | 17,600 | 16,700 | 15,800 |
| 净利润 | 14,800 | 14,100 | 13,400 | 12,700 |
| **每股指标** | | | | |
| 基本每股收益 | 11.75 | 11.20 | 10.65 | 10.10 |
| 稀释每股收益 | 11.75 | 11.20 | 10.65 | 10.10 |

*单位：百万元（每股收益除外）*

## 盈利能力指标

| 指标 | 2024Q3 | 2024Q2 | 2024Q1 | 2023Q4 |
|------|--------|--------|--------|--------|
| 毛利率 | 72.6% | 72.7% | 72.9% | 72.7% |
| 净利率 | 45.5% | 45.8% | 45.9% | 46.2% |
| 营收增长率 | 18.2% | 12.0% | 6.2% | 19.8% |

## TODO: 实现真实数据获取

```python
# 推荐方案1：使用 akshare（最简单）
import akshare as ak

def get_income_statement_real(symbol, freq='quarterly'):
    code = symbol.replace('sh', '').replace('sz', '')
    if freq == 'quarterly':
        df = ak.stock_profit_sheet_by_quarterly_em(symbol=code)
    else:
        df = ak.stock_profit_sheet_by_yearly_em(symbol=code)
    return df.to_markdown()

# 推荐方案2：使用 tushare
import tushare as ts

def get_income_statement_real(symbol, freq='quarterly'):
    pro = ts.pro_api('your_token')
    df = pro.income(ts_code=symbol.upper(), period='2024Q3')
    return df

# 推荐方案3：新浪财经HTML解析
# URL格式: http://money.finance.sina.com.cn/corp/go.php/vFD_ProfitSheet/stockid/{code}/displaytype/4.phtml
```

---
*数据来源：新浪财经（示例数据，需完善）*
*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        logger.info(f"[API_SUCCESS] sina_income_statement | {symbol} | freq={freq}")
        return result

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

    TODO: 当前返回模拟数据，需要实现真实数据获取
    推荐使用以下库之一：
    - akshare: ak.stock_cash_flow_sheet_by_yearly_em() / ak.stock_cash_flow_sheet_by_quarterly_em()
    - tushare: pro.cashflow(ts_code=...)
    - 新浪财经HTML解析: http://money.finance.sina.com.cn/corp/go.php/vFD_CashFlowSheet/stockid/600519/displaytype/4.phtml

    Args:
        ticker: 股票代码
        freq: 报告频率（quarterly或annual）
        curr_date: 当前日期（可选）

    Returns:
        str: Markdown格式的现金流量表
    """
    logger.info(f"[API_CALL] sina_cashflow | symbol={ticker} | freq={freq}")

    try:
        symbol = convert_symbol_to_sina_format(ticker)
        code = symbol.replace("sh", "").replace("sz", "")

        # 构建模拟的现金流量表数据
        result = f"""# {symbol.upper()} 现金流量表

## 报告频率: {freq}

| 项目 | 2024Q3 | 2024Q2 | 2024Q1 | 2023Q4 |
|------|--------|--------|--------|--------|
| **经营活动现金流** | | | | |
| 经营活动现金流入小计 | 35,800 | 34,200 | 32,600 | 31,000 |
| 经营活动现金流出小计 | 12,400 | 11,900 | 11,300 | 10,800 |
| 经营活动产生的现金流量净额 | 23,400 | 22,300 | 21,300 | 20,200 |
| **投资活动现金流** | | | | |
| 投资活动现金流入小计 | 2,100 | 1,900 | 1,800 | 1,700 |
| 投资活动现金流出小计 | 8,500 | 8,200 | 7,800 | 7,500 |
| 投资活动产生的现金流量净额 | -6,400 | -6,300 | -6,000 | -5,800 |
| **筹资活动现金流** | | | | |
| 筹资活动现金流入小计 | 500 | 450 | 400 | 350 |
| 筹资活动现金流出小计 | 15,200 | 14,500 | 13,800 | 13,200 |
| 筹资活动产生的现金流量净额 | -14,700 | -14,050 | -13,400 | -12,850 |
| **现金及现金等价物净增加额** | 2,300 | 1,950 | 1,900 | 1,550 |

*单位：百万元*

## 现金流分析指标

| 指标 | 2024Q3 | 2024Q2 | 2024Q1 | 2023Q4 |
|------|--------|--------|--------|--------|
| 经营现金流/净利润 | 1.58 | 1.58 | 1.59 | 1.59 |
| 自由现金流 | 17,000 | 16,100 | 15,300 | 14,400 |
| 现金流覆盖率 | 158% | 158% | 159% | 159% |

## TODO: 实现真实数据获取

```python
# 推荐方案1：使用 akshare（最简单）
import akshare as ak

def get_cashflow_real(symbol, freq='quarterly'):
    code = symbol.replace('sh', '').replace('sz', '')
    if freq == 'quarterly':
        df = ak.stock_cash_flow_sheet_by_quarterly_em(symbol=code)
    else:
        df = ak.stock_cash_flow_sheet_by_yearly_em(symbol=code)
    return df.to_markdown()

# 推荐方案2：使用 tushare
import tushare as ts

def get_cashflow_real(symbol, freq='quarterly'):
    pro = ts.pro_api('your_token')
    df = pro.cashflow(ts_code=symbol.upper(), period='2024Q3')
    return df

# 推荐方案3：新浪财经HTML解析
# URL格式: http://money.finance.sina.com.cn/corp/go.php/vFD_CashFlowSheet/stockid/{code}/displaytype/4.phtml
# HTML结构复杂，建议优先使用专业库
```

---
*数据来源：新浪财经（示例数据，需完善）*
*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        logger.info(f"[API_SUCCESS] sina_cashflow | {symbol} | freq={freq}")
        return result

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
