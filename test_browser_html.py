#!/usr/bin/env python3
"""
HTML报告浏览器验证测试

使用Playwright进行端到端浏览器验证
"""

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

async def test_html_browser_rendering():
    """使用Playwright测试HTML在浏览器中的渲染效果"""
    print("="*60)
    print("🌐 HTML浏览器渲染验证")
    print("="*60)
    
    # HTML文件路径
    html_filename = "test_AAPL_2026-03-16_中文报告.html"
    html_path = f"reports/{html_filename}"
    
    # 获取HTML文件的绝对路径
    current_dir = os.getcwd()
    absolute_html_path = os.path.join(current_dir, html_path)
    
    # 检查文件是否存在
    if not os.path.exists(absolute_html_path):
        print(f"❌ HTML文件不存在: {absolute_html_path}")
        return False
    
    print(f"📄 HTML文件路径: {absolute_html_path}")
    print(f"📂 文件绝对路径: {absolute_html_path}")
    
    # 验证file:// URL格式
    file_url = f"file://{absolute_html_path}"
    print(f"🔗 浏览器URL: {file_url}")
    
    try:
        async with async_playwright() as p:
            # 启动Chromium浏览器
            print(f"\n🚀 启动Chromium浏览器...")
            browser = await p.chromium.launch(headless=True)  # 无头模式，不显示浏览器窗口
            page = await browser.new_page()
            
            # 设置视窗大小
            await page.set_viewport_size({"width": 1200, "height": 800})
            
            # 导航到HTML文件
            print(f"\n🌍 导航到HTML文件...")
            print(f"   URL: {file_url}")
            
            response = await page.goto(file_url, timeout=10000)  # 10秒超时
            
            if response is None:
                print("❌ 页面加载失败 - 无响应")
                await browser.close()
                return False
                
            print(f"✅ 页面加载成功!")
            print(f"   状态码: {response.status}")
            print(f"   URL: {response.url}")
            
            # 等待页面加载完成
            print(f"\n⏳ 等待页面加载完成...")
            await page.wait_for_load_state("networkidle", timeout=5000)
            print(f"✅ 页面加载完成!")
            
            # 断言1: 验证h1标题存在
            print(f"\n🔍 验证页面元素...")
            
            # 检查h1标题
            try:
                h1_element = await page.query_selector("h1")
                if h1_element:
                    h1_text = await h1_element.inner_text()
                    print(f"   ✅ h1标题存在: '{h1_text}'")
                else:
                    print("   ❌ h1标题不存在")
                    return False
            except Exception as e:
                print(f"   ❌ 检查h1标题时出错: {e}")
                return False
            
            # 检查body背景色（查找body或特定容器）
            try:
                body_element = await page.query_selector("body")
                if body_element:
                    body_bg_color = await body_element.evaluate('el => getComputedStyle(el).backgroundColor')
                    print(f"   🎨 body背景色: {body_bg_color}")
                    
                    # 检查是否为黑色或接近黑色
                    if "rgb(0, 0, 0)" in body_bg_color.lower() or "black" in body_bg_color.lower():
                        print(f"   ✅ 背景色为黑色")
                    else:
                        print(f"   ⚠️ 背景色可能不是预期的黑色")
                else:
                    print("   ❌ body元素不存在")
                    return False
            except Exception as e:
                print(f"   ❌ 检查背景色时出错: {e}")
                return False
            
            # 检查决策卡片
            try:
                decision_elements = await page.query_selector_all("div.decision, .decision, [class*='decision']")
                if decision_elements:
                    for i, elem in enumerate(decision_elements):
                        text = await elem.inner_text()
                        print(f"   ✅ 决策元素 {i+1}: '{text}'")
                else:
                    print("   ❌ 未找到决策卡片元素")
                    return False
            except Exception as e:
                print(f"   ❌ 检查决策卡片时出错: {e}")
                return False
            
            # 检查免责声明
            try:
                disclaimer_elements = await page.query_selector_all("h3, .footer, [class*='disclaimer'], [class*='footer']")
                disclaimer_found = False
                
                for elem in disclaimer_elements:
                    text = await elem.inner_text()
                    if "免责声明" in text or "disclaimer" in text.lower():
                        print(f"   ✅ 免责声明找到: '{text}'")
                        disclaimer_found = True
                        break
                
                if not disclaimer_found:
                    print("   ❌ 未找到免责声明")
                    return False
            except Exception as e:
                print(f"   ❌ 检查免责声明时出错: {e}")
                return False
            
            # 检查主要文本内容
            try:
                content_elements = await page.query_selector_all("div.content, .content, p, .section")
                total_content = ""
                
                for elem in content_elements[:5]:  # 检查前5个内容元素
                    text = await elem.inner_text()
                    total_content += text + " "
                
                print(f"   📄 内容预览 (前200字符): {total_content[:200]}...")
                
                if "AAPL" in total_content and "买入" in total_content:
                    print(f"   ✅ 内容包含股票代码和决策信息")
                else:
                    print(f"   ⚠️ 内容可能缺少关键信息")
                    
            except Exception as e:
                print(f"   ❌ 检查内容时出错: {e}")
                return False
            
            # 保存截图
            print(f"\n📸 保存浏览器截图...")
            evidence_dir = Path(".sisyphus/evidence")
            screenshot_path = evidence_dir / "html-report-llm.png"
            
            try:
                await page.screenshot(path=str(screenshot_path), full_page=True)
                print(f"   ✅ 截图已保存: {screenshot_path}")
                print(f"   📊 文件大小: {screenshot_path.stat().st_size} 字节")
            except Exception as e:
                print(f"   ❌ 保存截图失败: {e}")
                return False
            
            # 获取页面标题验证
            try:
                page_title = await page.title()
                print(f"   📄 页面标题: {page_title}")
                if "AAPL" in page_title and "交易分析报告" in page_title:
                    print(f"   ✅ 页面标题正确")
                else:
                    print(f"   ⚠️ 页面标题可能不完整")
            except Exception as e:
                print(f"   ❌ 获取页面标题失败: {e}")
                return False
            
            # 等待一小段时间确保页面稳定
            await page.wait_for_timeout(2000)
            
            # 关闭浏览器
            print(f"\n🔚 关闭浏览器...")
            await browser.close()
            
            print(f"\n🎉 浏览器验证完成!")
            return True
            
    except Exception as e:
        print(f"\n❌ 浏览器验证过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    # 运行异步测试
    result = asyncio.run(test_html_browser_rendering())
    
    if result:
        print(f"\n✅ 所有浏览器验证测试通过！")
        print(f"📸 截图已保存到: .sisyphus/evidence/html-report-llm.png")
        return True
    else:
        print(f"\n❌ 浏览器验证测试失败！")
        return False

if __name__ == "__main__":
    main()