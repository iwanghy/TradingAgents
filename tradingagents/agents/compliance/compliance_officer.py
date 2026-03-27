"""Compliance Officer Agent

Reviews and modifies HTML content to ensure compliance with regulatory requirements.
"""

import signal
from dataclasses import dataclass
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage

from tradingagents.agents.compliance.rules import COMPLIANCE_SYSTEM_PROMPT


class TimeoutError(Exception):
    """Custom exception for timeout operations."""
    pass


def _timeout_handler(signum, frame):
    """Signal handler for timeout."""
    raise TimeoutError("LLM调用超时")


@dataclass
class ComplianceResult:
    """Result of compliance review.

    Attributes:
        is_success: Whether the review completed successfully
        original_html: The original HTML content before review
        compliant_html: The HTML content after compliance modifications
        error_message: Error message if review failed, None otherwise
        is_violation: Whether the content violates platform rules (for platform review)
        violation_categories: List of violation categories (for platform review)
        violation_reasons: List of specific violation reasons (for platform review)
        risk_level: Risk level - high/medium/low (for platform review)
        suggestions: Suggestions for fixing violations (for platform review)
    """
    is_success: bool
    original_html: str
    compliant_html: str
    error_message: Optional[str] = None
    is_violation: Optional[bool] = None
    violation_categories: Optional[list] = None
    violation_reasons: Optional[list] = None
    risk_level: Optional[str] = None
    suggestions: Optional[str] = None


def create_compliance_officer(llm_client, timeout: int = 30):
    """Create a compliance officer agent instance.

    Args:
        llm_client: LLM client instance for review operations
        timeout: Timeout in seconds for LLM calls (default: 30)

    Returns:
        A compliance officer object with review_html method
    """

    class ComplianceOfficer:
        """Compliance Officer agent for HTML compliance review."""

        def __init__(self, llm_client, timeout: int):
            self.llm_client = llm_client
            self.timeout = timeout

        def review_for_platform(
            self,
            content: str,
            platform: str = "xiaohongshu",
            max_retries: int = 3
        ) -> ComplianceResult:
            """Review content against platform compliance rules.

            Args:
                content: Text content to review
                platform: Platform name (currently supports "xiaohongshu")
                max_retries: Maximum retry attempts for JSON parsing failures

            Returns:
                ComplianceResult with violation detection results
            """
            from .rules import XIAOHONGSHU_REVIEW_PROMPT

            if platform != "xiaohongshu":
                return ComplianceResult(
                    is_success=False,
                    original_html=content,
                    compliant_html=content,
                    error_message=f"Unsupported platform: {platform}"
                )

            import json
            import re

            llm = self.llm_client.get_llm()

            for attempt in range(max_retries):
                try:
                    messages = [
                        SystemMessage(content=XIAOHONGSHU_REVIEW_PROMPT),
                        HumanMessage(content=content),
                    ]
                    result = llm.invoke(messages)

                    json_match = re.search(r'\{[^{}]*\}', result.content, re.DOTALL)
                    if json_match:
                        review_data = json.loads(json_match.group())
                        return ComplianceResult(
                            is_success=True,
                            original_html=content,
                            compliant_html=content,
                            is_violation=review_data.get("is_violation", False),
                            violation_categories=review_data.get("violation_categories", []),
                            violation_reasons=review_data.get("violation_reasons", []),
                            risk_level=review_data.get("risk_level", "low"),
                            suggestions=review_data.get("suggestions", ""),
                        )
                except (json.JSONDecodeError, Exception):
                    if attempt == max_retries - 1:
                        error_msg = f"JSON parsing failed after {max_retries} attempts"
                        return ComplianceResult(
                            is_success=False,
                            original_html=content,
                            compliant_html=content,
                            error_message=error_msg
                        )

            return ComplianceResult(
                is_success=False,
                original_html=content,
                compliant_html=content,
                error_message="Max retries exceeded"
            )

        def revise_for_platform(
            self,
            content: str,
            platform: str = "xiaohongshu",
            max_retries: int = 3
        ) -> ComplianceResult:
            """Revise content to comply with platform rules.

            Args:
                content: HTML content to revise
                platform: Platform name (currently supports "xiaohongshu")
                max_retries: Maximum retry attempts

            Returns:
                ComplianceResult with revised content
            """
            from .rules import XIAOHONGSHU_REVISE_PROMPT

            if platform != "xiaohongshu":
                return ComplianceResult(
                    is_success=False,
                    original_html=content,
                    compliant_html=content,
                    error_message=f"Unsupported platform: {platform}"
                )

            llm = self.llm_client.get_llm()

            for attempt in range(max_retries):
                try:
                    messages = [
                        SystemMessage(content=XIAOHONGSHU_REVISE_PROMPT),
                        HumanMessage(content=content),
                    ]
                    result = llm.invoke(messages)
                    revised_content = result.content.strip()

                    if revised_content == "CONTENT_IRREVERSIBLE":
                        return ComplianceResult(
                            is_success=True,
                            original_html=content,
                            compliant_html=content,
                            is_violation=True,
                            violation_reasons=["内容无法合规修改"],
                            risk_level="high",
                            suggestions="该内容无法修改为合规版本，建议重新创作"
                        )

                    if len(revised_content) > 100:
                        return ComplianceResult(
                            is_success=True,
                            original_html=content,
                            compliant_html=revised_content,
                            is_violation=False,
                        )

                except Exception as e:
                    if attempt == max_retries - 1:
                        return ComplianceResult(
                            is_success=False,
                            original_html=content,
                            compliant_html=content,
                            error_message=f"Revision failed: {str(e)}"
                        )

            return ComplianceResult(
                is_success=False,
                original_html=content,
                compliant_html=content,
                error_message="Max retries exceeded"
            )

        def review_html(self, html_content: str) -> ComplianceResult:
            """Review HTML content for compliance.

            Args:
                html_content: HTML content to review

            Returns:
                ComplianceResult with review outcome
            """
            def _invoke_llm():
                llm = self.llm_client.get_llm()
                messages = [
                    SystemMessage(content=COMPLIANCE_SYSTEM_PROMPT),
                    HumanMessage(content=html_content),
                ]
                result = llm.invoke(messages)
                return result

            try:
                # Unix: 使用 signal 模块设置超时
                if hasattr(signal, 'SIGALRM'):
                    old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
                    signal.alarm(self.timeout)

                    try:
                        result = _invoke_llm()
                        signal.alarm(0)  # 取消超时
                        signal.signal(signal.SIGALRM, old_handler)  # 恢复旧处理器
                    except TimeoutError:
                        signal.alarm(0)
                        signal.signal(signal.SIGALRM, old_handler)
                        return ComplianceResult(
                            is_success=False,
                            original_html=html_content,
                            compliant_html=html_content,
                            error_message=f"合规审查超时({self.timeout}秒)",
                        )
                else:
                    # 非 Unix 系统: 直接调用，依赖 LLM 客户端的超时机制
                    result = _invoke_llm()

                return ComplianceResult(
                    is_success=True,
                    original_html=html_content,
                    compliant_html=result.content,
                    error_message=None,
                )

            except Exception as e:
                error_msg = str(e)

                if "rate" in error_msg.lower() or "limit" in error_msg.lower():
                    error_msg = f"API限流: {error_msg}"
                elif "401" in error_msg or "auth" in error_msg.lower():
                    error_msg = f"API认证失败: {error_msg}"
                elif "timeout" in error_msg.lower():
                    error_msg = f"请求超时: {error_msg}"

                return ComplianceResult(
                    is_success=False,
                    original_html=html_content,
                    compliant_html=html_content,
                    error_message=error_msg,
                )

    return ComplianceOfficer(llm_client, timeout)
