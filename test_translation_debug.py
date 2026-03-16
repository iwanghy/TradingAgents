#!/usr/bin/env python3
"""
详细调试翻译功能
"""

import os
from dotenv import load_dotenv
from tradingagents.llm_clients.factory import create_llm_client
from tradingagents.default_config import DEFAULT_CONFIG
from langchain_core.messages import HumanMessage, SystemMessage

def main():
    # 加载环境变量
    load_dotenv()

    # 检查 API Key
    if not os.environ.get("ZHIPU_API_KEY"):
        print("❌ 错误: 未找到 ZHIPU_API_KEY")
        return

    print("="*60)
    print("🐛 翻译功能详细调试")
    print("="*60)

    # 配置
    config = DEFAULT_CONFIG.copy()
    provider = "zhipu"
    model = "glm-4.5-air"

    print(f"\n📊 配置:")
    print(f"  - 提供商: {provider}")
    print(f"  - 模型: {model}")
    print(f"  - API Key: {os.environ.get('ZHIPU_API_KEY')[:20]}...")

    # 创建 LLM 客户端
    print(f"\n🔧 创建 LLM 客户端...")
    try:
        llm_client = create_llm_client(provider=provider, model=model)
        print(f"✅ LLM 客户端创建成功")
        print(f"   类型: {type(llm_client)}")
    except Exception as e:
        print(f"❌ LLM 客户端创建失败: {e}")
        import traceback
        traceback.print_exc()
        return

    # 获取底层 LLM
    print(f"\n🔧 获取底层 LLM 实例...")
    try:
        llm = llm_client.get_llm()
        print(f"✅ LLM 实例获取成功")
        print(f"   类型: {type(llm)}")
        print(f"   模型: {llm.model_name}")
    except Exception as e:
        print(f"❌ LLM 实例获取失败: {e}")
        import traceback
        traceback.print_exc()
        return

    # 测试文本
    test_text = """
    Technical Analysis Report for NVDA

    The stock is showing a strong bullish trend.

    Recommendation: BUY
    """

    print(f"\n📝 测试文本:")
    print(f"   长度: {len(test_text)} 字符")
    print(f"   内容: {test_text[:100]}...")

    # 准备消息
    print(f"\n💬 准备消息...")
    messages = [
        SystemMessage(content="你是一个专业的金融翻译专家。请将提供的英文交易分析报告准确翻译为中文。"),
        HumanMessage(content=test_text),
    ]
    print(f"✅ 消息准备成功")
    print(f"   消息数量: {len(messages)}")
    print(f"   System: {messages[0].content[:50]}...")
    print(f"   Human: {messages[1].content[:50]}...")

    # 调用 API
    print(f"\n🔄 调用 API...")
    print(f"-"*60)

    try:
        result = llm.invoke(messages)

        print(f"\n✅ API 调用成功!")
        print(f"-"*60)
        print(f"结果类型: {type(result)}")
        print(f"内容类型: {type(result.content)}")
        print(f"内容长度: {len(result.content)}")
        print(f"\n翻译结果:")
        print(f"-"*60)
        print(result.content)
        print(f"-"*60)

    except Exception as e:
        print(f"\n❌ API 调用失败!")
        print(f"-"*60)
        print(f"错误类型: {type(e).__name__}")
        print(f"错误消息: {str(e)}")

        # 打印完整的错误堆栈
        print(f"\n详细错误信息:")
        print(f"-"*60)
        import traceback
        traceback.print_exc()
        print(f"-"*60)

        # 分析错误
        error_str = str(e).lower()
        if "rate" in error_str or "limit" in error_str:
            print(f"\n🔍 错误分析: API 限流")
        elif "400" in error_str or "prompt" in error_str:
            print(f"\n🔍 错误分析: 内容格式问题")
        elif "401" in error_str or "auth" in error_str:
            print(f"\n🔍 错误分析: 认证失败")
        elif "404" in error_str:
            print(f"\n🔍 错误分析: 模型不存在")
        else:
            print(f"\n🔍 错误分析: 未知错误")

if __name__ == "__main__":
    main()
