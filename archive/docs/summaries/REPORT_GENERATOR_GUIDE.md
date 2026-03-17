# 报告生成器使用指南

## 功能说明

报告生成器(`ReportGenerator`)可以将TradingAgents的分析结果:
1. **翻译为中文**: 将英文分析报告翻译为地道的中文
2. **生成Markdown文档**: 创建结构化的、易读的Markdown报告

## 快速开始

### 1. 基本使用

```python
from tradingagents.graph.report_generator import ReportGenerator
from tradingagents.default_config import DEFAULT_CONFIG

# 初始化
config = DEFAULT_CONFIG.copy()
generator = ReportGenerator(config)

# 生成报告
markdown_report = generator.generate_markdown_report(
    state=final_state,      # Agent状态
    decision=decision,       # 交易决策(BUY/SELL/HOLD)
    translate=True           # 是否翻译为中文
)

# 保存报告
generator.save_report(markdown_report, "报告.md")
```

### 2. 集成到test_glm.py

已为你修改好 `test_glm.py`,只需运行:

```bash
python test_glm.py
```

默认会:
- ✅ 自动生成中文报告
- ✅ 自动保存为Markdown格式
- ✅ 文件名: `reports/{ticker}_{date}_中文报告.md`

## 配置选项

在 `test_glm.py` 中可以控制:

```python
# 是否生成中文报告
translate_to_chinese = True  # True=中文, False=英文

# 是否生成Markdown文档
generate_markdown = True     # True=生成MD, False=不生成
```

## 报告结构

生成的Markdown报告包含以下部分:

### 1. 标题区域
- 股票代码
- 分析日期
- 生成时间

### 2. 最终决策
- **买入/卖出/持有** (粗体显示)

### 3. 分析摘要 (仅中文报告)
- 关键结论
- 决策依据

### 4. 详细分析
- 🌍 **市场分析**: 市场趋势、宏观环境
- 💰 **基本面分析**: 财务指标、公司状况
- 📰 **新闻分析**: 相关新闻、事件影响
- 💬 **情绪分析**: 社交媒体情绪
- 📈 **技术分析**: 技术指标、价格走势
- 🤔 **投资辩论**: 多空双方观点
- 👔 **交易员分析**: 交易策略建议
- ⚠️ **风险评估**: 风险水平、建议

### 5. 决策详情
- 最终决策的详细说明

### 6. 免责声明
- 投资风险提示

## 示例输出

### 中文报告示例

```markdown
# sh600519 交易分析报告

**分析日期**: 2026-03-13
**生成时间**: 2026-03-13 15:30:00

---

## 📊 最终交易决策

**决策**: **买入**

---

## 📋 分析摘要

本报告对 贵州茅台 进行了全面分析,结合了基本面、技术面、市场情绪等多维度因素。

**关键结论**:
- 经过多轮分析师讨论和风险评估,最终建议**买入**
- 所有报告均已翻译为中文,方便阅读理解

---

## 💰 基本面分析

贵州茅台是中国白酒行业的龙头企业...
```

### 英文报告示例

```markdown
# sh600519 Trading Analysis Report

**Analysis Date**: 2026-03-13
**Generation Time**: 2026-03-13 15:30:00

---

## 📊 Final Trading Decision

**Decision**: **BUY**

---

## 💰 Fundamental Analysis

Guizhou Moutai is a leading enterprise in China's Baijiu industry...
```

## 高级用法

### 自定义翻译器

如果你想使用不同的LLM进行翻译:

```python
from tradingagents.llm_clients import create_llm_client

config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openai"  # 使用OpenAI翻译
config["deep_think_llm"] = "gpt-4"

generator = ReportGenerator(config)
```

### 仅翻译不保存

```python
# 只生成内容,不保存文件
markdown_content = generator.generate_markdown_report(
    state, decision, translate=True
)

# 自己处理内容
print(markdown_content)
# 或发送到其他地方
```

### 自定义报告路径

```python
# 保存到自定义路径
generator.save_report(
    markdown_content,
    "custom/path/my_report.md"
)
```

## 测试

运行测试脚本验证功能:

```bash
python test_report_generator.py
```

这会:
- ✅ 生成英文测试报告
- ✅ 生成中文测试报告
- ✅ 保存为 `test_report_en.md` 和 `test_report_zh.md`

## 注意事项

### 翻译依赖
- 翻译需要LLM支持,确保配置了正确的API密钥
- 如果翻译失败,会自动回退到英文报告
- 翻译会增加一些处理时间

### 报告大小
- 完整报告可能很大(取决于分析内容)
- 如果只需要决策,可以提取 `final_trade_decision` 字段

### 字符编码
- 报告使用UTF-8编码
- 确保Markdown阅读器支持UTF-8

## 推荐工具

查看Markdown报告的工具:
- **Typora**: 所见即所得的Markdown编辑器
- **VS Code**: 配合Markdown Preview Enhanced插件
- **Obsidian**: 知识管理工具
- **GitHub**: 直接在GitHub上查看

## 故障排查

### 翻译失败
```
⚠️ 翻译失败: API key not found
```
**解决**: 检查 `.env` 文件中的API密钥配置

### 报告未生成
```
❌ 报告生成失败: Permission denied
```
**解决**: 检查reports目录权限,或更改保存路径

### 中文乱码
**解决**: 确保文件使用UTF-8编码打开

## 完整示例

```python
#!/usr/bin/env python3
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.graph.report_generator import ReportGenerator
from tradingagents.default_config import DEFAULT_CONFIG

# 1. 配置
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "zhipu"
config["deep_think_llm"] = "glm-4.5-air"
config["quick_think_llm"] = "glm-4.5-air"

# 2. 运行分析
ta = TradingAgentsGraph(debug=True, config=config)
state, decision = ta.propagate("sh600519", "2026-03-13")

# 3. 生成报告
generator = ReportGenerator(config)
report = generator.generate_markdown_report(
    state,
    decision,
    translate=True  # 翻译为中文
)

# 4. 保存报告
generator.save_report(report, "reports/分析报告.md")

print("✅ 报告已生成!")
```

## 更新日志

### v1.0.0 (2026-03-13)
- ✅ 初始版本
- ✅ 支持中英文报告生成
- ✅ 结构化Markdown输出
- ✅ 集成到test_glm.py
