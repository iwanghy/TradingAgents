"""
TradingAgents 结果翻译和格式化工具

将TradingAgents分析结果翻译为中文并生成结构化Markdown文档
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import html5lib
from concurrent.futures import ThreadPoolExecutor, as_completed
from tradingagents.llm_clients.factory import create_llm_client


class ReportGenerator:
    """生成结构化的交易分析报告"""

    def __init__(self, config: Dict[str, Any], html_llm_model: Optional[str] = None):
        """
        初始化报告生成器

        Args:
            config: 配置字典,包含LLM提供商设置
            html_llm_model: 可选，HTML生成专用模型。如果指定，将使用该模型生成HTML，
                          而不是使用默认的翻译模型。这对于使用更强大的模型生成复杂HTML很有用。
                          例如：html_llm_model="glm-4-plus" 而默认使用 "glm-4-flash"
        """
        self.config = config
        self.translator = None
        self.html_generator = None
        self.html_llm_model = html_llm_model

        provider = config.get("llm_provider")
        if provider:
            try:
                # 1. 创建翻译器（用于文本翻译）
                model = config.get("quick_think_llm", config.get("deep_think_llm"))
                self.translator = create_llm_client(
                    provider=provider,
                    model=model
                )

                # 添加翻译器状态检查
                if self.translator:
                    print(f"✅ 翻译器初始化成功 ({provider}/{model})")
                else:
                    print(f"⚠️ 警告: 翻译器初始化失败 - 翻译功能将不可用")

                # 2. 创建HTML生成器（如果指定了专用模型）
                if html_llm_model:
                    try:
                        self.html_generator = create_llm_client(
                            provider=provider,
                            model=html_llm_model
                        )
                        print(f"✅ HTML生成器初始化成功 ({provider}/{html_llm_model})")
                        print(f"   💡 HTML生成将使用专用模型: {html_llm_model}")
                    except Exception as e:
                        print(f"⚠️ 警告: HTML生成器初始化失败: {e}")
                        print(f"   将回退到使用翻译器模型: {model}")
                        self.html_generator = None
                else:
                    print(f"   📝 HTML生成将使用翻译器模型: {model}")

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
            elif "401" in error_msg or "auth" in error_msg: hello, 昊宇，你好，现在是用qnn2.33量化以后能正常转出qnn模型（需要把输入prompt_mask的类型从bool变成float32能正常转出qnn, 用unit8也会报错），然后使用mage-nn-run推理报错：打印的prompt_mask输入的type是invalid,
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

    def _translate_single_text(self, text: str, section_name: str) -> Tuple[str, str]:
        """
        翻译单个文本部分（用于并行处理）

        Args:
            text: 待翻译的文本
            section_name: 部分名称（用于日志）

        Returns:
            元组 (section_name, 翻译后的文本)
        """
        if not text or len(text.strip()) < 10:
            return section_name, text

        # 检查是否已经包含中文字符
        if self._contains_chinese(text):
            print(f"✓ {section_name}: 已是中文，跳过翻译")
            return section_name, text

        try:
            translated = self.translate_to_chinese(text)
            print(f"✓ {section_name}: 翻译完成")
            return section_name, translated
        except Exception as e:
            print(f"✗ {section_name}: 翻译失败 - {str(e)}")
            return section_name, text

    def _translate_reports_parallel(
        self,
        reports: Dict[str, str],
        max_workers: int = 5
    ) -> Dict[str, str]:
        """
        并行翻译多个报告部分

        Args:
            reports: 待翻译的报告字典 {section_name: content}
            max_workers: 最大并行工作线程数（默认5，避免API限流）

        Returns:
            翻译后的报告字典 {section_name: translated_content}
        """
        if not self.translator:
            print("❌ 翻译器未初始化 - 返回原始内容")
            return reports

        # 过滤出需要翻译的部分
        sections_to_translate = {
            name: content
            for name, content in reports.items()
            if content and not self._contains_chinese(content)
        }

        if not sections_to_translate:
            print("✓ 所有内容已是中文，无需翻译")
            return reports

        print(f"\n🔄 开始并行翻译 {len(sections_to_translate)} 个报告部分...")
        print(f"   并行工作线程数: {max_workers}\n")

        translated_results = {}
        failed_translations = {}

        # 使用线程池并行翻译
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有翻译任务
            future_to_section = {
                executor.submit(
                    self._translate_single_text,
                    content,
                    name
                ): name
                for name, content in sections_to_translate.items()
            }

            # 收集结果
            for future in as_completed(future_to_section):
                section_name = future_to_section[future]
                try:
                    _, translated_text = future.result()
                    translated_results[section_name] = translated_text
                except Exception as e:
                    print(f"✗ {section_name}: 并行翻译异常 - {str(e)}")
                    failed_translations[section_name] = sections_to_translate[section_name]

        # 合并结果：翻译成功的 + 翻译失败的（使用原文）+ 已经是中文的
        final_results = {}
        for name, content in reports.items():
            if name in translated_results:
                final_results[name] = translated_results[name]
            elif name in failed_translations:
                final_results[name] = failed_translations[name]
            else:
                # 已经是中文或不需要翻译的
                final_results[name] = content

        print(f"\n✅ 翻译完成: 成功 {len(translated_results)}/{len(sections_to_translate)} 个部分")
        if failed_translations:
            print(f"⚠️  翻译失败: {len(failed_translations)} 个部分使用原文\n")
        else:
            print()

        return final_results

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

        # 并行翻译所有报告部分
        if translate:
            print("\n" + "="*60)
            print("📊 开始生成报告（并行翻译模式）")
            print("="*60 + "\n")
            reports = self._translate_reports_parallel(reports, max_workers=5)

        # 添加各个分析部分
        if translate:
            report_lines.append("## 📋 分析摘要\n")
            report_lines.append(self._generate_summary_zh(decision_zh, reports))
            report_lines.append("\n---\n")

        # 定义报告部分的顺序
        section_order = ["market", "fundamentals", "news", "sentiment", "debate", "trader", "risk"]

        # 按顺序添加各个部分
        for section in section_order:
            if reports.get(section):
                report_lines.append(f"## {section_titles[section]}\n")
                report_lines.append(reports[section] + "\n")
                report_lines.append("---\n")

        # 最终决策详情
        report_lines.append("## 📝 决策详情\n")
        if reports.get("final_decision"):
            report_lines.append(reports["final_decision"] + "\n")

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

    def save_html_report(self, html_content: str, filepath: str) -> None:
        """保存 HTML 报告到文件

        Args:
            html_content: HTML 报告内容
            filepath: 保存路径
        """
        report_path = Path(filepath)
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ HTML 报告已保存: {report_path}")

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

    def _call_llm_for_html(self, prompt: str) -> str:
        """
        调用 LLM 生成 HTML 报告

        使用专门的 HTML 生成器或翻译器 LLM 客户端来生成 HTML 内容。
        使用专门针对 HTML 生成优化的系统提示词。

        Args:
            prompt: HTML 生成的完整提示词

        Returns:
            LLM 生成的 HTML 字符串

        Raises:
            RuntimeError: 如果没有可用的 LLM 客户端
        """
        # 优先使用专门的HTML生成器，如果没有则使用翻译器
        llm_client = self.html_generator if self.html_generator else self.translator

        if not llm_client:
            raise RuntimeError("Translation not initialized - cannot generate HTML")

        # 获取 LLM 客户端
        llm = llm_client.get_llm()

        # 导入消息类型
        from langchain_core.messages import HumanMessage, SystemMessage

        # 构建消息列表
        messages = [
            SystemMessage(
                content="你是一个专业的金融报告设计师，擅长生成高质量的 HTML 报告。"
            ),
            HumanMessage(content=prompt)
        ]

        # 调用 LLM 并返回结果
        result = llm.invoke(messages)

        # 清理可能存在的markdown代码块标记
        html_content = result.content.strip()

        # 移除markdown代码块标记（如果存在）
        if html_content.startswith("```html"):
            html_content = html_content[7:]  # 移除```html
        elif html_content.startswith("```"):
            html_content = html_content[3:]  # 移除```

        if html_content.endswith("```"):
            html_content = html_content[:-3]  # 移除结尾的```

        return html_content.strip()

    def generate_html_report_with_llm(
        self,
        state: Dict[str, Any],
        decision: str,
        translate: bool = True,
        max_retries: int = 3
    ) -> str:
        """
        使用 LLM 生成 HTML 报告的主方法
        
        集成所有子方法：生成 Markdown、构建提示词、调用 LLM、验证 HTML、实现重试机制
        
        Args:
            state: Agent状态字典,包含所有分析报告
            decision: 最终交易决策 (BUY/SELL/HOLD)
            translate: 是否翻译为中文
            max_retries: 最大重试次数
            
        Returns:
            生成的 HTML 报告字符串
        """
        print("🔄 开始生成 HTML 报告...")
        
        # 1. 先生成 Markdown 报告
        print("📄 正在生成 Markdown 报告...")
        markdown_text = self.generate_markdown_report(state, decision, translate=translate)
        print(f"✅ Markdown 报告生成完成 (长度: {len(markdown_text)} 字符)")
        
        # 2. 尝试生成 HTML（带重试机制）
        html_result = None
        last_errors = []
        last_html = None  # 初始化最后一次尝试的 HTML
        
        for attempt in range(max_retries):
            print(f"🎨 第 {attempt + 1}/{max_retries} 次尝试生成 HTML...")
            current_html = None  # 当前尝试的 HTML
            
            try:
                # 构建 prompt
                if attempt == 0:
                    # 第一次尝试，使用原始 markdown
                    prompt = self._build_html_prompt(markdown_text)
                else:
                    # 后续尝试，添加错误反馈
                    prompt = self._build_html_prompt(markdown_text, error_feedback=last_errors)
                
                print("📝 正在构建 LLM 提示词...")
                
                # 调用 LLM
                print("🤖 正在调用 LLM 生成 HTML...")
                current_html = self._call_llm_for_html(prompt)
                print("✅ LLM 调用完成")

                # 验证 HTML
                print("🔍 正在验证 HTML 格式...")
                if current_html is None:
                    is_valid, errors = False, ["HTML 生成失败，返回 None"]
                else:
                    is_valid, errors = self._validate_html(current_html)
                
                if is_valid:
                    print(f"✅ HTML 生成成功（第 {attempt + 1} 次尝试）")
                    html_result = current_html
                    break
                else:
                    print(f"⚠️ HTML 验证失败（第 {attempt + 1} 次尝试）")
                    print(f"   错误详情: {errors}")
                    last_errors = errors
                    
                    # 如果不是最后一次尝试，添加错误反馈并继续重试
                    if attempt < max_retries - 1:
                        print("   🔄 将添加错误反馈并重试...")
                    else:
                        print("   🚫 已达到最大重试次数")
                        
            except Exception as e:
                error_msg = f"LLM 调用异常: {str(e)}"
                print(f"❌ {error_msg}")
                last_errors = [error_msg]
                
                # 如果不是最后一次尝试，继续重试
                if attempt < max_retries - 1:
                    print("   🔄 将继续重试...")
                else:
                    print("   🚫 已达到最大重试次数")
            
            # 保存最后一次的 HTML 结果
            last_html = current_html
        
        # 3. 处理最终结果
        if html_result:
            print(f"🎉 HTML 报告生成成功！总长度: {len(html_result)} 字符")
            return html_result
        else:
            print(f"❌ HTML 报告生成失败，已尝试 {max_retries} 次")
            print("   返回最后一次生成结果（可能格式有问题）")
            
            # 如果有最后一次的 HTML 结果，返回它
            if 'last_html' in locals() and last_html is not None:
                return last_html
            else:
                # 如果没有任何有效结果，返回一个基本的 HTML 模板
                return self._generate_fallback_html(state, decision, translate)

    def _generate_fallback_html(
        self,
        state: Dict[str, Any],
        decision: str,
        translate: bool = True
    ) -> str:
        """
        生成后备 HTML 报告（当 LLM 生成失败时使用）
        
        Args:
            state: Agent状态字典
            decision: 交易决策
            translate: 是否翻译
            
        Returns:
            基本格式的 HTML 报告
        """
        ticker = state.get("company_of_interest", "UNKNOWN")
        trade_date = state.get("trade_date", "UNKNOWN")
        
        # 决策映射
        decision_map = {
            "BUY": "买入",
            "SELL": "卖出", 
            "HOLD": "持有"
        }
        decision_zh = decision_map.get(decision.upper(), decision)
        
        # 生成基础 HTML
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{ticker} 交易分析报告</title>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            background-color: #000000;
            color: #E9ECF1;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: #0A0A0A;
            padding: 30px;
            border-left: 4px solid #0068FF;
            border-radius: 5px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .title {{
            color: #E9ECF1;
            font-size: 2em;
            margin-bottom: 10px;
        }}
        .subtitle {{
            color: #A9B3C1;
            font-size: 1.1em;
        }}
        .decision {{
            text-align: center;
            font-size: 1.5em;
            font-weight: bold;
            color: #0068FF;
            margin: 20px 0;
        }}
        .section {{
            margin: 20px 0;
            padding: 15px;
            border-left: 3px solid #1A1A1A;
        }}
        .section-title {{
            color: #E9ECF1;
            font-size: 1.3em;
            margin-bottom: 10px;
        }}
        .content {{
            color: #A9B3C1;
            line-height: 1.8;
        }}
        .footer {{
            margin-top: 40px;
            padding: 20px;
            border-top: 1px solid #1A1A1A;
            font-size: 0.9em;
            color: #A9B3C1;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">{ticker} 交易分析报告</h1>
            <p class="subtitle">分析日期: {trade_date} | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="decision">
            最终决策: {decision_zh}
        </div>
        
        <div class="section">
            <h2 class="section-title">📊 分析摘要</h2>
            <div class="content">
                <p>本报告对市场情况进行了全面分析，结合了基本面、技术面、市场情绪等多维度因素。</p>
                <p><strong>关键结论</strong>:</p>
                <ul>
                    <li>经过多轮分析师讨论和风险评估，最终建议<strong>{decision_zh}</strong></li>
                    <li>由于 LLM 生成失败，当前显示为后备格式</li>
                    <li>建议检查 LLM 配置后重新生成完整报告</li>
                </ul>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">📋 报告状态</h2>
            <div class="content">
                <p><strong>状态</strong>: LLM 生成失败，使用后备模板</p>
                <p><strong>建议</strong>: 检查 API 配置和网络连接后重新生成</p>
                <p><strong>原始决策</strong>: {decision_zh}</p>
            </div>
        </div>
        
        <div class="footer">
            <h3>⚠️ 免责声明</h3>
            <p>本报告由AI分析师生成，仅供参考和学习使用，不构成任何投资建议。</p>
            <p>投资有风险，入市需谨慎。请根据自身风险承受能力做出投资决策。</p>
            <p>此页面为 LLM 生成失败时的后备显示格式。</p>
        </div>
    </div>
</body>
</html>"""
        
        return html
