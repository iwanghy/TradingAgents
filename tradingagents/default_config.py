import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings
    "llm_provider": "openai",
    "deep_think_llm": "gpt-5.2",
    "quick_think_llm": "gpt-5-mini",
    "backend_url": "https://api.openai.com/v1",
    "max_llm_retries": 3,                # 自动重试次数，用于处理 API 限流（429错误）和网络错误
    # Provider-specific thinking configuration
    "google_thinking_level": None,      # "high", "minimal", etc.
    "openai_reasoning_effort": None,    # "medium", "high", "low"
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Data vendor configuration
    # Category-level configuration (default for all tools in category)
    "data_vendors": {
        "core_stock_apis": "sina_finance",
        "technical_indicators": "yfinance",
        "fundamental_data": "sina_finance",
        "news_data": "akshare",
    },
    # Tool-level configuration (takes precedence over category-level)
    "tool_vendors": {
        # Example: "get_stock_data": "alpha_vantage",  # Override category default
    },
    # Logging configuration
    "logging": {
        "enabled": True,                    # 启用日志系统
        "level": "INFO",                    # 全局日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
        "data_api_level": "DEBUG",          # 数据获取层日志级别（更详细）
        "format": "detailed",               # 日志格式: "simple", "detailed", "json"
        "console": True,                    # 是否输出到控制台
        "file": "./logs/tradingagents.log", # 日志文件路径（启用日志文件输出）
        # 示例: "./logs/tradingagents.log"
    },
}
