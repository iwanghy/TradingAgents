# 报告生成功能 - 快速开始

## 🚀 3步开始使用

### 1. 运行分析(已自动集成)

```bash
python test_glm.py
```

**自动完成**:
- ✅ 运行完整的TradingAgents分析
- ✅ 生成结构化中文报告
- ✅ 保存为Markdown文档

### 2. 查看报告

报告保存在:
```
reports/{ticker}_{date}_中文报告.md
```

示例:
```
reports/sh600519_2026-03-13_中文报告.md
```

### 3. 用Markdown阅读器打开

推荐工具:
- **Typora**: 最简洁直观
- **VS Code**: 免费,功能强大
- **Obsidian**: 知识管理
- **GitHub**: 在线查看

---

## 📊 报告内容

生成的报告包含:

### 标题信息
- 股票代码
- 分析日期
- 生成时间

### 最终决策
- **买入/卖出/持有** (粗体高亮)

### 详细分析
- 🌍 市场分析
- 💰 基本面分析
- 📰 新闻分析
- 💬 情绪分析
- 🤔 投资辩论
- 👔 交易员分析
- ⚠️ 风险评估

### 决策依据
- 完整决策说明
- 风险提示

---

## ⚙️ 配置选项

在 `test_glm.py` 中修改:

```python
# 是否翻译为中文
translate_to_chinese = True   # True=中文, False=英文

# 是否生成Markdown
generate_markdown = True      # True=生成, False=不生成
```

---

## 💡 使用场景

### 场景1: 日常分析
```bash
# 运行分析,自动生成中文报告
python test_glm.py

# 报告保存到: reports/sh600519_2026-03-13_中文报告.md
```

### 场景2: 分析多只股票
```python
# 在test_glm.py中修改ticker
tickers = ["sh600519", "sz000001", "sh600036"]

for ticker in tickers:
    state, decision = ta.propagate(ticker, date)
    report = generator.generate_markdown_report(state, decision, translate=True)
    generator.save_report(report, f"reports/{ticker}_分析.md")
```

### 场景3: 只要决策,不要报告
```python
# 在test_glm.py中设置
generate_markdown = False  # 不生成报告

# 只会在终端显示决策
print(decision)  # BUY, SELL, 或 HOLD
```

### 场景4: 英文报告
```python
# 在test_glm.py中设置
translate_to_chinese = False  # 不翻译

# 生成英文报告
# 报告保存到: reports/sh600519_2026-03-13_英文报告.md
```

---

## 📝 报告示例

### 中文报告

```markdown
# sh600519 交易分析报告

**分析日期**: 2026-03-13
**生成时间**: 2026-03-13 16:08:48

---

## 📊 最终交易决策

**决策**: **买入**

---

## 📋 分析摘要

本报告对贵州茅台进行全面分析,结合了基本面、技术面、市场情绪等多维度因素。

**关键结论**:
- 经过多轮分析师讨论和风险评估,最终建议**买入**
- 所有报告均已翻译为中文,方便阅读理解
```

### 英文报告

```markdown
# sh600519 Trading Analysis Report

**Analysis Date**: 2026-03-13
**Generation Time**: 2026-03-13 16:08:48

---

## 📊 Final Trading Decision

**Decision**: **BUY**

---

## 🌍 Market Analysis

The market is showing strong bullish trends with increasing volume.
```

---

## 🧪 测试功能

```bash
# 测试报告生成器
python test_report_generator.py

# 生成测试报告:
# - test_report_en.md (英文)
# - test_report_zh (中文)
```

---

## ❓ 常见问题

### Q1: 翻译失败怎么办?
**A**: 系统会自动回退到英文报告,不影响使用。检查:
- API密钥是否配置
- 网络连接是否正常
- 配额是否充足

### Q2: 报告太大?
**A**: 报告包含完整分析过程。可以:
- 只查看"最终决策"部分
- 使用Markdown阅读器的目录导航
- 搜索关键字(如"买入", "风险")

### Q3: 如何自定义报告?
**A**: 修改 `report_generator.py` 中的:
- 章节标题
- 报告结构
- 翻译提示词

### Q4: 支持哪些股票?
**A**: 支持TradingAgents支持的所有股票:
- A股: sh600519, sz000001
- 美股: AAPL, NVDA, TSLA
- 其他: 取决于数据源

---

## 📚 相关文档

- **详细指南**: `REPORT_GENERATOR_GUIDE.md`
- **实现总结**: `IMPLEMENTATION_SUMMARY.md`
- **测试脚本**: `test_report_generator.py`

---

## ✨ 功能特点

✅ **自动翻译**: 英文报告自动翻译为中文
✅ **结构清晰**: Markdown格式,层次分明
✅ **内容完整**: 包含所有分析环节
✅ **易于阅读**: 专业排版,适合阅读
✅ **方便分享**: 标准格式,易于分享

---

**开始使用**: `python test_glm.py`

**查看报告**: 打开 `reports/` 目录下的 `.md` 文件

**享受分析**: 阅读专业的AI交易分析报告
