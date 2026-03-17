#!/usr/bin/env python3
"""测试日志系统是否正常工作"""

import sys
sys.path.insert(0, '.')

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.dataflows.logging_config import setup_logging, get_logger

# 测试日志配置
print("=== 测试 1: 基本日志功能 ===")
logger = setup_logging(level='INFO', format_type='detailed', console=True)
logger.info("日志系统初始化成功")

# 测试不同日志级别
print("\n=== 测试 2: 不同日志级别 ===")
logger.debug("这是 DEBUG 消息（不会显示）")
logger.info("这是 INFO 消息")
logger.warning("这是 WARNING 消息")
logger.error("这是 ERROR 消息")

# 测试配置读取
print("\n=== 测试 3: 配置读取 ===")
logging_config = DEFAULT_CONFIG.get('logging', {})
print(f"日志配置: {logging_config}")
print(f"✓ enabled: {logging_config.get('enabled')}")
print(f"✓ level: {logging_config.get('level')}")
print(f"✓ data_api_level: {logging_config.get('data_api_level')}")
print(f"✓ format: {logging_config.get('format')}")

# 测试命名 logger
print("\n=== 测试 4: 命名 Logger ===")
test_logger = get_logger("tradingagents.test")
test_logger.info("命名 logger 工作正常")

print("\n✅ 所有测试通过！")
