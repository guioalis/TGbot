#!/bin/bash

# 设置颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 确保脚本在错误时停止
set -e

echo -e "${GREEN}开始部署喵哥AI群管机器人...${NC}"

# 检查必要文件
if [ ! -f .env ]; then
    echo -e "${YELLOW}未找到.env文件，正在创建...${NC}"
    cp .env.example .env
    echo "请编辑 .env 文件，填入必要的配置信息"
    exit 1
fi

# 创建必要的目录
echo -e "${GREEN}创建必要的目录...${NC}"
mkdir -p data logs

# 设置文件权限
echo -e "${GREEN}设置文件权限...${NC}"
chmod +x scripts/docker-deploy.sh
chmod +x docker-entrypoint.sh

# 构建并启动服务
echo -e "${GREEN}构建并启动服务...${NC}"
docker-compose up --build -d

# 等待服务启动
echo -e "${GREEN}等待服务启动...${NC}"
sleep 5

# 检查服务状态
echo -e "${GREEN}检查服务状态...${NC}"
docker-compose ps

# 设置webhook
echo -e "${GREEN}设置Telegram Webhook...${NC}"
docker-compose exec bot python set_webhook.py

echo -e "${GREEN}部署完成！${NC}"
echo -e "${GREEN}可以使用以下命令查看日志：${NC}"
echo -e "${YELLOW}docker-compose logs -f${NC}" 