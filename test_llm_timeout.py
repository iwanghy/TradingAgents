"""
测试LLM调用超时和重试机制

当LLM服务器负载高时，调用可能会卡住。这个脚本测试新的超时保护功能。
"""
import os
from tradingagents.llm_clients.factory import create_llm_client

# 设置API密钥（使用环境变量或测试密钥）
# os.environ["ZHIPU_API_KEY"] = "your_api_key_here"

print("=== LLM调用超时测试 ===\n")

# 创建带超时保护的客户端
# 方式1：通过配置创建
config = {
    "llm_provider": "zhipu",
    "deep_think_llm": "glm-4.5-air",
    "llm_invoke_timeout": 120,  # 设置调用超时120秒
    "max_llm_retries": 3,
}

print(f"配置参数:")
print(f"  - provider: {config['llm_provider']}")
print(f"  - model: {config['deep_think_llm']}")
print(f"  - invoke_timeout: {config['llm_invoke_timeout']}s")
print(f"  - max_retries: {config['max_llm_retries']}")
print()

# 创建客户端
try:
    client = create_llm_client(
        provider=config["llm_provider"],
        model=config["deep_think_llm"],
        invoke_timeout=config["llm_invoke_timeout"],
        timeout=60,  # HTTP请求超时
        max_retries=2,  # HTTP请求重试
    )
    print(f"✓ 客户端创建成功")
    print(f"  超时设置: {client.invoke_timeout}s")
    print()
except Exception as e:
    print(f"✗ 客户端创建失败: {e}")
    exit(1)

# 测试调用（使用 invoke_with_timeout 方法）
from langchain_core.messages import HumanMessage, SystemMessage

messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="Say hello in one word."),
]

print("测试调用（带超时保护）...")
print("-" * 50)

try:
    # 使用新的带超时的调用方法
    result = client.invoke_with_timeout(messages, max_retries=2)
    print(f"✓ 调用成功")
    print(f"  响应: {result.content[:100]}...")
except TimeoutError as e:
    print(f"✗ 调用超时: {e}")
except Exception as e:
    print(f"✗ 调用失败: {type(e).__name__}: {e}")

print()
print("=== 测试完成 ===")

print("""
说明:
1. invoke_with_timeout() 方法会自动处理超时和重试
2. 如果超时，会记录 [LLM_TIMEOUT] 日志并自动重试
3. 所有重试都失败后，会抛出 TimeoutError
4. 可以通过 config["llm_invoke_timeout"] 调整超时时间
""")
