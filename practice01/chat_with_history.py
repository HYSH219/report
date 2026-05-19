import os
import json
import time
from http.client import HTTPSConnection
from urllib.parse import urlparse
import sys

# 读取.env文件
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    # 移除引号
                    if (value.startswith('"') and value.endswith('"')) or (value.startswith('\'') and value.endswith('\'')):
                        value = value[1:-1]
                    env_vars[key] = value
    return env_vars

# 流式发送请求到LLM API
def stream_llm_api(base_url, api_key, model, messages, temperature=0.7, max_tokens=1000):
    # 解析URL
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = parsed_url.path or '/'
    if not path.endswith('/'):
        path += '/'
    path += 'chat/completions'
    
    # 构建请求数据
    data = {
        "model": model,
        "messages": messages,
        "temperature": float(temperature),
        "max_tokens": int(max_tokens),
        "stream": True
    }
    
    # 构建请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 发送请求
    conn = HTTPSConnection(host)
    conn.request("POST", path, json.dumps(data), headers)
    response = conn.getresponse()
    
    # 处理流式响应
    full_response = ""
    for line in response:
        line = line.decode('utf-8').strip()
        if line and line.startswith('data: '):
            data_part = line[6:]
            if data_part == '[DONE]':
                break
            try:
                chunk = json.loads(data_part)
                if 'choices' in chunk and len(chunk['choices']) > 0:
                    delta = chunk['choices'][0].get('delta', {})
                    if 'content' in delta:
                        content = delta['content']
                        print(content, end='', flush=True)
                        full_response += content
            except json.JSONDecodeError:
                pass
    
    conn.close()
    print()  # 换行
    return full_response

def main():
    # 加载环境变量
    env_vars = load_env()
    
    # 检查必要的P环境变量
    if 'BASE_URL' not in env_vars or 'API_KEY' not in env_vars or 'MODEL' not in env_vars:
        print("Error: Missing required environment variables. Please create a .env file based on env.example.")
        exit(1)
    
    # 获取配置
    base_url = env_vars.get('BASE_URL')
    api_key = env_vars.get('API_KEY')
    model = env_vars.get('MODEL')
    temperature = env_vars.get('TEMPERATURE', 0.7)
    max_tokens = env_vars.get('MAX_TOKENS', 1000)
    
    # 初始化聊天历史
    chat_history = []
    
    print("=== AI Chat Interface ===")
    print("Type your message and press Enter to chat with the AI.")
    print("Press Ctrl+C to exit.")
    print("-" * 50)
    
    try:
        while True:
            # 获取用户输入
            user_input = input("You: ")
            
            # 添加用户消息到历史
            chat_history.append({"role": "user", "content": user_input})
            
            # 限制历史消息长度，避免token超限
            if len(chat_history) > 10:  # 保留最近10条消息
                chat_history = chat_history[-10:]
            
            print("AI: ", end='', flush=True)
            
            # 调用流式API
            ai_response = stream_llm_api(base_url, api_key, model, chat_history, temperature, max_tokens)
            
            # 添加AI响应到历史
            chat_history.append({"role": "assistant", "content": ai_response})
            
            print("-" * 50)
            
    except KeyboardInterrupt:
        print("\nExiting chat...")
        print("Thank you for using the AI chat interface!")

if __name__ == "__main__":
    main()
