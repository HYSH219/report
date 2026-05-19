import os
import json
import time
from http.client import HTTPSConnection
from urllib.parse import urlparse
import sys
import subprocess

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

# 工具函数6：访问网页并返回内容
def fetch_web_content(url):
    """访问指定URL并返回网页内容"""
    try:
        # 解析URL
        parsed_url = urlparse(url)
        host = parsed_url.netloc
        path = parsed_url.path or '/'
        if parsed_url.query:
            path += '?' + parsed_url.query
        
        # 构建请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # 发送请求
        conn = HTTPSConnection(host)
        conn.request("GET", path, headers=headers)
        response = conn.getresponse()
        
        # 处理响应
        content = response.read().decode('utf-8', errors='ignore')
        conn.close()
        
        return {"status": "success", "content": content, "status_code": response.status}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 工具函数7：查找聊天历史
def search_chat_history(query):
    """查找聊天历史并返回相关信息"""
    try:
        # 构建log文件路径
        log_dir = "/Users/atfa/Desktop/实验报告"
        log_file = os.path.join(log_dir, "log.txt")
        
        # 确保目录存在
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 读取log文件内容
        log_content = ""
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
        
        return {"status": "success", "log_content": log_content, "query": query}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 工具函数8：调用AnythingLLM API
def anythingllm_query(message):
    """使用curl命令调用AnythingLLM的聊天API接口"""
    try:
        # 加载环境变量
        env_vars = load_env()
        
        # 获取API密钥和工作区slug
        api_key = env_vars.get('ANYTHINGLLM_API_KEY')
        workspace_slug = env_vars.get('ANYTHINGLLM_WORKSPACE_SLUG')
        
        if not api_key or not workspace_slug:
            return {"status": "error", "message": "Missing ANYTHINGLLM_API_KEY or ANYTHINGLLM_WORKSPACE_SLUG in .env file"}
        
        # 构建API URL
        api_url = f"http://localhost:3001/api/v1/workspace/{workspace_slug}/chat"
        
        # 构建请求数据
        data = {
            "message": message
        }
        data_json = json.dumps(data, ensure_ascii=False)
        
        # 构建curl命令
        curl_cmd = [
            "curl",
            "-X", "POST",
            api_url,
            "-H", f"Authorization: Bearer {api_key}",
            "-H", "Content-Type: application/json",
            "-d", data_json
        ]
        
        # 执行curl命令
        result = subprocess.run(curl_cmd, capture_output=True, text=True, encoding='utf-8')
        
        # 处理响应
        if result.returncode == 0:
            try:
                response_data = json.loads(result.stdout)
                return {"status": "success", "response": response_data}
            except json.JSONDecodeError:
                return {"status": "error", "message": f"Invalid JSON response: {result.stdout}"}
        else:
            return {"status": "error", "message": f"Curl error: {result.stderr}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 工具函数9：加载技能内容
def load_skill_content(skill_name):
    """加载指定技能的SKILL.md文件内容（YAML front matter之后的部分）"""
    try:
        # 构建技能文件路径
        skill_dir = os.path.join(os.path.dirname(__file__), 'skills', skill_name)
        skill_file = os.path.join(skill_dir, 'SKILL.md')
        
        # 检查文件是否存在
        if not os.path.exists(skill_file):
            return {"status": "error", "message": f"Skill file not found: {skill_file}"}
        
        # 读取文件内容
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析YAML front matter，返回之后的内容
        # YAML front matter以---开始和结束
        if content.startswith('---'):
            # 找到第二个---
            end_index = content.find('---', 3)
            if end_index != -1:
                # 返回front matter之后的内容
                return {"status": "success", "content": content[end_index + 3:].strip()}
        
        # 如果没有YAML front matter，返回整个内容
        return {"status": "success", "content": content.strip()}
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
    elif function_name == "fetch_web_content":
        url = arguments.get("url")
        return fetch_web_content(url)
    elif function_name == "search_chat_history":
        query = arguments.get("query")
        return search_chat_history(query)
    elif function_name == "anythingllm_query":
        message = arguments.get("message")
        return anythingllm_query(message)
    elif function_name == "load_skill_content":
        skill_name = arguments.get("skill_name")
        return load_skill_content(skill_name)
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
```json
{
  "skills": [
    {"name": "list_files", "description": "列出指定目录下的所有文件及其属性"},
    {"name": "rename_file", "description": "修改指定目录下的文件名字"},
    {"name": "delete_file", "description": "删除指定目录下的文件"},
    {"name": "create_file", "description": "在指定目录下新建文件并写入内容"},
    {"name": "read_file", "description": "读取指定目录下的文件内容"},
    {"name": "fetch_web_content", "description": "访问指定URL并返回网页内容"},
    {"name": "search_chat_history", "description": "查找聊天历史并返回相关信息"},
    {"name": "anythingllm_query", "description": "调用AnythingLLM的聊天API接口，查询文档仓库中的信息"},
    {"name": "load_skill_content", "description": "加载指定技能的SKILL.md文件内容"},
    {"name": "notice", "description": "用于撰写、修改、润色通知的技能"}
  ]
}
```

你是一个可以调用工具的AI助手。我需要你帮助我完成一些文件操作任务，同时处理聊天历史管理和搜索。

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

6. fetch_web_content
   - 功能：访问指定URL并返回网页内容
   - 参数：
     - url: 字符串，要访问的网页URL
   - 返回：包含网页内容、状态码的JSON对象

7. search_chat_history
   - 功能：查找聊天历史并返回相关信息
   - 参数：
     - query: 字符串，搜索查询
   - 返回：包含log文件内容和查询的JSON对象

8. anythingllm_query
   - 功能：调用AnythingLLM的聊天API接口，查询文档仓库中的信息
   - 参数：
     - message: 字符串，要发送的查询消息
   - 返回：包含API响应的JSON对象

9. load_skill_content
   - 功能：加载指定技能的SKILL.md文件内容（YAML front matter之后的部分）
   - 参数：
     - skill_name: 字符串，技能名称
   - 返回：包含技能内容的JSON对象

当你需要执行文件操作时，请以JSON格式返回工具调用请求，格式如下：
{"toolcall": {"name": "工具函数名", "arguments": {"参数1": "值1", "参数2": "值2"}}}

例如，要列出D:\ai目录下的文件，你应该返回：
{"toolcall": {"name": "list_files", "arguments": {"directory": "D:\\ai"}}}

当我执行完工具调用后，会将执行结果以JSON格式返回给你，格式如下：
{"tool_result": {"status": "success", "result": {...}}}

请根据工具执行结果，为我提供最终的回答。

特别说明：
1. 当用户发送的信息以"/search"开头，或用户表达了"查找聊天历史"的意思，或你认为应该查找聊天历史时，请调用search_chat_history工具。
2. 当用户提到"文档仓库"、"文件仓库"、"仓库"时，请调用anythingllm_query工具。
3. 当用户要求撰写通知、修改通知、润色通知时，请调用load_skill_content工具加载notice技能，然后根据技能要求执行。
4. 每五次聊天后，请提取关键信息，按照5W规则（谁Who、做了什么事What、什么时候When（可选）、在何处Where（可选）、为什么要做这个事Why（可选））提取多条关键信息，并记录到用户的本地电脑 /Users/atfa/Desktop/实验报告/log.txt 文件中。
5. 当聊天历史超过5轮，或聊天上下文长度超过3k时，需要主动触发聊天记录总结，对前70%左右的内容进行压缩，保留最后30%左右的内容原文。
"""
    
    # 初始化聊天历史
    chat_history = [
        {"role": "system", "content": system_prompt}
    ]
    
    # 初始化聊天轮数计数器
    chat_rounds = 0
    
    print("=== AI Tool Call Interface ===")
    print("Type your message and press Enter to interact with the AI.")
    print("Press Ctrl+C to exit.")
    print("-" * 50)
    
    try:
        while True:
            # 获取用户输入
            user_input = input("You: ")
            
            # 检查是否需要搜索聊天历史
            if user_input.startswith("/search") or "查找聊天历史" in user_input:
                # 调用搜索工具
                tool_call = {"name": "search_chat_history", "arguments": {"query": user_input}}
                print(f"Executing tool: {tool_call['name']}")
                
                # 执行工具调用
                tool_result = execute_tool_call(tool_call)
                
                # 将工具执行结果添加到聊天历史
                tool_result_message = {
                    "role": "user",
                    "content": json.dumps({"tool_result": tool_result}, ensure_ascii=False)
                }
                chat_history.append(tool_result_message)
                
                # 调用LLM API获取最终响应
                response = call_llm_api(base_url, api_key, model, chat_history, temperature, max_tokens)
                if "choices" in response and len(response["choices"]) > 0:
                    message = response["choices"][0].get("message", {})
                    content = message.get("content", "")
                    print(content)
                    chat_history.append({"role": "assistant", "content": content})
                else:
                    print("Error: No response from API")
                
                print("-" * 50)
                continue
            
            # 添加用户消息到历史
            chat_history.append({"role": "user", "content": user_input})
            chat_rounds += 1
            
            # 计算聊天上下文长度
            context_length = sum(len(msg.get("content", "")) for msg in chat_history)
            
            # 检查是否需要触发聊天记录总结
            if len(chat_history) - 1 > 5 or context_length > 3000:  # 减1是因为系统消息不计入轮数
                # 对聊天记录进行总结
                # 保留系统消息
                system_msg = chat_history[0]
                # 计算分割点
                total_msgs = len(chat_history) - 1  # 减1是因为系统消息
                split_point = int(total_msgs * 0.7)
                # 前70%的消息
                first_part = chat_history[1:split_point+1]
                # 后30%的消息
                second_part = chat_history[split_point+1:]
                
                # 构建总结提示
                summary_prompt = "请对以下聊天记录进行总结，保持关键信息：\n"
                for msg in first_part:
                    summary_prompt += f"{msg['role']}: {msg['content']}\n"
                
                # 调用LLM进行总结
                summary_messages = [
                    {"role": "system", "content": "你是一个聊天记录总结助手，需要对聊天内容进行简洁的总结。"},
                    {"role": "user", "content": summary_prompt}
                ]
                summary_response = call_llm_api(base_url, api_key, model, summary_messages, temperature, max_tokens)
                
                if "choices" in summary_response and len(summary_response["choices"]) > 0:
                    summary = summary_response["choices"][0].get("message", {}).get("content", "")
                    
                    # 重建聊天历史：系统消息 + 总结 + 后30%消息
                    new_chat_history = [system_msg]
                    new_chat_history.append({"role": "assistant", "content": f"[聊天记录总结]\n{summary}"})
                    new_chat_history.extend(second_part)
                    chat_history = new_chat_history
            
            # 检查是否需要提取关键信息
            if chat_rounds % 5 == 0:
                # 构建提取关键信息的提示
                extraction_prompt = "请从以下聊天记录中提取关键信息，按照5W规则（谁Who、做了什么事What、什么时候When（可选）、在何处Where（可选）、为什么要做这个事Why（可选））提取多条关键信息：\n"
                for msg in chat_history[1:]:  # 跳过系统消息
                    extraction_prompt += f"{msg['role']}: {msg['content']}\n"
                
                # 调用LLM提取关键信息
                extraction_messages = [
                    {"role": "system", "content": "你是一个信息提取助手，需要从聊天记录中按照5W规则提取关键信息。"},
                    {"role": "user", "content": extraction_prompt}
                ]
                extraction_response = call_llm_api(base_url, api_key, model, extraction_messages, temperature, max_tokens)
                
                if "choices" in extraction_response and len(extraction_response["choices"]) > 0:
                    key_info = extraction_response["choices"][0].get("message", {}).get("content", "")
                    
                    # 写入log文件
                    log_dir = "/Users/atfa/Desktop/实验报告"
                    log_file = os.path.join(log_dir, "log.txt")
                    
                    # 确保目录存在
                    if not os.path.exists(log_dir):
                        os.makedirs(log_dir)
                    
                    # 写入关键信息
                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(f"\n=== 第{chat_rounds}轮聊天关键信息 ===\n")
                        f.write(key_info)
                        f.write("\n")
            
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

# 测试函数
def test_notice_skill():
    """测试notice技能的功能"""
    # 测试load_skill_content函数
    print("=== 测试load_skill_content函数 ===")
    result = load_skill_content("notice")
    print(f"Load skill content result: {result}")
    
    print("\n" + "-" * 50 + "\n")
    
    # 模拟测试场景1：用户未提供部门信息
    print("=== 测试场景1：用户未提供部门信息 ===")
    print("用户请求：撰写关于五一节放假的通知")
    print("预期结果：通知应该以'XX部通知'开头")
    print("示例输出：")
    print("XX部通知\n\n全体员工：\n\n根据国家法定节假日安排，现将2026年五一节放假安排通知如下：\n\n一、放假时间：2026年5月1日至5月5日，共5天。\n二、工作安排：4月26日（星期日）、5月9日（星期六）正常上班。\n三、注意事项：\n1. 请各部门做好放假前的安全检查工作，关闭不必要的电器设备。\n2. 放假期间外出的员工请注意个人安全，遵守交通规则。\n3. 如有紧急工作需要处理，请及时联系部门负责人。\n\n祝大家节日快乐！\n\nXX部\n2026年4月XX日")
    
    print("\n" + "-" * 50 + "\n")
    
    # 模拟测试场景2：用户提供部门信息（销售部）
    print("=== 测试场景2：用户提供部门信息（销售部） ===")
    print("用户请求：我是销售部的，撰写关于五一节放假的通知")
    print("预期结果：通知应该以'销售部通知'开头")
    print("示例输出：")
    print("销售部通知\n\n全体销售人员：\n\n根据国家法定节假日安排，现将2026年五一节放假安排通知如下：\n\n一、放假时间：2026年5月1日至5月5日，共5天。\n二、工作安排：4月26日（星期日）、5月9日（星期六）正常上班。\n三、注意事项：\n1. 请各位销售人员在放假前与客户做好沟通，确保假期期间的业务衔接。\n2. 放假期间外出的员工请注意个人安全，遵守交通规则。\n3. 如有紧急客户需求，请及时联系部门负责人。\n\n祝大家节日快乐！\n\n销售部\n2026年4月XX日")

if __name__ == "__main__":
    # 运行测试
    test_notice_skill()
    # 运行主程序
    # main()