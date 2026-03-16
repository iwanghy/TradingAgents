#!/usr/bin/env python3
"""
测试HTML生成专用模型功能

演示如何使用html_llm_model参数指定HTML生成专用模型
"""

import os
from dotenv import load_dotenv
from tradingagents.graph.report_generator import ReportGenerator
from tradingagents.default_config import DEFAULT_CONFIG

# 加载.env文件
load_dotenv()

def test_html_with_dedicated_model():
    """测试使用专用HTML生成模型"""
    print("="*80)
    print("🧪 测试HTML生成专用模型功能")
    print("="*80)

    # 配置
    print(f"\n⚙️ 配置LLM提供商...")
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "zhipu"

    # 快速任务使用较快的模型
    config["quick_think_llm"] = "glm-4-flash"
    config["deep_think_llm"] = "glm-4-flash"

    print(f"   📋 LLM提供商: {config.get('llm_provider')}")
    print(f"   ⚡ 快速任务模型: {config.get('quick_think_llm')}")
    print(f"   🧠 深度思考模型: {config.get('deep_think_llm')}")

    # HTML生成使用更强大的模型
    html_model = "glm-4-plus"
    print(f"\n🎨 HTML生成专用模型: {html_model}")
    print(f"   💡 好处: 更强的模型可以生成更完整、更详细的HTML内容")

    try:
        # 初始化报告生成器，指定HTML生成专用模型
        print(f"\n🚀 初始化报告生成器（带HTML专用模型）...")
        generator = ReportGenerator(config, html_llm_model=html_model)
        print(f"   ✅ 报告生成器初始化完成")

        # 验证配置
        print(f"\n🔍 验证LLM客户端配置:")
        print(f"   📝 翻译器模型: {config.get('quick_think_llm')}")
        if generator.html_generator:
            print(f"   🎨 HTML生成器模型: {html_model} (专用)")
        else:
            print(f"   ⚠️ HTML生成器: 使用翻译器模型")

        # 创建简单的测试state
        state = {
            "company_of_interest": "TEST",
            "trade_date": "2026-03-16",
            "market_report": "测试市场分析内容",
            "sentiment_report": "测试情绪分析内容",
            "news_report": "测试新闻分析内容",
            "fundamentals_report": "测试基本面分析内容",
            "technical_report": "测试技术分析内容",
            "investment_debate_state": {
                "history": "测试辩论历史",
                "judge_decision": "测试辩论结论"
            },
            "trader_investment_plan": "测试交易员计划",
            "risk_debate_state": {
                "history": "测试风险讨论",
                "judge_decision": "测试风险评估"
            },
            "final_trade_decision": "测试最终决策"
        }
        decision = "HOLD"

        # 生成简单的HTML测试
        print(f"\n🎨 生成HTML报告（测试模式）...")
        html_content = generator.generate_html_report_with_llm(
            state=state,
            decision=decision,
            translate=False
        )

        print(f"\n✅ HTML生成完成")
        print(f"   📊 HTML长度: {len(html_content)} 字符")

        # 保存测试文件
        test_file = "reports/test_html_with_dedicated_model.html"
        generator.save_html_report(html_content, test_file)
        print(f"   💾 测试文件: {test_file}")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_html_without_dedicated_model():
    """测试不使用专用HTML生成模型（默认行为）"""
    print(f"\n\n{'='*80}")
    print("🧪 测试默认行为（不使用HTML专用模型）")
    print("="*80)

    # 配置
    print(f"\n⚙️ 配置LLM提供商...")
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "zhipu"
    config["quick_think_llm"] = "glm-4-flash"
    config["deep_think_llm"] = "glm-4-flash"

    print(f"   📋 LLM提供商: {config.get('llm_provider')}")
    print(f"   ⚡ 任务模型: {config.get('quick_think_llm')}")
    print(f"   🎨 HTML生成: 将使用相同的模型")

    try:
        # 不指定html_llm_model，使用默认行为
        print(f"\n🚀 初始化报告生成器（默认模式）...")
        generator = ReportGenerator(config)  # 不指定html_llm_model
        print(f"   ✅ 报告生成器初始化完成")

        # 验证配置
        print(f"\n🔍 验证LLM客户端配置:")
        print(f"   📝 翻译器模型: {config.get('quick_think_llm')}")
        if generator.html_generator:
            print(f"   🎨 HTML生成器: 专用模型")
        else:
            print(f"   🎨 HTML生成器: 使用翻译器模型（默认）")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False

def print_usage_guide():
    """打印使用指南"""
    print(f"\n\n{'='*80}")
    print("📖 使用指南")
    print("="*80)

    guide = """
## HTML生成专用模型功能

### 1. 基本用法

```python
from tradingagents.graph.report_generator import ReportGenerator
from tradingagents.default_config import DEFAULT_CONFIG

# 配置
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "zhipu"
config["quick_think_llm"] = "glm-4-flash"  # 快速模型
config["deep_think_llm"] = "glm-4-flash"   # 深度思考模型

# 初始化时指定HTML生成专用模型
generator = ReportGenerator(
    config,
    html_llm_model="glm-4-plus"  # HTML生成使用更强的模型
)

# 生成HTML报告
html = generator.generate_html_report_with_llm(state, decision)
```

### 2. 模型选择建议

**快速模型（用于翻译、简单任务）**:
- `glm-4-flash` - 速度快，适合快速响应
- `glm-4-air` - 轻量级，成本较低

**HTML生成专用模型（需要更强的理解和生成能力）**:
- `glm-4-plus` - 最强大，适合生成完整、详细的HTML
- `glm-4` - 标准版本，平衡性能和质量
- `glm-4.7` - 最新版本，支持更长上下文

### 3. 配置示例

**场景1: 追求质量（推荐）**
```python
config["quick_think_llm"] = "glm-4-flash"
config["deep_think_llm"] = "glm-4"
html_llm_model = "glm-4-plus"  # HTML使用最强模型
```

**场景2: 追求速度**
```python
config["quick_think_llm"] = "glm-4-flash"
config["deep_think_llm"] = "glm-4-flash"
html_llm_model = None  # 不指定，使用相同的快速模型
```

**场景3: 平衡性能和成本**
```python
config["quick_think_llm"] = "glm-4-flash"
config["deep_think_llm"] = "glm-4"
html_llm_model = "glm-4"  # HTML使用标准模型
```

### 4. 优势

✅ **性能优化**: 不同任务使用合适的模型
✅ **成本控制**: HTML生成可以使用更强的模型而不影响其他任务
✅ **灵活性**: 可以根据需求调整各个阶段的模型
✅ **向后兼容**: 不指定html_llm_model时，行为与之前完全相同

### 5. 注意事项

- HTML生成是计算密集型任务，使用更强的模型会提高质量但增加成本
- 如果html_llm_model指定的模型初始化失败，会自动回退到使用翻译器模型
- 确保指定的模型在当前LLM提供商（如zhipu）中可用
"""

    print(guide)

def main():
    """主函数"""
    success1 = test_html_with_dedicated_model()
    success2 = test_html_without_dedicated_model()

    print_usage_guide()

    print(f"\n{'='*80}")
    if success1 and success2:
        print("✅ 所有测试通过!")
        print("="*80)
        print("\n💡 你现在可以使用html_llm_model参数来指定HTML生成专用模型了!")
        return 0
    else:
        print("❌ 部分测试失败")
        print("="*80)
        return 1

if __name__ == "__main__":
    exit(main())
