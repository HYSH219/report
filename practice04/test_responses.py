#!/usr/bin/env python3
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tool_call_client import mock_llm_response

# 测试不同的用户输入
test_messages = [
    [{"role": "user", "content": "你好"}],
    [{"role": "user", "content": "我叫什么名字"}],
    [{"role": "user", "content": "你是谁"},
     {"role": "assistant", "content": "我是你的AI助手"},
     {"role": "user", "content": "现在几点了"}],
    [{"role": "user", "content": "谢谢你"}]
]

print("=== 测试模拟LLM响应功能 ===\n")

for i, messages in enumerate(test_messages, 1):
    user_input = messages[-1]["content"]
    response = mock_llm_response(messages)
    ai_response = response["choices"][0]["message"]["content"]
    
    print(f"测试 {i}:")
    print(f"用户: {user_input}")
    print(f"AI: {ai_response}")
    print("-" * 50)