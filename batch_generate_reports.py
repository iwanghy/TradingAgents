#!/usr/bin/env python3
"""
批量股票分析报告生成脚本

读取 txt 文件中的股票代码列表，自动为每个股票生成 JPG 报告。
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# 【重要】在导入 yfinance 之前设置环境变量，禁用 curl_cffi
os.environ['YFINANCE_NO_CURL'] = '1'

from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.report_generator import ReportGenerator
from tradingagents.utils.html_to_jpg import convert, check_wkhtmltoimage

console = Console()


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="批量股票分析报告生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认配置
  python batch_generate_reports.py tickers.txt

  # 指定输出目录和报告语言
  python batch_generate_reports.py tickers.txt -o ./my_reports -l chinese

  # 启用分段模式生成多张图片
  python batch_generate_reports.py tickers.txt --segment

  # 使用不同的 LLM 配置
  python batch_generate_reports.py tickers.txt --debate-rounds 3 --model glm-4-plus
        """
    )
    
    parser.add_argument(
        "ticker_file",
        type=str,
        help="包含股票代码的 txt 文件路径（每行一个代码）"
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        type=str,
        default="./reports/batch",
        help="输出目录（默认: ./reports/batch）"
    )
    
    parser.add_argument(
        "-l", "--language",
        type=str,
        choices=["chinese", "english"],
        default="chinese",
        help="报告语言（默认: chinese）"
    )
    
    parser.add_argument(
        "-q", "--quality",
        type=int,
        default=85,
        help="JPG 图片质量 1-100（默认: 85）"
    )
    
    parser.add_argument(
        "--segment",
        action="store_true",
        help="启用分段模式，生成多张图片"
    )
    
    parser.add_argument(
        "--max-segments",
        type=int,
        default=20,
        help="分段模式下最大图片数量（默认: 20）"
    )
    
    parser.add_argument(
        "--debate-rounds",
        type=int,
        default=1,
        help="辩论轮数（默认: 1，更深入分析可设置为 2-3）"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="glm-4.7",
        help="主模型名称（默认: glm-4.7）"
    )
    
    parser.add_argument(
        "--quick-model",
        type=str,
        default="glm-4.5-air",
        help="快速模型名称（默认: glm-4.5-air）"
    )
    
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="遇到错误时继续处理下一个股票"
    )
    
    return parser.parse_args()


def load_tickers(filepath: str) -> List[str]:
    """从文件加载股票代码列表
    
    Args:
        filepath: txt 文件路径
        
    Returns:
        股票代码列表
    """
    ticker_file = Path(filepath)
    
    if not ticker_file.exists():
        raise FileNotFoundError(f"文件不存在: {filepath}")
    
    with open(ticker_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 解析股票代码：去除空白、注释行、空行
    tickers = []
    for line in lines:
        line = line.strip()
        # 跳过空行和注释
        if not line or line.startswith('#') or line.startswith('//'):
            continue
        tickers.append(line)
    
    return tickers


def analyze_single_stock(
    ticker: str,
    config: dict,
    translate_to_chinese: bool,
    output_dir: Path,
    quality: int,
    enable_segmentation: bool,
    max_segments: int,
    html_llm_model: str
) -> dict:
    """分析单个股票并生成报告
    
    Args:
        ticker: 股票代码
        config: 配置字典
        translate_to_chinese: 是否翻译为中文
        output_dir: 输出目录
        quality: JPG 质量
        enable_segmentation: 是否启用分段模式
        max_segments: 最大分段数量
        html_llm_model: HTML 生成模型
        
    Returns:
        包含状态和信息的字典
    """
    trade_date = datetime.now().strftime('%Y-%m-%d')
    result = {
        "ticker": ticker,
        "date": trade_date,
        "success": False,
        "decision": None,
        "html_path": None,
        "jpg_paths": [],
        "error": None
    }
    
    try:
        # 创建该股票的输出目录
        stock_output_dir = output_dir / ticker / trade_date
        stock_output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. 执行分析
        ta = TradingAgentsGraph(debug=False, config=config)
        state, decision = ta.propagate(ticker, trade_date)
        result["decision"] = decision
        
        # 2. 生成报告
        generator = ReportGenerator(config, html_llm_model=html_llm_model)
        
        # 生成 Markdown（可选，用于存档）
        markdown_report = generator.generate_markdown_report(
            state,
            decision,
            translate=translate_to_chinese
        )
        md_path = stock_output_dir / f"{ticker}_{trade_date}_报告.md"
        generator.save_report(markdown_report, str(md_path))
        
        # 生成 HTML
        html_report = generator.generate_html_report_with_llm(
            state,
            decision,
            translate=translate_to_chinese,
            markdown_text=markdown_report
        )
        
        lang_suffix = "中文" if translate_to_chinese else "英文"
        html_filename = f"{ticker}_{trade_date}_{lang_suffix}报告.html"
        html_path = stock_output_dir / html_filename
        generator.save_html_report(html_report, str(html_path))
        result["html_path"] = str(html_path)
        
        # 3. 转换为 JPG
        jpg_paths = convert(
            html_path=html_path,
            output_dir=stock_output_dir,
            quality=quality,
            enable_segmentation=enable_segmentation,
            max_segments=max_segments
        )
        result["jpg_paths"] = jpg_paths
        result["success"] = True
        
    except Exception as e:
        result["error"] = str(e)
        
    return result


def print_summary(results: List[dict]):
    """打印处理结果摘要"""
    console.print()
    console.print(Panel.fit(
        "[bold green]📊 批量处理完成[/bold green]",
        border_style="green"
    ))
    
    # 创建结果表格
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("股票代码", style="cyan", width=12)
    table.add_column("状态", width=8)
    table.add_column("决策", width=8)
    table.add_column("JPG 文件", width=30)
    table.add_column("备注", style="dim")
    
    success_count = 0
    for r in results:
        status = "[green]✓ 成功[/green]" if r["success"] else "[red]✗ 失败[/red]"
        if r["success"]:
            success_count += 1
            
        decision = r["decision"] or "-"
        jpg_count = len(r["jpg_paths"]) if r["jpg_paths"] else 0
        jpg_info = f"{jpg_count} 张图片" if jpg_count > 0 else "-"
        
        note = r["error"][:40] + "..." if r["error"] and len(r["error"]) > 40 else (r["error"] or "-")
        
        table.add_row(
            r["ticker"],
            status,
            decision,
            jpg_info,
            note if not r["success"] else "-"
        )
    
    console.print(table)
    
    # 统计信息
    console.print()
    stats_table = Table(show_header=False, box=None)
    stats_table.add_column("Stats", justify="center")
    stats_table.add_row(
        f"[bold]总计:[/bold] {len(results)} 个股票 | "
        f"[green]成功:[/green] {success_count} | "
        f"[red]失败:[/red] {len(results) - success_count}"
    )
    console.print(Panel(stats_table, border_style="blue"))


def main():
    """主函数"""
    args = parse_args()
    
    # 加载环境变量
    load_dotenv()
    
    # 检查 API Key
    if not os.environ.get("ZHIPU_API_KEY"):
        console.print("[red]❌ 错误: 未找到 ZHIPU_API_KEY[/red]")
        console.print("\n请在 .env 文件中设置:")
        console.print("ZHIPU_API_KEY=your-api-key-here")
        console.print("\n获取 API Key: https://open.bigmodel.cn/")
        sys.exit(1)
    
    # 检查 wkhtmltoimage
    if not check_wkhtmltoimage():
        console.print("[red]❌ 错误: wkhtmltoimage 未安装[/red]")
        console.print("请运行: sudo apt-get install wkhtmltopdf")
        sys.exit(1)
    
    # 加载股票代码
    try:
        tickers = load_tickers(args.ticker_file)
    except FileNotFoundError as e:
        console.print(f"[red]❌ {e}[/red]")
        sys.exit(1)
    
    if not tickers:
        console.print("[red]❌ 未找到有效的股票代码[/red]")
        sys.exit(1)
    
    # 配置
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "zhipu"
    config["deep_think_llm"] = args.model
    config["quick_think_llm"] = args.quick_model
    config["max_debate_rounds"] = args.debate_rounds
    config["max_llm_retries"] = 3
    
    translate_to_chinese = args.language == "chinese"
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 打印配置信息
    console.print(Panel.fit(
        f"[bold cyan]TradingAgents 批量报告生成[/bold cyan]\n\n"
        f"📋 股票文件: {args.ticker_file}\n"
        f"📊 股票数量: {len(tickers)}\n"
        f"📁 输出目录: {output_dir}\n"
        f"🌐 报告语言: {'中文' if translate_to_chinese else '英文'}\n"
        f"🤖 主模型: {args.model}\n"
        f"⚡ 快速模型: {args.quick_model}\n"
        f"🔄 辩论轮数: {args.debate_rounds}\n"
        f"🖼️  JPG 质量: {args.quality}\n"
        f"📄 分段模式: {'启用' if args.segment else '禁用'}",
        title="[bold]配置信息[/bold]",
        border_style="cyan"
    ))
    
    console.print(f"\n[bold]待处理股票列表:[/bold] {', '.join(tickers)}\n")
    
    # 批量处理
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        main_task = progress.add_task(
            "[cyan]处理进度[/cyan]",
            total=len(tickers)
        )
        
        for ticker in tickers:
            progress.update(main_task, description=f"[cyan]正在分析: {ticker}[/cyan]")
            
            result = analyze_single_stock(
                ticker=ticker,
                config=config,
                translate_to_chinese=translate_to_chinese,
                output_dir=output_dir,
                quality=args.quality,
                enable_segmentation=args.segment,
                max_segments=args.max_segments,
                html_llm_model=args.model
            )
            results.append(result)
            
            if result["success"]:
                progress.console.print(f"[green]  ✓ {ticker} 完成 - 决策: {result['decision']}[/green]")
            else:
                progress.console.print(f"[red]  ✗ {ticker} 失败 - {result['error']}[/red]")
                if not args.continue_on_error:
                    progress.console.print("[red]停止处理（使用 --continue-on-error 继续处理后续股票）[/red]")
                    break
            
            progress.advance(main_task)
    
    # 打印摘要
    print_summary(results)
    
    # 返回状态码
    success_count = sum(1 for r in results if r["success"])
    if success_count == len(tickers):
        sys.exit(0)
    elif success_count > 0:
        sys.exit(1)  # 部分成功
    else:
        sys.exit(2)  # 全部失败


if __name__ == "__main__":
    main()
