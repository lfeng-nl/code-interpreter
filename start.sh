#!/bin/bash

# Python 代码解释器服务启动脚本

echo "🐍 启动 Python 代码解释器服务..."

# 检查 Python 版本
python_version=$(python3 --version 2>&1)
echo "Python 版本: $python_version"

# 检查依赖
echo "检查依赖..."
if ! pip show flask > /dev/null 2>&1; then
    echo "安装依赖..."
    pip install -r requirements.txt
fi

# 检查端口是否被占用
if lsof -Pi :12001 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  端口 12001 已被占用，尝试终止现有进程..."
    pkill -f "python.*app.py"
    sleep 2
fi

# 启动服务
echo "启动服务在端口 12001..."
python3 app.py

echo "服务已启动！"
echo "Web 界面: http://localhost:12001"
echo "API 文档: 请查看 README.md"