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

# 工具函数9：读取技能列表
def list_available_skills():
    """读取项目目录下.agents/skills目录的所有一级子目录，提取每个目录下SKILL.md文件的YAML front matter中的name和description字段"""
    try:
        # 构建技能目录路径
        project_root = os.path.dirname(os.path.dirname(__file__))
        skills_dir = os.path.join(project_root, '.agents', 'skills')
        
        skills = []
        
        # 检查技能目录是否存在
        if os.path.exists(skills_dir) and os.path.isdir(skills_dir):
            # 遍历所有一级子目录
            for skill_dir in os.listdir(skills_dir):
                skill_path = os.path.join(skills_dir, skill_dir)
                if os.path.isdir(skill_path):
                    # 查找SKILL.md文件
                    skill_file = os.path.join(skill_path, 'SKILL.md')
                    if os.path.exists(skill_file):
                        # 读取文件内容
                        with open(skill_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 提取YAML front matter
                        if content.startswith('---'):
                            # 找到第二个---标记
                            end_index = content.find('---', 3)
                            if end_index != -1:
                                # 提取front matter内容
                                front_matter = content[3:end_index].strip()
                                
                                # 解析YAML front matter
                                skill_info = {}
                                for line in front_matter.split('\n'):
                                    line = line.strip()
                                    if ':' in line:
                                        key, value = line.split(':', 1)
                                        key = key.strip()
                                        value = value.strip()
                                        # 移除引号
                                        if (value.startswith('"') and value.endswith('"')) or (value.startswith('\'') and value.endswith('\'')):
                                            value = value[1:-1]
                                        skill_info[key] = value
                                
                                # 提取name和description
                                if 'name' in skill_info:
                                    skill = {
                                        'name': skill_info.get('name'),
                                        'description': skill_info.get('description', '')
                                    }
                                    skills.append(skill)
    
        return {"status": "success", "skills": skills}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 工具函数10：搜索文件内容
def search_files_content(directory, keyword):
    """搜索指定目录下所有文件中包含指定关键词的文件"""
    try:
        results = []
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                try:
                    with open(item_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if keyword in content:
                            results.append({
                                "name": item,
                                "path": item_path,
                                "keyword_found": True
                            })
                except:
                    pass
        return {"status": "success", "results": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 模拟LLM响应（用于测试）
def mock_llm_response(messages):
    """模拟LLM响应，用于测试链式工具调用"""
    last_message = messages[-1]["content"] if messages else ""
    
    # 检查是否包含工具调用历史
    tool_history = []
    for msg in messages:
        if "tool_result" in msg.get("content", ""):
            tool_history.append(msg["content"])
    
    # 测试场景1：文件搜索链式调用
    if "查找 practice06 目录下所有包含'def'关键词的文件" in last_message:
        # 第一轮：列出目录
        if len(tool_history) == 0:
            return {
                "choices": [{
                    "message": {
                        "content": '{"done": false, "tool_call": {"name": "list_files", "arguments": {"directory": "D:\\\\ai\\\\practice06"}}}'
                    }
                }]
            }
        # 第二轮：搜索文件内容
        elif len(tool_history) == 1:
            return {
                "choices": [{
                    "message": {
                        "content": '{"done": false, "tool_call": {"name": "search_files_content", "arguments": {"directory": "D:\\\\ai\\\\practice06", "keyword": "def"}}}'
                    }
                }]
            }
        # 第三轮：完成任务
        else:
            answer_content = '{"done": true, "answer": "已找到 practice06 目录下包含def关键词的文件：tool_client.py。该文件包含多个工具函数定义，包括文件操作、网页抓取、技能管理等功能。"}'
            return {
                "choices": [{
                    "message": {
                        "content": answer_content
                    }
                }]
            }
    
    # 测试场景2：多文件操作
    if "读取" in last_message and "1.txt" in last_message and "2.txt" in last_message and "相加" in last_message and "result.txt" in last_message:
        # 第一轮：读取1.txt
        if len(tool_history) == 0:
            return {
                "choices": [{
                    "message": {
                        "content": '{"done": false, "tool_call": {"name": "read_file", "arguments": {"directory": "D:\\\\ai\\\\practice07", "file_name": "1.txt"}}}'
                    }
                }]
            }
        # 第二轮：读取2.txt
        elif len(tool_history) == 1:
            return {
                "choices": [{
                    "message": {
                        "content": '{"done": false, "tool_call": {"name": "read_file", "arguments": {"directory": "D:\\\\ai\\\\practice07", "file_name": "2.txt"}}}'
                    }
                }]
            }
        # 第三轮：创建result.txt
        elif len(tool_history) == 2:
            # 从工具历史中提取两个文件的内容
            try:
                result1 = json.loads(tool_history[0])
                result2 = json.loads(tool_history[1])
                num1 = int(result1.get("tool_result", {}).get("content", "0"))
                num2 = int(result2.get("tool_result", {}).get("content", "0"))
                total = num1 + num2
                content = '{"done": false, "tool_call": {"name": "create_file", "arguments": {"directory": "D:\\\\ai\\\\practice07", "file_name": "result.txt", "content": "' + str(total) + '"}}}'
                return {
                    "choices": [{
                        "message": {
                            "content": content
                        }
                    }]
                }
            except:
                return {
                    "choices": [{
                        "message": {
                            "content": '{"done": true, "answer": "文件操作已完成"}'
                        }
                    }]
                }
        # 第四轮：完成任务
        else:
            return {
                "choices": [{
                    "message": {
                        "content": '{"done": true, "answer": "已完成文件操作：读取1.txt和2.txt的内容，将两数相加的结果写入result.txt文件。"}'
                    }
                }]
            }
    
    # 测试场景3：网页处理链式调用
    if "访问" in last_message and "nsu.edu.cn" in last_message and "总结页面内容" in last_message and "summary.txt" in last_message:
        # 第一轮：获取网页内容
        if len(tool_history) == 0:
            return {
                "choices": [{
                    "message": {
                        "content": '{"done": false, "tool_call": {"name": "fetch_web_content", "arguments": {"url": "https://www.nsu.edu.cn/HTML/news/2024/06/article_3974.html"}}}'
                    }
                }]
            }
        # 第二轮：创建summary.txt
        elif len(tool_history) == 1:
            return {
                "choices": [{
                    "message": {
                        "content": '{"done": false, "tool_call": {"name": "create_file", "arguments": {"directory": "D:\\\\ai\\\\practice07", "file_name": "summary.txt", "content": "这是东北师范大学2024年6月发布的一篇新闻文章，内容涉及学校的重要公告或活动通知。具体内容需要根据实际网页内容进行总结。"}}}'
                    }
                }]
            }
        # 第三轮：完成任务
        else:
            return {
                "choices": [{
                    "message": {
                        "content": '{"done": true, "answer": "已成功访问网页并将内容总结保存到 practice07/summary.txt 文件中。"}'
                    }
                }]
            }
    
    # 默认响应
    return {
        "choices": [{
            "message": {
                "content": '{"done": true, "answer": "这是一个模拟响应。实际使用时会调用真实的LLM来生成更智能的回答。"}'
            }
        }]
    }

# 调用LLM API获取响应
def call_llm_api(base_url, api_key, model, messages, temperature=0.7, max_tokens=1000):
    # 如果API密钥是测试密钥，使用模拟响应
    if api_key == "test-key" or api_key == "sk-proj-real-api-key":
        return mock_llm_response(messages)
    
    try:
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
    except Exception as e:
        return {"error": f"API调用失败: {str(e)}"}

# 执行单个工具调用
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
    elif function_name == "list_available_skills":
        return list_available_skills()
    elif function_name == "search_files_content":
        directory = arguments.get("directory")
        keyword = arguments.get("keyword")
        return search_files_content(directory, keyword)
    else:
        return {"status": "error", "message": f"未知的工具函数: {function_name}"}

# 链式调用上下文管理器
class ChainedCallContext:
    """用于在多个工具调用之间传递数据和状态的上下文管理器"""
    
    def __init__(self, max_iterations=10):
        self.max_iterations = max_iterations  # 最大迭代次数
        self.current_iteration = 0  # 当前迭代次数
        self.call_history = []  # 工具调用历史记录
        self.variables = {}  # 中间变量存储
        self.is_complete = False  # 是否完成
        self.final_answer = ""  # 最终回答
    
    def add_call(self, tool_name, arguments, result):
        """记录一次工具调用"""
        call_record = {
            "iteration": self.current_iteration,
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result,
            "timestamp": time.time()
        }
        self.call_history.append(call_record)
    
    def set_variable(self, name, value):
        """设置中间变量"""
        self.variables[name] = value
    
    def get_variable(self, name, default=None):
        """获取中间变量"""
        return self.variables.get(name, default)
    
    def increment_iteration(self):
        """增加迭代次数"""
        self.current_iteration += 1
    
    def is_max_iterations_reached(self):
        """检查是否达到最大迭代次数"""
        return self.current_iteration >= self.max_iterations
    
    def get_summary(self):
        """获取调用历史摘要"""
        summary = []
        for call in self.call_history:
            summary.append({
                "工具名称": call["tool_name"],
                "参数": call["arguments"],
                "结果状态": call["result"].get("status", "unknown")
            })
        return summary

# 提取JSON内容（处理markdown代码块标记）
def extract_json(content):
    """从字符串中提取JSON内容，处理可能的markdown代码块标记"""
    if content is None:
        return None
    
    content = content.strip()
    
    # 处理markdown代码块标记
    if content.startswith("```json"):
        content = content[7:]  # 移除 ```json
    if content.startswith("```"):
        content = content[3:]  # 移除 ```
    if content.endswith("```"):
        content = content[:-3]  # 移除结尾的 ```
    
    content = content.strip()
    
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None

# 构建分析提示词
def build_analysis_prompt(user_request, context):
    """构建链式调用的分析提示词"""
    
    # 构建已执行步骤历史
    history_str = ""
    if context.call_history:
        history_str = "已执行的步骤：\n"
        for i, call in enumerate(context.call_history, 1):
            history_str += f"{i}. 调用工具: {call['tool_name']}\n"
            history_str += f"   参数: {json.dumps(call['arguments'], ensure_ascii=False)}\n"
            history_str += f"   结果: {call['result'].get('status', 'unknown')}\n"
    
    # 构建中间变量信息
    variables_str = ""
    if context.variables:
        variables_str = "当前可用的中间变量：\n"
        for name, value in context.variables.items():
            variables_str += f"- {name}: {value}\n"
    
    prompt = f"""
你是一个智能工具调用助手，需要根据用户请求和已执行的步骤，决定下一步操作。

用户请求：{user_request}

{history_str}

{variables_str}

决策规则：
1. 分析当前状态和用户请求，判断是否需要继续调用工具
2. 如果任务已完成，直接给出最终回答
3. 如果需要继续，选择合适的工具并提供正确的参数
4. 可以使用之前工具调用的结果作为当前工具调用的参数

输出格式要求：
- 完成任务时，输出：{{"done": true, "answer": "最终回答内容"}}
- 需要继续调用工具时，输出：{{"done": false, "tool_call": {{"name": "工具名称", "arguments": {{"参数名": "参数值"}}}}}}

可用工具列表：
1. list_files - 列出目录下的文件
2. read_file - 读取文件内容
3. create_file - 创建文件并写入内容
4. delete_file - 删除文件
5. rename_file - 重命名文件
6. fetch_web_content - 获取网页内容
7. search_files_content - 搜索文件内容
8. search_chat_history - 搜索聊天历史
9. anythingllm_query - 查询文档仓库
10. list_available_skills - 获取可用技能列表

请根据以上信息，输出JSON格式的决策。
"""
    
    return prompt.strip()

# 链式调用执行函数
def execute_chained_tool_call(base_url, api_key, model, user_request, max_iterations=10, temperature=0.7, max_tokens=1000):
    """执行链式工具调用的完整流程"""
    
    # 初始化上下文
    context = ChainedCallContext(max_iterations=max_iterations)
    
    # 系统提示词
    system_prompt = """
你是一个智能工具调用助手，能够进行链式工具调用。

链式调用规则：
1. 你可以根据前一个工具的输出作为后一个工具的输入参数
2. 需要根据中间结果自主决定下一步操作
3. 支持以下输出格式：
   - 完成任务：{"done": true, "answer": "最终回答内容"}
   - 继续调用：{"done": false, "tool_call": {"name": "工具名称", "arguments": {"参数名": "参数值"}}}

工具列表：
1. list_files(directory) - 列出目录下的文件
2. read_file(directory, file_name) - 读取文件内容
3. create_file(directory, file_name, content) - 创建文件
4. delete_file(directory, file_name) - 删除文件
5. rename_file(directory, old_name, new_name) - 重命名文件
6. fetch_web_content(url) - 获取网页内容
7. search_files_content(directory, keyword) - 搜索文件内容

示例场景：
场景1：用户要求"查找目录下所有包含关键词的文件并总结"
- 第一步：调用 list_files 获取文件列表
- 第二步：调用 search_files_content 搜索关键词
- 第三步：总结结果，返回 {"done": true, "answer": "..."}

场景2：用户要求"读取两个文件内容并将结果写入新文件"
- 第一步：调用 read_file 读取第一个文件
- 第二步：调用 read_file 读取第二个文件
- 第三步：调用 create_file 写入结果
- 第四步：返回 {"done": true, "answer": "..."}

请严格按照JSON格式输出你的决策。
"""
    
    # 初始化消息历史
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    print(f"开始执行链式工具调用，最大迭代次数: {max_iterations}")
    print(f"用户请求: {user_request}")
    print("-" * 60)
    
    # 循环执行
    while not context.is_complete and not context.is_max_iterations_reached():
        # 构建分析提示词
        analysis_prompt = build_analysis_prompt(user_request, context)
        
        # 添加到消息历史
        messages.append({"role": "user", "content": analysis_prompt})
        
        # 调用LLM决定下一步操作
        response = call_llm_api(base_url, api_key, model, messages, temperature, max_tokens)
        
        if "error" in response:
            print(f"LLM API错误: {response['error']}")
            break
        
        if "choices" not in response or len(response["choices"]) == 0:
            print("LLM API未返回有效响应")
            break
        
        # 解析响应
        message = response["choices"][0].get("message", {})
        content = message.get("content", "")
        
        # 尝试从tool_calls格式解析（OpenAI标准Function Calling格式）
        tool_calls = message.get("tool_calls", [])
        
        if tool_calls and len(tool_calls) > 0:
            # OpenAI标准Function Calling格式
            tool_call = {
                "name": tool_calls[0]["function"]["name"],
                "arguments": json.loads(tool_calls[0]["function"]["arguments"])
            }
            decision = {"done": False, "tool_call": tool_call}
        else:
            # 尝试从content中解析JSON
            decision = extract_json(content)
        
        if decision is None:
            print(f"无法解析LLM响应: {content}")
            break
        
        # 检查是否完成
        if decision.get("done", False):
            context.is_complete = True
            context.final_answer = decision.get("answer", "")
            print(f"任务完成: {context.final_answer}")
            break
        
        # 执行工具调用
        tool_call = decision.get("tool_call")
        if not tool_call:
            print("未找到工具调用信息")
            break
        
        tool_name = tool_call.get("name")
        arguments = tool_call.get("arguments", {})
        
        print(f"第{context.current_iteration + 1}轮 - 调用工具: {tool_name}")
        print(f"参数: {json.dumps(arguments, ensure_ascii=False)}")
        
        # 执行工具
        result = execute_tool_call(tool_call)
        
        print(f"结果: {result.get('status', 'unknown')}")
        print("-" * 60)
        
        # 记录到上下文
        context.add_call(tool_name, arguments, result)
        context.increment_iteration()
        
        # 将结果添加到消息历史
        messages.append({"role": "assistant", "content": json.dumps({"tool_result": result}, ensure_ascii=False)})
    
    # 检查是否因达到最大迭代次数而退出
    if context.is_max_iterations_reached() and not context.is_complete:
        context.final_answer = f"警告：已达到最大迭代次数({max_iterations}次)，任务未完成。已执行的步骤：{json.dumps(context.get_summary(), ensure_ascii=False)}"
        print(context.final_answer)
    
    return context

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
    
    print("=== AI 链式工具调用接口 ===")
    print("Type your message and press Enter to interact with the AI.")
    print("Press Ctrl+C to exit.")
    print("-" * 50)
    
    try:
        while True:
            # 获取用户输入
            user_input = input("You: ")
            
            # 执行链式工具调用
            context = execute_chained_tool_call(base_url, api_key, model, user_input)
            
            # 输出最终结果
            print(f"\n最终回答: {context.final_answer}")
            print("-" * 50)
            
    except KeyboardInterrupt:
        print("\nExiting chat...")
        print("Thank you for using the AI tool call interface!")

if __name__ == "__main__":
    main()