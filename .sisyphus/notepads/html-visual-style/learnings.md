# HTML Visual Style - Learnings

## 修改记录 (2026-04-23)

### 修改文件
- `tradingagents/graph/report_generator.py` - `_build_html_prompt()` 方法样式描述块重写

### 修改内容摘要
将"简洁清爽浅色主题"替换为"经济学人杂志风"样式描述。

### 新配色方案（具体 hex 值）
- 页面背景：冷灰 `#F0F2F5`（非纯白）
- 主文字：深蓝 `#1A2B4A`（非纯黑）
- 次文字：中灰蓝 `#5A6B82`
- 强调色：青蓝 `#2D6A9F`
- 分隔线：浅灰蓝 `#D5DBE3`
- 表格条纹：交替 `#F5F7FA` / `#FFFFFF`
- 表格头背景：深灰蓝 `#E8ECF2`

### 决策卡冷化语义色
- BUY：薄荷青绿 — 背景 `#E0F2F1`，边框 `#00897B`
- SELL：冷红玫红 — 背景 `#FFEBEE`，边框 `#C62828`
- HOLD：石板蓝 — 背景 `#E3F2FD`，边框 `#1565C0`
- 所有决策卡文字统一深蓝 `#1A2B4A`

### 字体方案
- 标题（H1/H2）：`Georgia, "Times New Roman", "Noto Serif SC", "STSong", serif`
- 正文：`-apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", sans-serif`

### 精致表格样式
- 圆角 6px 边框
- 条纹行（交替浅灰蓝背景）
- 表头深灰蓝背景 + 深蓝粗体文字
- 数据行 hover 强调色提示 `#2D6A9F`

### 编辑排版感
- 段落间距 28px
- H2 标题上方间距 36px
- H2 标题下方 2px 底线（颜色 `#2D6A9F`）
- 细线分隔（1px `#D5DBE3`）代替粗边框
- 引用/高亮框：背景 `#E8F4F8` + 1px 边框 `#2D6A9F`

### 必须保留不变的内容（已确认完整保留）
1. **技术限制** 段落 (L606-613) - 内联 CSS、无 JS、无外部文件、UTF-8
2. **HTML 结构要求** 段落 (L615-632) - container > section > h2 规则
3. **error_feedback** 处理逻辑 (L713-721)
4. viewport meta 设置 (width=375)
5. 375px/343px 尺寸值

### WCAG 对比度验证
- `#1A2B4A` on `#F0F2F5` ≈ 10:1（合规）