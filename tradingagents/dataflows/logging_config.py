"""
TradingAgents 日志配置模块

提供统一的日志配置和初始化功能
"""
import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_type: str = "detailed",  # "simple", "detailed", "json"
    console: bool = True
) -> logging.Logger:
    """
    初始化 TradingAgents 日志系统

    Args:
        level: 日志级别 ("DEBUG", "INFO", "WARNING", "ERROR")
        log_file: 日志文件路径（可选）
        format_type: 日志格式类型
        console: 是否输出到控制台

    Returns:
        配置好的根 logger
    """

    # 解析日志级别
    log_level = getattr(logging, level.upper(), logging.INFO)

    # 定义日志格式
    if format_type == "simple":
        log_format = "%(levelname)s - %(message)s"
        date_format = None
    elif format_type == "json":
        log_format = '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
        date_format = None
    else:  # detailed
        log_format = "[%(asctime)s] [%(levelname)-8s] [%(name)s] %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"

    formatter = logging.Formatter(log_format, datefmt=date_format)

    # 获取根 logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # 设置为最低级别，允许DEBUG消息通过

    # 清除现有 handlers（避免重复）
    root_logger.handlers.clear()

    # 控制台 handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)  # 终端只显示INFO及以上级别
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # 文件 handler（带轮转）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)  # 文件记录DEBUG及以上级别
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # 配置第三方库日志级别（减少噪音）
    logging.getLogger("yfinance").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    获取命名 logger

    Args:
        name: logger 名称（通常使用 __name__）

    Returns:
        Logger 实例
    """
    return logging.getLogger(name)


# 预定义的日志消息模板
class LogMessages:
    """日志消息模板"""

    # 工具层
    TOOL_ENTRY = "TOOL_ENTRY: {tool_name} called with {params}"
    TOOL_SUCCESS = "TOOL_SUCCESS: {tool_name} completed successfully"
    TOOL_ERROR = "TOOL_ERROR: {tool_name} failed: {error}"

    # 路由层
    ROUTE_DECISION = "ROUTE: {method} -> {vendor} (category: {category})"
    ROUTE_TRY = "ROUTE_ATTEMPT: Trying vendor '{vendor}' for {method}"
    ROUTE_SUCCESS = "ROUTE_SUCCESS: {method} via {vendor}"
    RATE_LIMIT = "RATE_LIMIT: {vendor} rate limit exceeded for {method}"

    # API 层
    API_CALL_START = "API_CALL: {vendor} fetching {symbol} | params: {params}"
    API_CALL_SUCCESS = "API_SUCCESS: {vendor} | {symbol} | records: {records} | duration: {duration:.2f}s"
    API_CALL_ERROR = "API_ERROR: {vendor} | {symbol} | {error_type}: {error}"
    API_EMPTY_DATA = "API_EMPTY: {vendor} | No data found for {symbol}"

    # 速率限制专项
    YFINANCE_RATE_LIMIT = "YFINANCE_RATE_LIMIT: symbol={symbol} | {error} | Will retry after {delay}s"
    ALPHA_VANTAGE_RATE_LIMIT = "AV_RATE_LIMIT: {error} | Will fallback to next vendor"
