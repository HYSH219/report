#!/usr/bin/env python3
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tool_client import load_env, execute_chained_tool_call

def run_tests():
    # 加载环境变量
    env_vars = load_env()
    
    # 获取配置
    base_url = env_vars.get('BASE_URL', 'https://api.openai.com/v1')
    api_key = env_vars.get('API_KEY', 'test-key')
    model = env_vars.get('MODEL', 'gpt-3.5-turbo')
    
    print("=== 链式工具调用测试 ===")
    print("=" * 60)
    
    # 测试1：文件搜索链式调用
    print("\n测试1：文件搜索链式调用")
    print("-" * 60)
    user_request1 = "请查找 practice06 目录下所有包含'def'关键词的文件，并总结这些文件的主要内容"
    print(f"用户请求: {user_request1}")
    context1 = execute_chained_tool_call(base_url, api_key, model, user_request1)
    print(f"测试1结果: {context1.final_answer}")
    
    # 测试2：多文件操作
    print("\n测试2：多文件操作")
    print("-" * 60)
    user_request2 = f"读取 {os.path.dirname(os.path.abspath(__file__))}\\1.txt 和 {os.path.dirname(os.path.abspath(__file__))}\\2.txt 两个文件，文件内容的都是正整数，把两个数相加的和写入 result.txt 文件。"
    print(f"用户请求: {user_request2}")
    context2 = execute_chained_tool_call(base_url, api_key, model, user_request2)
    print(f"测试2结果: {context2.final_answer}")
    
    # 测试3：网页处理链式调用
    print("\n测试3：网页处理链式调用")
    print("-" * 60)
    user_request3 = "访问 `https://www.nsu.edu.cn/HTML/news/2024/06/article_3974.html` 并总结页面内容，保存到 practice07/summary.txt"
    print(f"用户请求: {user_request3}")
    context3 = execute_chained_tool_call(base_url, api_key, model, user_request3)
    print(f"测试3结果: {context3.final_answer}")
    
    print("\n" + "=" * 60)
    print("所有测试完成！")

if __name__ == "__main__":
    run_tests()