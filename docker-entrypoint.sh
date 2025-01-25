#!/bin/bash
set -e

# 打印环境信息
echo "Python version:"
python --version

# 创建必要的目录
mkdir -p data logs

# 等待健康检查通过
echo "Waiting for application to be ready..."
until curl -f http://localhost:8000/health || [ $? -eq 22 ]; do
    sleep 1
done

# 设置webhook
echo "Setting up Telegram webhook..."
python set_webhook.py

# 启动应用
echo "Starting application..."
exec "$@" 