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

# 工具函数1：列出目录下的文件及信息
def list_files(directory):
    """列出指定目录下的所有文件及其属性"""
    try:
        files = []
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                stat = os.stat(item_path)
                files.append({
                    "name": item,
                    "path": item_path,
                    "size": stat.st_size,
                    "last_modified": time.ctime(stat.st_mtime),
                    "is_file": True
                })
            elif os.path.isdir(item_path):
                files.append({
                    "name": item,
                    "path": item_path,
                    "is_file": False
                })
        return {"status": "success", "files": files}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 工具函数2：修改文件名字
def rename_file(directory, old_name, new_name):
    """修改指定目录下的文件名字"""
    try:
        old_path = os.path.join(directory, old_name)
        new_path = os.path.join(directory, new_name)
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            return {"status": "success", "message": f"文件已重命名为 {new_name}"}
        else:
            return {"status": "error", "message": "文件不存在"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 工具函数3：删除文件
def delete_file(directory, file_name):
    """删除指定目录下的文件"""
    try:
        file_path = os.path.join(directory, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            return {"status": "success", "message": "文件已删除"}
        else:
            return {"status": "error", "message": "文件不存在"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 工具函数4：新建文件并写入内容
def create_file(directory, file_name, content):
    """在指定目录下新建文件并写入内容"""
    try:
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"status": "success", "message": f"文件已创建并写入内容"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 工具函数5：读取文件内容
def read_file(directory, file_name):
    """读取指定目录下的文件内容"""
    try:
        file_path = os.path.join(directory, file_name)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"status": "success", "content": content}
        else:
            return {"status": "error", "message": "文件不存在"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 调用LLM API获取响应
def call_llm_api(base_url, api_key, model, messages, temperature=0.7, max_tokens=1000):
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
        "stream": False
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
    
    # 处理响应
    response_data = response.read().decode('utf-8')
    conn.close()
    
    try:
        return json.loads(response_data)
    except json.JSONDecodeError:
        return {"error": "Invalid response from API"}

# 执行工具调用
def execute_tool_call(tool_call):
    function_name = tool_call.get("name")
    arguments = tool_call.get("arguments", {})
    
    if function_name == "list_files":
        directory = arguments.get("directory")
        return list_files(directory)
    elif function_name == "rename_file":
        directory = arguments.get("directory")
        old_name = arguments.get("old_name")
        new_name = arguments.get("new_name")
        return rename_file(directory, old_name, new_name)
    elif function_name == "delete_file":
        directory = arguments.get("directory")
        file_name = arguments.get("file_name")
        return delete_file(directory, file_name)
    elif function_name == "create_file":
        directory = arguments.get("directory")
        file_name = arguments.get("file_name")
        content = arguments.get("content")
        return create_file(directory, file_name, content)
    elif function_name == "read_file":
        directory = arguments.get("directory")
        file_name = arguments.get("file_name")
        return read_file(directory, file_name)
    else:
        return {"status": "error", "message": f"未知的工具函数: {function_name}"}

def main():
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
    
    # 系统提示词，包含工具调用信息
    system_prompt = """
你是一个可以调用工具的AI助手。我需要你帮助我完成一些文件操作任务。

你可以使用以下工具：

1. list_files
   - 功能：列出指定目录下的所有文件及其属性
   - 参数：
     - directory: 字符串，要列出文件的目录路径
   - 返回：包含文件列表的JSON对象，每个文件包含name, path, size, last_modified, is_file等属性

2. rename_file
   - 功能：修改指定目录下的文件名字
   - 参数：
     - directory: 字符串，文件所在的目录路径
     - old_name: 字符串，原文件名字
     - new_name: 字符串，新文件名字
   - 返回：包含操作结果的JSON对象

3. delete_file
   - 功能：删除指定目录下的文件
   - 参数：
     - directory: 字符串，文件所在的目录路径
     - file_name: 字符串，要删除的文件名字
   - 返回：包含操作结果的JSON对象

4. create_file
   - 功能：在指定目录下新建文件并写入内容
   - 参数：
     - directory: 字符串，要创建文件的目录路径
     - file_name: 字符串，要创建的文件名字
     - content: 字符串，要写入文件的内容
   - 返回：包含操作结果的JSON对象

5. read_file
   - 功能：读取指定目录下的文件内容
   - 参数：
     - directory: 字符串，文件所在的目录路径
     - file_name: 字符串，要读取的文件名字
   - 返回：包含文件内容的JSON对象

当你需要执行文件操作时，请以JSON格式返回工具调用请求，格式如下：
{"toolcall": {"name": "工具函数名", "arguments": {"参数1": "值1", "参数2": "值2"}}}

例如，要列出D:\ai目录下的文件，你应该返回：
{"toolcall": {"name": "list_files", "arguments": {"directory": "D:\\ai"}}}

当我执行完工具调用后，会将执行结果以JSON格式返回给你，格式如下：
{"tool_result": {"status": "success", "result": {...}}}

请根据工具执行结果，为我提供最终的回答。
"""
    
    # 初始化聊天历史
    chat_history = [
        {"role": "system", "content": system_prompt}
    ]
    
    print("=== AI Tool Call Interface ===")
    print("Type your message and press Enter to interact with the AI.")
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
            
            # 调用LLM API
            response = call_llm_api(base_url, api_key, model, chat_history, temperature, max_tokens)
            
            # 处理API响应
            if "error" in response:
                print(f"Error: {response['error']}")
            elif "choices" in response and len(response["choices"]) > 0:
                message = response["choices"][0].get("message", {})
                content = message.get("content", "")
                
                # 检查是否是工具调用
                if content and content.strip().startswith("{"):
                    try:
                        tool_call_data = json.loads(content.strip())
                        if "toolcall" in tool_call_data:
                            tool_call = tool_call_data["toolcall"]
                            print(f"Executing tool: {tool_call['name']}")
                            
                            # 执行工具调用
                            tool_result = execute_tool_call(tool_call)
                            
                            # 将工具执行结果添加到聊天历史
                            tool_result_message = {
                                "role": "user",
                                "content": json.dumps({"tool_result": tool_result}, ensure_ascii=False)
                            }
                            chat_history.append(tool_result_message)
                            
                            # 再次调用LLM API获取最终响应
                            final_response = call_llm_api(base_url, api_key, model, chat_history, temperature, max_tokens)
                            if "choices" in final_response and len(final_response["choices"]) > 0:
                                final_message = final_response["choices"][0].get("message", {})
                                final_content = final_message.get("content", "")
                                print(final_content)
                                
                                # 添加最终响应到历史
                                chat_history.append({"role": "assistant", "content": final_content})
                        else:
                            print(content)
                            chat_history.append({"role": "assistant", "content": content})
                    except json.JSONDecodeError:
                        print(content)
                        chat_history.append({"role": "assistant", "content": content})
                else:
                    print(content)
                    chat_history.append({"role": "assistant", "content": content})
            
            print("-" * 50)
            
    except KeyboardInterrupt:
        print("\nExiting chat...")
        print("Thank you for using the AI tool call interface!")

if __name__ == "__main__":
    main()