from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from code_executor import CodeExecutor
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 创建代码执行器实例
executor = CodeExecutor(timeout=10, max_output_size=10000)

# HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python 代码解释器</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .input-section {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 10px;
            font-weight: bold;
            color: #555;
        }
        textarea {
            width: 100%;
            height: 200px;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            resize: vertical;
            box-sizing: border-box;
        }
        textarea:focus {
            border-color: #4CAF50;
            outline: none;
        }
        .button-section {
            text-align: center;
            margin: 20px 0;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #45a049;
        }
        button:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
        }
        .output-section {
            margin-top: 20px;
        }
        .output {
            background-color: #f8f8f8;
            border: 2px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            min-height: 100px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .success {
            border-color: #4CAF50;
            background-color: #f0fff0;
        }
        .error {
            border-color: #f44336;
            background-color: #fff0f0;
            color: #d32f2f;
        }
        .loading {
            text-align: center;
            color: #666;
            font-style: italic;
        }
        .examples {
            margin-top: 30px;
            padding: 20px;
            background-color: #f9f9f9;
            border-radius: 5px;
        }
        .example {
            margin-bottom: 15px;
            padding: 10px;
            background-color: white;
            border-radius: 3px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .example:hover {
            background-color: #e8f5e8;
        }
        .example-title {
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        .example-code {
            font-family: 'Courier New', monospace;
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐍 Python 代码解释器</h1>
        
        <div class="input-section">
            <label for="code">输入 Python 代码：</label>
            <textarea id="code" placeholder="在这里输入你的 Python 代码...&#10;例如：&#10;print('Hello, World!')&#10;&#10;import math&#10;print(f'π = {math.pi}')"></textarea>
        </div>
        
        <div class="button-section">
            <button onclick="executeCode()" id="executeBtn">执行代码</button>
        </div>
        
        <div class="output-section">
            <label>执行结果：</label>
            <div id="output" class="output">等待执行代码...</div>
        </div>
        
        <div class="examples">
            <h3>示例代码（点击使用）：</h3>
            
            <div class="example" onclick="useExample(this)">
                <div class="example-title">1. 基础打印</div>
                <div class="example-code">print('Hello, World!')</div>
            </div>
            
            <div class="example" onclick="useExample(this)">
                <div class="example-title">2. 数学计算</div>
                <div class="example-code">import math&#10;result = math.sqrt(16) + math.pi&#10;print(f'计算结果: {result:.2f}')</div>
            </div>
            
            <div class="example" onclick="useExample(this)">
                <div class="example-title">3. 列表操作</div>
                <div class="example-code">numbers = [1, 2, 3, 4, 5]&#10;squares = [x**2 for x in numbers]&#10;print(f'原数组: {numbers}')&#10;print(f'平方数组: {squares}')</div>
            </div>
            
            <div class="example" onclick="useExample(this)">
                <div class="example-title">4. 字符串处理</div>
                <div class="example-code">text = "Python Code Interpreter"&#10;print(f'原文: {text}')&#10;print(f'大写: {text.upper()}')&#10;print(f'单词数: {len(text.split())}')</div>
            </div>
            
            <div class="example" onclick="useExample(this)">
                <div class="example-title">5. 时间处理</div>
                <div class="example-code">import datetime&#10;now = datetime.datetime.now()&#10;print(f'当前时间: {now.strftime("%Y-%m-%d %H:%M:%S")}')</div>
            </div>
        </div>
    </div>

    <script>
        function executeCode() {
            const code = document.getElementById('code').value;
            const output = document.getElementById('output');
            const button = document.getElementById('executeBtn');
            
            if (!code.trim()) {
                output.textContent = '请输入代码';
                output.className = 'output error';
                return;
            }
            
            // 显示加载状态
            output.textContent = '正在执行代码...';
            output.className = 'output loading';
            button.disabled = true;
            button.textContent = '执行中...';
            
            // 发送请求
            fetch('/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ code: code })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    output.textContent = data.output || '代码执行成功，无输出';
                    output.className = 'output success';
                } else {
                    output.textContent = data.error || '执行失败';
                    output.className = 'output error';
                }
            })
            .catch(error => {
                output.textContent = '网络错误: ' + error.message;
                output.className = 'output error';
            })
            .finally(() => {
                button.disabled = false;
                button.textContent = '执行代码';
            });
        }
        
        function useExample(element) {
            const codeElement = element.querySelector('.example-code');
            const code = codeElement.textContent.replace(/&#10;/g, '\\n');
            document.getElementById('code').value = code;
        }
        
        // 支持 Ctrl+Enter 快捷键执行
        document.getElementById('code').addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                executeCode();
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """主页面"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/execute', methods=['POST'])
def execute_code():
    """执行代码的API端点"""
    try:
        data = request.get_json()
        
        if not data or 'code' not in data:
            return jsonify({
                'success': False,
                'error': '请求格式错误：缺少code字段'
            }), 400
        
        code = data['code']
        
        if not isinstance(code, str):
            return jsonify({
                'success': False,
                'error': '代码必须是字符串类型'
            }), 400
        
        # 记录执行请求
        logger.info(f"执行代码请求: {len(code)} 字符")
        
        # 执行代码
        result = executor.execute(code)
        
        # 记录执行结果
        if result['success']:
            logger.info(f"代码执行成功，耗时: {result['execution_time']:.3f}秒")
        else:
            logger.warning(f"代码执行失败: {result['error']}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"服务器错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500

@app.route('/health')
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'service': 'Python Code Interpreter',
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        'success': False,
        'error': '端点不存在'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        'success': False,
        'error': '服务器内部错误'
    }), 500

if __name__ == '__main__':
    print("🚀 启动 Python 代码解释器服务...")
    print("📝 访问 http://localhost:12001 使用Web界面")
    print("🔗 API端点: POST /execute")
    print("❤️  健康检查: GET /health")
    
    app.run(
        host='0.0.0.0',
        port=12001,
        debug=True,
        threaded=True
    )