import os
import json
import time
from http.client import HTTPSConnection
from urllib.parse import urlparse

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

# 发送请求到LLM API
def call_llm_api(base_url, api_key, model, prompt, temperature=0.7, max_tokens=1000):
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
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": float(temperature),
        "max_tokens": int(max_tokens),
        "stream": False
    }
    
    # 构建请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 发送请求
    start_time = time.time()
    conn = HTTPSConnection(host)
    conn.request("POST", path, json.dumps(data), headers)
    response = conn.getresponse()
    end_time = time.time()
    
    # 读取响应
    response_data = response.read().decode('utf-8')
    conn.close()
    
    # 解析响应
    response_json = json.loads(response_data)
    
    # 计算统计信息
    total_time = end_time - start_time
    if 'choices' in response_json and len(response_json['choices']) > 0:
        completion = response_json['choices'][0]['message']['content']
        prompt_tokens = response_json['usage']['prompt_tokens']
        completion_tokens = response_json['usage']['total_tokens'] - prompt_tokens
        total_tokens = response_json['usage']['total_tokens']
        
        # 计算速度
        tokens_per_second = total_tokens / total_time
        
        return {
            'completion': completion,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': total_tokens,
            'total_time': total_time,
            'tokens_per_second': tokens_per_second
        }
    else:
        return {'error': response_json.get('error', 'Unknown error')}

if __name__ == "__main__":
    # 加载环境变量
    env_vars = load_env()
    
    # 检查必要的环境变量
    if 'BASE_URL' not in env_vars or 'API_KEY' not in env_vars or 'MODEL' not in env_vars:
        print("Error: Missing required environment variables. Please create a .env file based on env.example.")
        exit(1)
    
    # 获取配置
    base_url = env_vars.get('BASE_URL')
    api_key = env_vars.get('API_KEY')
    model = env_vars.get('MODEL')
    temperature = env_vars.get('TEMPERATURE', 0.7)
    max_tokens = env_vars.get('MAX_TOKENS', 1000)
    
    # 测试提示
    test_prompt = "Hello, how are you? Please provide a brief response."
    
    print("Testing LLM API...")
    print(f"Model: {model}")
    print(f"Base URL: {base_url}")
    print(f"Prompt: {test_prompt}")
    print("-" * 50)
    
    # 调用API
    result = call_llm_api(base_url, api_key, model, test_prompt, temperature, max_tokens)
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Response: {result['completion']}")
        print("-" * 50)
        print(f"Prompt tokens: {result['prompt_tokens']}")
        print(f"Completion tokens: {result['completion_tokens']}")
        print(f"Total tokens: {result['total_tokens']}")
        print(f"Total time: {result['total_time']:.2f} seconds")
        print(f"Tokens per second: {result['tokens_per_second']:.2f}")
