#!/usr/bin/env python
"""调用合规员 Agent 进行小红书内容审核"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.llm_clients import create_llm_client
from tradingagents.agents.compliance import create_compliance_officer


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/xiaohongshu_review_llm.py <html_file>")
        print()
        print("Environment variables required:")
        print("  OPENAI_API_KEY=...      (for OpenAI)")
        print("  GOOGLE_API_KEY=...      (for Google Gemini)")
        print("  ANTHROPIC_API_KEY=...   (for Anthropic Claude)")
        print("  ZHIPU_API_KEY=...       (for Zhipu GLM)")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    html_content = file_path.read_text(encoding="utf-8")

    config = DEFAULT_CONFIG.copy()
    provider = "zhipu"
    model = "glm-4.7"

    print("=" * 60)
    print(f"小红书内容合规审核: {file_path.name}")
    print("=" * 60)
    print()
    print(f"Provider: {provider}")
    print(f"Model: {model}")
    print()

    llm_client = create_llm_client(provider=provider, model=model)
    officer = create_compliance_officer(llm_client, timeout=120)

    print("正在审核并修改...")
    print()

    result = officer.revise_for_platform(html_content, platform="xiaohongshu")

    if result.is_success:
        if result.is_violation:
            print("【结果】: 内容无法合规修改")
            print(f"【原因】: {result.violation_reasons}")
            print(f"【建议】: {result.suggestions}")
        else:
            print("【结果】: 修改成功")
            print()
            print("=" * 60)
            print("修改后内容:")
            print("=" * 60)
            print()
            print(result.compliant_html)

            output_path = file_path.with_suffix('.revised.html')
            output_path.write_text(result.compliant_html, encoding="utf-8")
            print()
            print(f"已保存到: {output_path}")
    else:
        print(f"【失败】: {result.error_message}")


if __name__ == "__main__":
    main()
