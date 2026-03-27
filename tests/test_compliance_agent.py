"""
测试合规员（Compliance Agent）功能

TDD Red Phase - 这些测试预期失败，因为功能代码尚未实现
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio


@pytest.fixture
def sample_report_path():
    """提供测试用的报告 HTML 文件路径"""
    return Path("tests/fixtures/sample_report.html")


@pytest.fixture
def sample_report_content(sample_report_path):
    """提供测试用的报告 HTML 内容"""
    return sample_report_path.read_text(encoding='utf-8')


@pytest.fixture
def mock_llm_client():
    """Mock LLM 客户端"""
    client = MagicMock()
    client.invoke = AsyncMock()
    return client


# ========== 基础决策术语测试 ==========

def test_decision_terms_buy(sample_report_content):
    """测试买入决策术语转换：BUY/买入 → 值得研究"""
    from tradingagents.agents.compliance.rules import COMPLIANCE_RULES

    # 验证规则定义
    assert "BUY" in COMPLIANCE_RULES["decision"], "应包含 BUY 术语规则"
    assert "买入" in COMPLIANCE_RULES["decision"], "应包含 买入 术语规则"
    assert COMPLIANCE_RULES["decision"]["BUY"] == "值得研究", "BUY 应转换为 值得研究"
    assert COMPLIANCE_RULES["decision"]["买入"] == "值得研究", "买入 应转换为 值得研究"

    # TODO: 功能实现后测试实际转换
    # from tradingagents.agents.compliance import compliance_agent
    # result = compliance_agent.convert_report(sample_report_content)
    # assert "值得研究" in result
    # assert "买入" not in result or "BUY" not in result


def test_decision_terms_sell():
    """测试卖出决策术语转换：SELL/卖出 → 谨慎对待"""
    from tradingagents.agents.compliance.rules import COMPLIANCE_RULES

    assert "SELL" in COMPLIANCE_RULES["decision"], "应包含 SELL 术语规则"
    assert "卖出" in COMPLIANCE_RULES["decision"], "应包含 卖出 术语规则"
    assert COMPLIANCE_RULES["decision"]["SELL"] == "谨慎对待", "SELL 应转换为 谨慎对待"
    assert COMPLIANCE_RULES["decision"]["卖出"] == "谨慎对待", "卖出 应转换为 谨慎对待"


def test_decision_terms_hold():
    """测试持有决策术语转换：HOLD/持有 → 暂时持有"""
    from tradingagents.agents.compliance.rules import COMPLIANCE_RULES

    assert "HOLD" in COMPLIANCE_RULES["decision"], "应包含 HOLD 术语规则"
    assert "持有" in COMPLIANCE_RULES["decision"], "应包含 持有 术语规则"
    assert COMPLIANCE_RULES["decision"]["HOLD"] == "暂时持有", "HOLD 应转换为 暂时持有"
    assert COMPLIANCE_RULES["decision"]["持有"] == "暂时持有", "持有 应转换为 暂时持有"


# ========== 激进预测术语测试 ==========

def test_aggressive_terms():
    """测试激进预测术语转换"""
    from tradingagents.agents.compliance.rules import COMPLIANCE_RULES

    # 测试强烈看好类
    assert COMPLIANCE_RULES["aggressive"]["强烈看好"] == "关注度较高"
    assert COMPLIANCE_RULES["aggressive"]["强力推荐"] == "建议关注"
    assert COMPLIANCE_RULES["aggressive"]["强烈推荐"] == "建议关注"

    # 测试必涨类
    assert COMPLIANCE_RULES["aggressive"]["必涨"] == "存在上涨潜力"
    assert COMPLIANCE_RULES["aggressive"]["肯定涨"] == "存在上涨潜力"
    assert COMPLIANCE_RULES["aggressive"]["一定会涨"] == "存在上涨潜力"

    # 测试买入建议类
    assert COMPLIANCE_RULES["aggressive"]["建议买入"] == "可加入观察列表"
    assert COMPLIANCE_RULES["aggressive"]["建议购买"] == "可加入观察列表"
    assert COMPLIANCE_RULES["aggressive"]["建议加仓"] == "可考虑增加配置"

    # 测试时机类
    assert COMPLIANCE_RULES["aggressive"]["最佳买点"] == "值得关注的时点"
    assert COMPLIANCE_RULES["aggressive"]["最好时机"] == "值得关注的时间点"
    assert COMPLIANCE_RULES["aggressive"]["绝佳机会"] == "存在投资机会"

    # 测试其他激进表述
    assert COMPLIANCE_RULES["aggressive"]["不容错过"] == "值得关注"
    assert COMPLIANCE_RULES["aggressive"]["千载难逢"] == "较少见的机会"
    assert COMPLIANCE_RULES["aggressive"]["十年一遇"] == "值得关注的机会"


# ========== 保本承诺术语测试 ==========

def test_guarantee_terms():
    """测试保本承诺术语转换"""
    from tradingagents.agents.compliance.rules import COMPLIANCE_RULES

    # 测试稳赚类
    assert COMPLIANCE_RULES["guarantee"]["稳赚不赔"] == "存在投资机会"
    assert COMPLIANCE_RULES["guarantee"]["稳赚"] == "存在盈利机会"
    assert COMPLIANCE_RULES["guarantee"]["必赚"] == "存在盈利可能"

    # 测试无风险类
    assert COMPLIANCE_RULES["guarantee"]["无风险"] == "风险相对较低"
    assert COMPLIANCE_RULES["guarantee"]["零风险"] == "风险相对较低"
    assert COMPLIANCE_RULES["guarantee"]["毫无风险"] == "风险相对可控"

    # 测试绝对回报类
    assert COMPLIANCE_RULES["guarantee"]["绝对回报"] == "预期回报"
    assert COMPLIANCE_RULES["guarantee"]["必定盈利"] == "预期收益"
    assert COMPLIANCE_RULES["guarantee"]["保证收益"] == "预期收益"

    # 测试其他保本表述
    assert COMPLIANCE_RULES["guarantee"]["不会亏"] == "存在损失风险"
    assert COMPLIANCE_RULES["guarantee"]["不可能亏"] == "存在损失可能"
    assert COMPLIANCE_RULES["guarantee"]["百分之百赚"] == "盈利概率存在不确定性"


# ========== 系统提示词测试 ==========

def test_system_prompt_structure():
    """测试合规转换系统提示词结构"""
    from tradingagents.agents.compliance.rules import COMPLIANCE_SYSTEM_PROMPT

    # 验证提示词包含关键部分
    assert "金融合规助手" in COMPLIANCE_SYSTEM_PROMPT, "应明确角色定位"
    assert "转换原则" in COMPLIANCE_SYSTEM_PROMPT, "应包含转换原则"
    assert "术语映射规则" in COMPLIANCE_SYSTEM_PROMPT, "应包含术语映射规则"
    assert "工作流程" in COMPLIANCE_SYSTEM_PROMPT, "应包含工作流程"
    assert "注意事项" in COMPLIANCE_SYSTEM_PROMPT, "应包含注意事项"

    # 验证提示词包含所有分类
    assert "基础决策" in COMPLIANCE_SYSTEM_PROMPT, "应包含基础决策分类"
    assert "激进预测" in COMPLIANCE_SYSTEM_PROMPT, "应包含激进预测分类"
    assert "保本承诺" in COMPLIANCE_SYSTEM_PROMPT, "应包含保本承诺分类"


# ========== 实际转换功能测试（TDD - 预期失败）==========

@pytest.mark.asyncio
async def test_full_report_conversion(sample_report_content, mock_llm_client):
    """测试完整报告的合规转换（功能未实现，预期失败）"""
    from tradingagents.agents.compliance import compliance_agent

    # Mock LLM 响应
    mock_llm_client.invoke.return_value = MagicMock(
        content="这是转换后的报告内容..."
    )

    # TODO: 功能实现后测试
    # result = await compliance_agent.convert_report(
    #     report_content=sample_report_content,
    #     llm_client=mock_llm_client
    # )
    #
    # assert isinstance(result, str), "应返回字符串"
    # assert len(result) > 0, "转换后内容不应为空"
    # pytest.skip("功能尚未实现 - TDD Red Phase")


@pytest.mark.asyncio
async def test_timeout_fallback(sample_report_content, mock_llm_client):
    """测试超时时返回原始 HTML（功能未实现，预期失败）"""
    from tradingagents.agents.compliance import compliance_agent

    # Mock LLM 超时
    mock_llm_client.invoke.side_effect = asyncio.TimeoutError("LLM timeout")

    # TODO: 功能实现后测试
    # result = await compliance_agent.convert_report(
    #     report_content=sample_report_content,
    #     llm_client=mock_llm_client,
    #     timeout=1.0
    # )
    #
    # assert result == sample_report_content, "超时应返回原始内容"
    # pytest.skip("功能尚未实现 - TDD Red Phase")


@pytest.mark.asyncio
async def test_llm_failure_fallback(sample_report_content, mock_llm_client):
    """测试 LLM 失败时返回原始 HTML（功能未实现，预期失败）"""
    from tradingagents.agents.compliance import compliance_agent

    # Mock LLM 失败
    mock_llm_client.invoke.side_effect = Exception("LLM API error")

    # TODO: 功能实现后测试
    # result = await compliance_agent.convert_report(
    #     report_content=sample_report_content,
    #     llm_client=mock_llm_client
    # )
    #
    # assert result == sample_report_content, "LLM 失败应返回原始内容"
    # pytest.skip("功能尚未实现 - TDD Red Phase")


# ========== 真实报告场景测试 ==========

def test_real_report_contains_decision_terms(sample_report_content):
    """测试真实报告包含需要转换的决策术语"""
    # 验证真实报告包含需要转换的术语
    assert "买入" in sample_report_content, "真实报告应包含 '买入' 术语"
    assert "BUY" in sample_report_content, "真实报告应包含 'BUY' 术语"
    # 行198: `买入 (BUY)`
    # 行212: `分析师一致建议 买入`
    # 行349: `当前价位立即买入`
    # 行373: `为何买入`


def test_real_report_decision_terms_context(sample_report_content):
    """测试真实报告中决策术语的上下文"""
    # 验证特定行的内容
    assert "买入 (BUY)" in sample_report_content, "应包含 '买入 (BUY)' 组合"
    assert "分析师一致建议" in sample_report_content, "应包含分析师建议"
    assert "当前价位立即买入" in sample_report_content, "应包含买入时机建议"


# ========== 边界情况测试 ==========

def test_empty_report_handling():
    """测试空报告的处理（功能未实现，预期失败）"""
    from tradingagents.agents.compliance import compliance_agent

    # TODO: 功能实现后测试
    # result = compliance_agent.convert_report("")
    # assert result == "", "空报告应返回空字符串"
    # pytest.skip("功能尚未实现 - TDD Red Phase")


def test_report_without_compliance_terms():
    """测试不包含合规术语的报告（功能未实现，预期失败）"""
    from tradingagents.agents.compliance import compliance_agent

    clean_report = "<html><body>这是一份合规的财务分析报告</body></html>"

    # TODO: 功能实现后测试
    # result = compliance_agent.convert_report(clean_report)
    # assert result == clean_report, "无需转换时应返回原始内容"
    # pytest.skip("功能尚未实现 - TDD Red Phase")


def test_mixed_language_terms():
    """测试中英文混合术语的转换（功能未实现，预期失败）"""
    from tradingagents.agents.compliance import compliance_agent

    mixed_report = """
    <html>
    <body>
        <p>建议 BUY 这支股票</p>
        <p>强烈建议 SELL</p>
        <p>当前应该 HOLD</p>
    </body>
    </html>
    """

    # TODO: 功能实现后测试
    # from tradingagents.agents.compliance.rules import COMPLIANCE_RULES
    # result = compliance_agent.convert_report(mixed_report)
    #
    # # 验证中英文术语都被转换
    # assert "BUY" not in result
    # assert "SELL" not in result
    # assert "HOLD" not in result
    # assert "值得研究" in result or "关注度较高" in result
    # pytest.skip("功能尚未实现 - TDD Red Phase")


# ========== 小红书平台审核测试 ==========

def test_xiaohongshu_rules_exist():
    """测试小红书审核规则定义"""
    from tradingagents.agents.compliance.rules import (
        XIAOHONGSHU_PROHIBITED_CATEGORIES,
        XIAOHONGSHU_PROFIT_INDUCEMENT,
        XIAOHONGSHU_TRAFFIC_DIVERSION,
        XIAOHONGSHU_HIGH_RETURN_CLAIMS,
    )

    assert isinstance(XIAOHONGSHU_PROHIBITED_CATEGORIES, dict)
    assert "股票投资" in XIAOHONGSHU_PROHIBITED_CATEGORIES
    assert "股票" in XIAOHONGSHU_PROHIBITED_CATEGORIES["股票投资"]

    assert isinstance(XIAOHONGSHU_PROFIT_INDUCEMENT, list)
    assert "稳赚" in XIAOHONGSHU_PROFIT_INDUCEMENT
    assert "暴富" in XIAOHONGSHU_PROFIT_INDUCEMENT

    assert isinstance(XIAOHONGSHU_TRAFFIC_DIVERSION, list)
    assert "加微信" in XIAOHONGSHU_TRAFFIC_DIVERSION
    assert "进群" in XIAOHONGSHU_TRAFFIC_DIVERSION

    assert isinstance(XIAOHONGSHU_HIGH_RETURN_CLAIMS, list)
    assert "翻倍" in XIAOHONGSHU_HIGH_RETURN_CLAIMS
    assert "十倍" in XIAOHONGSHU_HIGH_RETURN_CLAIMS


def test_xiaohongshu_system_prompt():
    """测试小红书审核系统提示词"""
    from tradingagents.agents.compliance.rules import XIAOHONGSHU_REVIEW_PROMPT

    assert "小红书内容合规审核助手" in XIAOHONGSHU_REVIEW_PROMPT
    assert "禁止分享股票" in XIAOHONGSHU_REVIEW_PROMPT
    assert "禁止盈利诱导" in XIAOHONGSHU_REVIEW_PROMPT
    assert "禁止导流行为" in XIAOHONGSHU_REVIEW_PROMPT
    assert "禁止高回报噱头" in XIAOHONGSHU_REVIEW_PROMPT
    assert "is_violation" in XIAOHONGSHU_REVIEW_PROMPT
    assert "risk_level" in XIAOHONGSHU_REVIEW_PROMPT


def test_compliance_result_has_platform_fields():
    """测试 ComplianceResult 包含平台审核字段"""
    from tradingagents.agents.compliance import ComplianceResult

    result = ComplianceResult(
        is_success=True,
        original_html="test",
        compliant_html="test",
        is_violation=True,
        violation_categories=["股票投资"],
        violation_reasons=["包含股票术语"],
        risk_level="high",
        suggestions="删除股票相关内容"
    )

    assert result.is_violation is True
    assert result.violation_categories == ["股票投资"]
    assert result.violation_reasons == ["包含股票术语"]
    assert result.risk_level == "high"
    assert result.suggestions == "删除股票相关内容"


def test_review_for_platform_unsupported():
    """测试不支持的平台"""
    from tradingagents.agents.compliance import create_compliance_officer

    mock_client = MagicMock()
    officer = create_compliance_officer(mock_client)

    result = officer.review_for_platform("test content", platform="unsupported")

    assert result.is_success is False
    assert "Unsupported platform" in result.error_message
