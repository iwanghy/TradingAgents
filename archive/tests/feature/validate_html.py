#!/usr/bin/env python3
"""
HTML报告内容完整性验证脚本
"""

import os
from pathlib import Path

def validate_html_content(html_path):
    """验证HTML文件的内容完整性"""
    print("="*60)
    print("🔍 HTML内容完整性验证")
    print("="*60)
    
    if not os.path.exists(html_path):
        print(f"❌ HTML文件不存在: {html_path}")
        return False
    
    # 读取HTML内容
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print(f"📄 文件路径: {html_path}")
    print(f"📊 文件大小: {len(html_content)} 字符")
    
    # 验证必要内容
    required_checks = {
        "DOCTYPE声明": "<!DOCTYPE html>" in html_content,
        "HTML根标签": "<html" in html_content and "</html>" in html_content,
        "head标签": "<head>" in html_content and "</head>" in html_content,
        "body标签": "<body>" in html_content and "</body>" in html_content,
        "UTF-8编码": "charset=\"utf-8\"" in html_content,
        "viewport设置": "viewport" in html_content,
        "暗黑主题背景": "#000000" in html_content or "black" in html_content.lower(),
        "主要文字颜色": "#E9ECF1" in html_content,
        "次要文字颜色": "#A9B3C1" in html_content,
        "股票代码标题": "AAPL" in html_content,
        "分析日期": "2026-03-16" in html_content,
        "决策信息": "买入" in html_content or "BUY" in html_content,
        "免责声明": "免责声明" in html_content,
        "投资风险提示": "投资有风险" in html_content,
        "中文标题": "交易分析报告" in html_content,
        "结构化样式": "style" in html_content and "<style>" in html_content,
        "容器元素": "container" in html_content,
        "页脚元素": "footer" in html_content,
        "标题层级": "h1" in html_content and "h2" in html_content
    }
    
    print(f"\n📋 验查结果:")
    print("-"*50)
    
    all_passed = True
    passed_count = 0
    total_count = len(required_checks)
    
    for check_name, passed in required_checks.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check_name}: {'通过' if passed else '失败'}")
        if passed:
            passed_count += 1
        else:
            all_passed = False
    
    print("-"*50)
    print(f"📊 验证统计: {passed_count}/{total_count} 项通过")
    
    if all_passed:
        print(f"\n🎉 所有验证项目通过!")
    else:
        print(f"\n⚠️ {total_count - passed_count} 项验证未通过")
    
    # 特殊检查：决策颜色
    if "买入" in html_content:
        print(f"\n🎯 决策类型检查: 买入决策 - 应为蓝色 (#0068FF)")
        if "#0068FF" in html_content:
            print("   ✅ 决策颜色正确")
        else:
            print("   ❌ 决策颜色可能不正确")
    
    return all_passed

def get_absolute_path(html_path):
    """获取HTML文件的绝对路径"""
    # 获取当前工作目录
    current_dir = os.getcwd()
    # 构建绝对路径
    absolute_path = os.path.join(current_dir, html_path)
    return absolute_path

if __name__ == "__main__":
    # HTML文件路径
    html_path = "reports/test_AAPL_2026-03-16_中文报告.html"
    
    # 获取绝对路径
    absolute_html_path = get_absolute_path(html_path)
    
    # 验证HTML内容
    is_valid = validate_html_content(absolute_html_path)
    
    print(f"\n🔗 文件绝对路径: {absolute_html_path}")
    print(f"📂 文件所在目录: {os.path.dirname(absolute_html_path)}")
    
    if is_valid:
        print(f"\n✅ HTML内容验证成功！可以进行下一步浏览器测试。")
    else:
        print(f"\n❌ HTML内容验证失败，需要修复后再进行浏览器测试。")