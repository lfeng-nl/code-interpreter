# Python 代码解释器服务

一个安全的 Python 代码执行服务，允许用户通过 Web 界面或 API 执行 Python 代码片段。

## 功能特性

- 🔒 **安全执行**：限制危险模块导入，防止恶意代码执行
- ⏱️ **超时控制**：防止无限循环和长时间运行的代码
- 🌐 **Web 界面**：简洁的 HTML 界面，支持代码输入和结果显示
- 📡 **REST API**：提供 HTTP API 接口，支持程序化调用
- 🎯 **示例代码**：内置多个示例，方便快速测试
- 📊 **执行统计**：显示代码执行时间和状态

## 安全限制

为了确保服务安全，以下模块和操作被限制：

- 系统操作：`os`, `subprocess`, `sys`
- 文件操作：`open`, `file`, `input`
- 网络操作：`socket`, `urllib`, `requests`
- 其他危险模块：`eval`, `exec`, `compile`

允许的模块包括：`math`, `random`, `datetime`, `json`, `re`, `collections` 等安全模块。

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
python app.py
```

服务将在 `http://localhost:12001` 启动。

### 使用 Web 界面

1. 打开浏览器访问 `http://localhost:12001`
2. 在文本框中输入 Python 代码
3. 点击"执行代码"按钮
4. 查看执行结果

### 使用 API

#### 执行代码

```bash
curl -X POST http://localhost:12001/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"Hello, World!\")"}'
```

响应格式：
```json
{
  "success": true,
  "output": "Hello, World!\n",
  "error": null,
  "execution_time": 0.001
}
```

#### 健康检查

```bash
curl http://localhost:12001/health
```

## 项目结构

```
code-interpreter/
├── app.py              # Flask Web 服务
├── code_executor.py    # 代码执行引擎
├── requirements.txt    # 项目依赖
├── README.md          # 项目文档
└── server.log         # 服务日志
```

## 技术栈

- **后端框架**：Flask 2.3.3
- **CORS 支持**：Flask-CORS 4.0.0
- **Web 服务器**：Werkzeug 2.3.7
- **Python 版本**：3.8+

## 示例代码

### 1. 基础打印
```python
print('Hello, World!')
```

### 2. 数学计算
```python
import math
result = math.sqrt(16) + math.pi
print(f'计算结果: {result:.2f}')
```

### 3. 列表操作
```python
numbers = [1, 2, 3, 4, 5]
squares = [x**2 for x in numbers]
print(f'原数组: {numbers}')
print(f'平方数组: {squares}')
```

### 4. 字符串处理
```python
text = "Python Code Interpreter"
print(f'原文: {text}')
print(f'大写: {text.upper()}')
print(f'单词数: {len(text.split())}')
```

### 5. 时间处理
```python
import datetime
now = datetime.datetime.now()
print(f'当前时间: {now.strftime("%Y-%m-%d %H:%M:%S")}')
```

## 部署说明

### 开发环境
```bash
python app.py
```

### 生产环境
建议使用 gunicorn 或其他 WSGI 服务器：
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:12001 app:app
```

## 注意事项

1. **安全性**：本服务仅适用于受信任的环境，不建议直接暴露到公网
2. **资源限制**：代码执行有 5 秒超时限制，防止资源滥用
3. **错误处理**：所有执行错误都会被捕获并返回给用户
4. **日志记录**：服务运行日志保存在 `server.log` 文件中

## 许可证

MIT License