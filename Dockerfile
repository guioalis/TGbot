# 使用Python 3.9作为基础镜像
FROM python:3.9-slim

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
COPY . .

# 设置权限
RUN chmod +x docker-entrypoint.sh

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8000

# 设置入口点
ENTRYPOINT ["./docker-entrypoint.sh"]

# 启动命令
CMD ["gunicorn", "web_app:app", "--worker-class", "eventlet", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"] 