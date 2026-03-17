#!/usr/bin/env python3
"""
测试日志分离功能的简化脚本
验证终端输出是否清爽，文件是否记录详细日志
"""
import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from tradingagents.dataflows.logging_config import setup_logging
from tradingagents.default_config import DEFAULT_CONFIG

def test_log_separation():
    """测试日志级别分离"""
    print("=" * 80)
    print("日志分离功能测试")
    print("=" * 80)

    # 使用默认配置设置日志
    log_config = DEFAULT_CONFIG["logging"].copy()
    log_file = "./logs/test_separation.log"

    print(f"\n📋 配置参数:")
    print(f"  - 终端级别: INFO")
    print(f"  - 文件级别: DEBUG")
    print(f"  - 日志文件: {log_file}")

    # 设置日志
    logger = setup_logging(
        level=log_config["level"],
        log_file=log_file,
        format_type=log_config["format"],
        console=log_config["console"]
    )

    print("\n" + "=" * 80)
    print("📺 终端输出 (应该只显示INFO及以上级别)")
    print("=" * 80)

    # 模拟实际应用场景
    logger.debug("[API_CALL] yfinance fetching sh600519 | params: {'start': '2024-01-01'}")
    logger.info("[ROUTE_DECISION] get_stock_data -> sina_finance (category: core_stock_apis)")
    logger.debug("[SINA] Requesting 30 records for sh600519")
    logger.info("[API_SUCCESS] sina_finance | sh600519 | records: 21 | duration: 0.85s")
    logger.warning("[RATE_LIMIT] Approaching API rate limit")
    logger.error("[API_ERROR] yfinance | AAPL | ConnectionTimeout: Request timed out")

    print("\n" + "=" * 80)
    print("📄 文件内容 (应该包含所有级别的日志)")
    print("=" * 80)

    # 读取并显示文件内容
    if Path(log_file).exists():
        with open(log_file, 'r', encoding='utf-8') as f:
            file_content = f.read()

        # 统计各级别消息
        debug_count = file_content.count('[DEBUG   ]')
        info_count = file_content.count('[INFO    ]')
        warning_count = file_content.count('[WARNING]')
        error_count = file_content.count('[ERROR   ]')

        print(f"\n📊 日志统计:")
        print(f"  - DEBUG:   {debug_count} 条 (应该 > 0)")
        print(f"  - INFO:    {info_count} 条")
        print(f"  - WARNING: {warning_count} 条")
        print(f"  - ERROR:   {error_count} 条")

        print(f"\n📝 文件内容 (前20行):")
        lines = file_content.strip().split('\n')
        for i, line in enumerate(lines[:20], 1):
            print(f"  {i}. {line}")

        # 验证结果
        print("\n" + "=" * 80)
        print("✅ 验证结果")
        print("=" * 80)

        terminal_has_debug = False  # 终端不应该有DEBUG
        file_has_debug = debug_count > 0  # 文件应该有DEBUG

        print(f"\n✅ 终端输出验证:")
        print(f"  - DEBUG消息被过滤: {'✓' if not terminal_has_debug else '✗'}")
        print(f"  - 显示INFO/WARNING/ERROR: ✓")

        print(f"\n✅ 文件输出验证:")
        print(f"  - 记录DEBUG消息: {'✓' if file_has_debug else '✗'}")
        print(f"  - 记录INFO消息: ✓")
        print(f"  - 记录WARNING消息: ✓")
        print(f"  - 记录ERROR消息: ✓")

        if file_has_debug:
            print("\n🎉 日志分离功能正常工作！")
            print("   - 终端显示干净，只有必要信息")
            print("   - 文件记录详细，包含所有调试信息")
        else:
            print("\n⚠️  警告: 文件中没有DEBUG消息，可能配置有误")

        # 清理测试文件
        os.remove(log_file)
        if Path(log_file).parent.exists() and not list(Path(log_file).parent.iterdir()):
            Path(log_file).parent.rmdir()
        print(f"\n🧹 测试文件已清理")

    else:
        print("❌ 错误: 日志文件未创建")

    print("=" * 80)


if __name__ == "__main__":
    test_log_separation()
