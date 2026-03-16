"""
改进的新闻获取模块 - 添加重试机制和限流处理
"""

import time
import logging
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)


def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 2.0,
    backoff_factor: float = 2.0,
    *args,
    **kwargs
) -> Optional[Any]:
    """
    带有指数退避的重试机制

    Args:
        func: 要重试的函数
        max_retries: 最大重试次数
        base_delay: 基础延迟时间（秒）
        backoff_factor: 退避因子
        *args, **kwargs: 传递给函数的参数

    Returns:
        函数返回值，或 None（所有重试都失败）
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_error = e
            error_str = str(e).lower()

            # 检查是否是限流错误
            is_rate_limit = (
                "too many requests" in error_str or
                "rate limit" in error_str or
                "429" in error_str
            )

            if is_rate_limit and attempt < max_retries - 1:
                # 计算延迟时间：base_delay * (backoff_factor ** attempt)
                delay = base_delay * (backoff_factor ** attempt)
                logger.warning(
                    f"[RATE_LIMIT] 第 {attempt + 1}/{max_retries} 次尝试失败，"
                    f"等待 {delay:.1f} 秒后重试..."
                )
                time.sleep(delay)
            elif attempt < max_retries - 1:
                # 非限流错误，短暂延迟后重试
                logger.warning(
                    f"[ERROR] 第 {attempt + 1}/{max_retries} 次尝试失败: {e}"
                )
                time.sleep(1)
            else:
                # 最后一次尝试失败
                logger.error(f"[ERROR] 所有重试均失败: {e}")

    # 所有重试都失败
    return None


def safe_get_news_yfinance(
    get_news_func: Callable,
    ticker: str,
    start_date: str,
    end_date: str,
    max_retries: int = 3
) -> str:
    """
    安全的新闻获取（带重试）

    Args:
        get_news_func: 新闻获取函数
        ticker: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        max_retries: 最大重试次数

    Returns:
        新闻字符串或错误消息
    """
    def _fetch():
        return get_news_func(ticker, start_date, end_date)

    result = retry_with_backoff(_fetch, max_retries=max_retries)

    if result is None:
        return (
            f"⚠️ 新闻获取失败：API 限流或网络错误\n"
            f"   建议：\n"
            f"   - 稍后重试\n"
            f"   - 使用 Alpha Vantage 作为新闻源\n"
            f"   - 配置文件中设置：config['data_vendors']['news_data'] = 'alpha_vantage'"
        )

    return result


def safe_get_global_news_yfinance(
    get_global_news_func: Callable,
    curr_date: str,
    look_back_days: int = 7,
    limit: int = 10,
    max_retries: int = 3
) -> str:
    """
    安全的全局新闻获取（带重试和请求限制）

    Args:
        get_global_news_func: 全局新闻获取函数
        curr_date: 当前日期
        look_back_days: 回溯天数
        limit: 限制数量
        max_retries: 最大重试次数

    Returns:
        新闻字符串或错误消息
    """
    # 添加延迟以避免立即触发限流
    time.sleep(1)

    def _fetch():
        return get_global_news_func(curr_date, look_back_days, limit)

    result = retry_with_backoff(_fetch, max_retries=max_retries)

    if result is None:
        return (
            f"⚠️ 全局新闻获取失败：API 限流或网络错误\n"
            f"   建议：\n"
            f"   - 稍后重试\n"
            f"   - 减少 look_back_days 或 limit 参数\n"
            f"   - 使用 Alpha Vantage 作为新闻源"
        )

    return result


# 使用示例
if __name__ == "__main__":
    # 测试重试机制
    def test_func():
        raise Exception("Too Many Requests")

    result = retry_with_backoff(test_func, max_retries=2, base_delay=0.5)
    print(f"结果: {result}")
