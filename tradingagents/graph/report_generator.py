"""
TradingAgents 结果翻译和格式化工具

将TradingAgents分析结果翻译为中文并生成结构化Markdown文档
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import html5lib
from tradingagents.llm_clients.factory import create_llm_client


class ReportGenerator:
    """生成结构化的交易分析报告"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化报告生成器

        Args:
            config: 配置字典,包含LLM提供商设置
        """
        self.config = config
        self.translator = None

        provider = config.get("llm_provider")
        if provider:
            try:
                # 获取模型名称
                model = config.get("quick_think_llm", config.get("deep_think_llm"))

                # 创建LLM客户端
                self.translator = create_llm_client(
                    provider=provider,
                    model=model
                )

                # 添加翻译器状态检查
                if self.translator:
                    print(f"✅ 翻译器初始化成功 ({provider}/{model})")
                else:
                    print(f"⚠️ 警告: 翻译器初始化失败 - 翻译功能将不可用")
            except Exception as e:
                print(f"⚠️ 警告: 无法初始化翻译器: {e}")
                print("   将跳过翻译功能,直接生成英文报告")

    def translate_to_chinese(self, text: str) -> str:
        """
        将文本翻译为中文

        Args:
            text: 英文文本

        Returns:
            中文翻译
        """
        # 添加调试信息
        if not self.translator:
            print("❌ 翻译器未初始化 - 检查配置")
            return f"[翻译失败-翻译器未初始化] {text}"

        # 检查文本是否为空或过短
        if not text or len(text.strip()) < 10:
            return text

        # 检查是否已经包含中文字符
        if self._contains_chinese(text):
            # 已经是中文，不需要翻译
            return text

        # 截断过长的文本（避免超过API限制）
        max_length = 6000  # 更保守的长度限制
        if len(text) > max_length:
            print(f"⚠️ 文本过长({len(text)}字符)，截断到{max_length}字符")
            text = text[:max_length] + "\n\n...[因内容过长，后续部分未翻译]"

        try:
            print(f"🔄 正在翻译文本 (长度: {len(text)}字符)...")  # 添加
            # 获取底层的ChatOpenAI实例
            llm = self.translator.get_llm()

            # 使用正确的消息格式
            from langchain_core.messages import HumanMessage, SystemMessage

            messages = [
                SystemMessage(
                    content="你是一个专业的金融翻译专家。请将提供的英文交易分析报告准确翻译为中文。"
                    "保持专业术语的准确性,使用地道的中文表达。"
                    "不要添加任何解释或额外内容,只返回翻译结果。"
                ),
                HumanMessage(content=text),
            ]

            result = llm.invoke(messages)
            print(f"✅ 翻译成功")  # 添加
            return result.content

        except Exception as e:
            # 详细的错误信息
            error_msg = str(e)
            print(f"❌ 翻译失败: {error_msg}")  # 添加

            if "rate" in error_msg.lower() or "limit" in error_msg.lower():
                print(f"   原因: API限流")
                return f"[翻译失败-API限流] {text}"
            elif "400" in error_msg or "prompt" in error_msg:
                print(f"   原因: 内容格式问题")
                return f"[翻译失败-格式问题] {text}"
            elif "401" in error_msg or "auth" in error_msg:
                print(f"   原因: API认证失败")
                return f"[翻译失败-认证问题] {text}"
            else:
                print(f"   原因: 未知错误")
                return f"[翻译失败-{type(e).__name__}] {text}"

    def _contains_chinese(self, text: str) -> bool:
        """检查文本是否包含中文字符"""
        if not text:
            return False
        # 检查是否有中文字符（Unicode范围）
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                return True
        return False

    def generate_markdown_report(
        self,
        state: Dict[str, Any],
        decision: str,
        translate: bool = True
    ) -> str:
        """
        生成结构化的Markdown报告

        Args:
            state: Agent状态字典,包含所有分析报告
            decision: 最终交易决策 (BUY/SELL/HOLD)
            translate: 是否翻译为中文

        Returns:
            完整的Markdown报告内容
        """
        ticker = state.get("company_of_interest", "UNKNOWN")
        trade_date = state.get("trade_date", "UNKNOWN")

        # 决策映射
        decision_map = {
            "BUY": "买入",
            "SELL": "卖出",
            "HOLD": "持有"
        }

        # 生成报告
        report_lines = []

        # 标题
        report_lines.append(f"# {ticker} 交易分析报告\n")
        report_lines.append(f"**分析日期**: {trade_date}\n")
        report_lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report_lines.append("---\n")

        # 最终决策
        decision_zh = decision_map.get(decision.upper(), decision)
        report_lines.append("## 📊 最终交易决策\n")
        report_lines.append(f"**决策**: **{decision_zh}**\n")
        report_lines.append("---\n")

        # 获取各个报告
        reports = self._extract_reports(state)

        # 翻译标题
        section_titles = {
            "market": "🌍 市场分析",
            "sentiment": "💬 情绪分析",
            "news": "📰 新闻分析",
            "fundamentals": "💰 基本面分析",
            "technical": "📈 技术分析",
            "debate": "🤔 投资辩论",
            "trader": "👔 交易员分析",
            "risk": "⚠️ 风险评估"
        }

        # 添加各个分析部分
        if translate:
            report_lines.append("## 📋 分析摘要\n")
            report_lines.append(self._generate_summary_zh(decision_zh, reports))
            report_lines.append("\n---\n")

        # 市场分析
        if reports.get("market"):
            report_lines.append(f"## {section_titles['market']}\n")
            content = reports["market"]
            if translate:
                content = self.translate_to_chinese(content)
            report_lines.append(content + "\n")
            report_lines.append("---\n")

        # 基本面分析
        if reports.get("fundamentals"):
            report_lines.append(f"## {section_titles['fundamentals']}\n")
            content = reports["fundamentals"]
            if translate:
                content = self.translate_to_chinese(content)
            report_lines.append(content + "\n")
            report_lines.append("---\n")

        # 新闻分析
        if reports.get("news"):
            report_lines.append(f"## {section_titles['news']}\n")
            content = reports["news"]
            if translate:
                content = self.translate_to_chinese(content)
            report_lines.append(content + "\n")
            report_lines.append("---\n")

        # 情绪分析
        if reports.get("sentiment"):
            report_lines.append(f"## {section_titles['sentiment']}\n")
            content = reports["sentiment"]
            if translate:
                content = self.translate_to_chinese(content)
            report_lines.append(content + "\n")
            report_lines.append("---\n")

        # 投资辩论
        if reports.get("debate"):
            report_lines.append(f"## {section_titles['debate']}\n")
            content = reports["debate"]
            if translate:
                content = self.translate_to_chinese(content)
            report_lines.append(content + "\n")
            report_lines.append("---\n")

        # 交易员分析
        if reports.get("trader"):
            report_lines.append(f"## {section_titles['trader']}\n")
            content = reports["trader"]
            if translate:
                content = self.translate_to_chinese(content)
            report_lines.append(content + "\n")
            report_lines.append("---\n")

        # 风险评估
        if reports.get("risk"):
            report_lines.append(f"## {section_titles['risk']}\n")
            content = reports["risk"]
            if translate:
                content = self.translate_to_chinese(content)
            report_lines.append(content + "\n")
            report_lines.append("---\n")

        # 最终决策详情
        report_lines.append("## 📝 决策详情\n")
        if reports.get("final_decision"):
            content = reports["final_decision"]
            if translate:
                content = self.translate_to_chinese(content)
            report_lines.append(content + "\n")

        # 免责声明
        report_lines.append("\n---\n")
        report_lines.append("## ⚠️ 免责声明\n")
        disclaimer = (
            "本报告由AI分析师生成,仅供参考和学习使用,不构成任何投资建议。"
            "投资有风险,入市需谨慎。请根据自身风险承受能力做出投资决策。"
        )
        if translate:
            report_lines.append(disclaimer + "\n")
        else:
            report_lines.append(
                "This report is generated by AI analysts for reference and learning purposes only. "
                "It does not constitute investment advice. Please invest cautiously.\n"
            )

        return "\n".join(report_lines)

    def _extract_reports(self, state: Dict[str, Any]) -> Dict[str, str]:
        """
        从state中提取各个分析报告

        Args:
            state: Agent状态字典

        Returns:
            包含各个报告的字典
        """
        reports = {}

        # 基础报告
        reports["market"] = state.get("market_report", "")
        reports["sentiment"] = state.get("sentiment_report", "")
        reports["news"] = state.get("news_report", "")
        reports["fundamentals"] = state.get("fundamentals_report", "")

        # 投资辩论（使用英文标题，翻译时会自动翻译）
        debate_state = state.get("investment_debate_state", {})
        debate_parts = []
        if debate_state.get("history"):
            debate_parts.append(f"### Debate History\n\n{debate_state['history']}")
        if debate_state.get("judge_decision"):
            debate_parts.append(f"### Debate Conclusion\n\n{debate_state['judge_decision']}")
        if debate_parts:
            reports["debate"] = "\n\n".join(debate_parts)

        # 交易员分析
        reports["trader"] = state.get("trader_investment_plan", "")

        # 风险评估（使用英文标题，翻译时会自动翻译）
        risk_state = state.get("risk_debate_state", {})
        risk_parts = []
        if risk_state.get("history"):
            risk_parts.append(f"### Risk Discussion\n\n{risk_state['history']}")
        if risk_state.get("judge_decision"):
            risk_parts.append(f"### Risk Conclusion\n\n{risk_state['judge_decision']}")
        if risk_parts:
            reports["risk"] = "\n\n".join(risk_parts)

        # 最终决策
        reports["final_decision"] = state.get("final_trade_decision", "")

        return reports

    def _generate_summary_zh(self, decision: str, reports: Dict[str, str]) -> str:
        """
        生成中文分析摘要

        Args:
            decision: 交易决策(中文)
            reports: 各个分析报告

        Returns:
            摘要内容
        """
        # 方案1：使用通用描述（不引用具体报告内容）
        summary_lines = [
            f"本报告对市场情况进行了全面分析,",
            f"结合了基本面、技术面、市场情绪等多维度因素。",
            f"\n**关键结论**:\n",
            f"- 经过多轮分析师讨论和风险评估,最终建议**{decision}**\n",
            f"- 所有报告均已翻译为中文,方便阅读理解\n"
        ]
        return "".join(summary_lines)

    def save_report(self, content: str, filepath: str):
        """
        保存报告到文件

        Args:
            content: Markdown报告内容
            filepath: 保存路径
        """
        # 创建目录
        report_path = Path(filepath)
        report_path.parent.mkdir(parents=True, exist_ok=True)

        # 写入文件
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ 报告已保存: {report_path}")

    def _build_html_prompt(
        self,
        markdown: str,
        error_feedback: Optional[list[str]] = None
    ) -> str:
        """
        构建 HTML 生成 prompt

        根据 Markdown 分析报告，生成专业的 HTML 报告生成指令。
        采用纯文字描述方式，不提供 HTML 示例代码。

        Args:
            markdown: Markdown 报告内容
            error_feedback: 可选的错误反馈列表（用于迭代修复）

        Returns:
            完整的 prompt 文本
        """
        prompt = f"""你是一个专业的金融报告设计师。请根据以下 Markdown 分析报告，生成一个面向投资小白的视觉化 HTML 报告。

**设计主题和风格**：
- 使用 Bloomberg Terminal 暗色主题风格
- 背景颜色：纯黑色 #000000
- 主要文字颜色：浅灰色 #E9ECF1
- 次要文字颜色：中灰色 #A9B3C1
- 边框和分隔线颜色：深灰色 #1A1A1A
- 整体风格专业、简洁、高对比度

**布局要求**：
- 单页面滚动设计，禁止分页
- 内容区域最大宽度 1200px，居中对齐
- 总高度控制在 2000-3000px 之间（相当于 2 页 A4 纸）
- 执行摘要（决策卡片）必须置于页面最顶部
- 使用清晰的视觉层次引导阅读顺序

**决策卡片设计**：
- 决策卡片必须是页面的第一个视觉元素
- 根据决策类型使用不同的左边框颜色和强调色：
  * 买入（BUY）：主色调 #4AF6C3（青绿色）
  * 卖出（SELL）：主色调 #FF433D（红色）
  * 持有（HOLD）：主色调 #0068FF（蓝色）
- 卡片内边距 24px
- 左边框宽度 4px，颜色与决策类型匹配
- 卡片背景色略深于页面背景（建议 #0A0A0A）
- 决策文字使用大号字体加粗显示
- 卡片应包含股票代码、分析日期、决策类型

**技术限制**：
- 生成单个独立的 HTML 文件
- 所有 CSS 样式必须内联在 <style> 标签中，位于 <head> 部分
- 严禁使用任何 JavaScript 代码
- 严禁引用外部 CSS 或 JS 文件
- 使用 UTF-8 编码
- 使用语义化 HTML5 标签（header, main, section, article, footer 等）
- 确保所有标签正确闭合和嵌套

**内容组织结构**：
1. 页面头部：股票代码、公司名称、分析日期
2. 决策卡片：最顶部的执行摘要，清晰展示交易决策
3. 详细分析部分：
   - 市场分析
   - 基本面分析
   - 技术分析
   - 新闻分析
   - 情绪分析
   - 投资辩论
   - 交易员分析
   - 风险评估
4. 决策详情：最终决策的理由和依据
5. 免责声明：位于页面底部，使用较小的字体

**排版和可读性**：
- 使用清晰的标题层级（h1, h2, h3）
- 段落之间有适当的间距（建议 1.5em 行高）
- 使用项目符号和编号列表提高可读性
- 重要数据和结论使用加粗或颜色强调
- 保持足够的留白，避免内容过于密集

**视觉一致性**：
- 所有章节使用统一的间距和对齐方式
- 标题使用固定的颜色方案
- 保持配色方案的一致性
- 使用微妙的阴影和边框创建层次感

**Markdown 报告内容**：
{markdown}

**输出要求**：
- 只输出完整的 HTML 代码，不要任何解释性文字
- 确保包含完整的 HTML 文档结构（<!DOCTYPE html>, <html>, <head>, <body>）
- 确保 HTML 语法正确（所有标签闭合、嵌套正确）
- 确保 CSS 语法正确（括号闭合、分号结束）
- 在 <head> 中设置 charset="utf-8"
- 在 <head> 中设置 viewport meta 标签以支持响应式设计
"""

        # 添加错误反馈部分
        if error_feedback:
            error_list = '\n'.join(f'- {error}' for error in error_feedback)
            prompt += f"""
**上一次生成验证失败，请修复以下错误**：
{error_list}

请根据上述错误提示，重新生成完整的 HTML 代码，确保修复所有问题。
"""

        return prompt

    def _validate_html(self, html: str) -> tuple[bool, list[str]]:
        """
        验证 HTML 语法是否正确

        使用 html5lib 的严格模式验证 HTML，检测语法错误和标签嵌套问题。
        用于 LLM 生成 HTML 后的验证，如果验证失败则提供错误信息用于重试。

        Args:
            html: 待验证的 HTML 字符串

        Returns:
            元组 (is_valid, error_messages):
                - is_valid: HTML 是否有效
                - error_messages: 错误消息列表，验证成功时为空列表
        """
        try:
            parser = html5lib.HTMLParser(strict=True)
            parser.parse(html)
            return True, []
        except Exception as e:
            return False, [str(e)]
