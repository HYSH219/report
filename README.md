# AI智能体开发教学项目

## 项目简介

这是一个基于Python的AI智能体开发教学项目，旨在帮助学习者了解如何使用Python与OpenAI兼容的LLM API进行交互，以及如何构建简单的AI应用。

## 目录结构

```
├── practice01/          # 第一个教学代码目录
│   ├── llm_token_speed.py  # LLM访问和Token速度统计
│   └── chat_with_history.py  # 聊天功能与历史记录管理
├── practice02/          # 第二个教学代码目录
│   └── tool_call_client.py  # 工具调用功能
├── practice03/          # 第三个教学代码目录
│   └── tool_call_client.py  # 工具调用功能（新增网络访问）
├── venv/                # 虚拟环境目录
├── .gitignore           # Git忽略文件
├── env.example          # 环境变量示例文件
└── README.md            # 项目说明文件
```

## 环境配置

1. **检查Python环境**
   - 确保安装了Python 3.7或更高版本
   - 运行 `python --version` 确认版本

2. **初始化虚拟环境**
   ```bash
   python -m venv venv
   ```

3. **配置环境变量**
   - 复制 `env.example` 文件为 `.env`
   - 编辑 `.env` 文件，填写正确的LLM API配置信息

## 代码功能说明

### practice01/llm_token_speed.py

**功能用途：**
- 读取项目根目录的 `.env` 文件，获取LLM API配置
- 使用Python标准HTTP库访问用户定义的LLM API
- 发送测试请求并获取响应
- 统计Token使用情况和响应速度

**教学目标：**
- 学习如何使用Python标准库处理HTTP请求
- 了解LLM API的基本调用方式
- 掌握环境变量的读取和管理
- 学习如何解析JSON响应数据
- 了解Token使用和速度统计的方法

**使用方法：**
```bash
# 激活虚拟环境
venv\Scripts\activate

# 运行代码
python practice01\llm_token_speed.py
```

### practice01/chat_with_history.py

**功能用途：**
- 读取项目根目录的 `.env` 文件，获取LLM API配置
- 提供终端界面，支持用户输入聊天内容
- 使用流式输出方式显示AI响应，提升用户体验
- 自动保存聊天历史记录，并在每次请求时添加到上下文
- 支持用户通过Ctrl+C退出聊天

**教学目标：**
- 学习如何实现流式API调用
- 了解如何管理聊天历史记录
- 掌握终端界面的交互设计
- 学习如何处理键盘中断信号
- 了解如何优化API调用的上下文管理

**使用方法：**
```bash
# 激活虚拟环境
venv\Scripts\activate

# 运行代码
python practice01\chat_with_history.py

# 然后在终端中输入消息，按Enter发送
# 按Ctrl+C退出聊天
```

### practice02/tool_call_client.py

**功能用途：**
- 读取项目根目录的 `.env` 文件，获取LLM API配置
- 提供终端界面，支持用户与AI交互
- 实现工具调用功能，包括：
  - 列出目录下的文件及信息
  - 修改文件名字
  - 删除文件
  - 新建文件并写入内容
  - 读取文件内容
- AI可以根据用户请求自动调用相应的工具

**教学目标：**
- 学习如何实现工具调用功能
- 了解如何设计工具函数的参数和返回值
- 掌握如何解析和执行工具调用请求
- 学习如何将工具执行结果反馈给AI
- 了解如何构建更复杂的AI智能体应用

**使用方法：**
```bash
# 激活虚拟环境
venv\Scripts\activate

# 运行代码
python practice02\tool_call_client.py

# 然后在终端中输入消息，按Enter发送
# 例如："列出D:\ai目录下的文件"
# 按Ctrl+C退出聊天
```

### practice03/tool_call_client.py

**功能用途：**
- 基于 practice02 的代码，新增网络访问功能
- 实现 `fetch_web_content` 工具函数，支持访问网页并返回内容
- 其他功能与 practice02 相同

**教学目标：**
- 学习如何实现网络访问功能
- 了解如何处理HTTP请求和响应
- 掌握如何将网络访问功能集成到工具调用系统中
- 学习如何处理网络请求中的错误情况

**使用方法：**
```bash
# 激活虚拟环境
venv\Scripts\activate

# 运行代码
python practice03\tool_call_client.py

# 然后在终端中输入消息，按Enter发送
# 例如："访问百度网站并返回内容"
# 按Ctrl+C退出聊天
```

## 后续教学内容

本项目将持续添加更多教学代码，包括：
- 更复杂的工具集成
- 多智能体协作
- 外部服务集成
- 更高级的AI应用场景

## 注意事项

- 请确保在 `.env` 文件中填写正确的API密钥和配置信息
- 本项目使用Python标准库，无需额外安装依赖
- 所有代码均为教学目的，实际生产环境中可能需要更多的错误处理和安全措施
