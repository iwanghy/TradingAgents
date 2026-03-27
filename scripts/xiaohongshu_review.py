#!/usr/bin/env python
"""小红书内容合规审核脚本"""

import sys
import json
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tradingagents.agents.compliance.rules import (
    XIAOHONGSHU_PROHIBITED_CATEGORIES,
    XIAOHONGSHU_PROFIT_INDUCEMENT,
    XIAOHONGSHU_TRAFFIC_DIVERSION,
    XIAOHONGSHU_HIGH_RETURN_CLAIMS,
)


def extract_text(html_content: str) -> str:
    content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
    content = re.sub(r'<[^>]+>', '', content)
    content = re.sub(r'\s+', ' ', content).strip()
    return content


def review_content(html_content: str) -> dict:
    text = extract_text(html_content)
    violations = []

    for category, keywords in XIAOHONGSHU_PROHIBITED_CATEGORIES.items():
        found = [kw for kw in keywords if kw in text]
        if found:
            violations.append({"category": category, "keywords": found})

    profit_found = [kw for kw in XIAOHONGSHU_PROFIT_INDUCEMENT if kw in text]
    if profit_found:
        violations.append({"category": "盈利诱导", "keywords": profit_found})

    traffic_found = [kw for kw in XIAOHONGSHU_TRAFFIC_DIVERSION if kw in text]
    if traffic_found:
        violations.append({"category": "导流行为", "keywords": traffic_found})

    high_return_found = [kw for kw in XIAOHONGSHU_HIGH_RETURN_CLAIMS if kw in text]
    if high_return_found:
        violations.append({"category": "高回报噱头", "keywords": high_return_found})

    is_violation = len(violations) > 0
    risk_level = "high" if len(violations) > 2 else "medium" if violations else "low"

    return {
        "is_violation": is_violation,
        "risk_level": risk_level,
        "violations": violations,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/xiaohongshu_review.py <html_file>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    html_content = file_path.read_text(encoding="utf-8")
    result = review_content(html_content)

    print("=" * 60)
    print(f"小红书内容审核: {file_path.name}")
    print("=" * 60)
    print()

    if result["is_violation"]:
        print(f"【是否违规】: 是")
        print(f"【风险等级】: {result['risk_level']}")
        print()

        categories = [v["category"] for v in result["violations"]]
        print(f"【违规类别】: {', '.join(categories)}")
        print()

        print("【违规详情】:")
        for v in result["violations"]:
            print(f"  ❌ {v['category']}: {', '.join(v['keywords'])}")
    else:
        print("【是否违规】: 否")
        print("【风险等级】: low")

    print()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
