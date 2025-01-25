#!/bin/bash

# 确保脚本在错误时停止
set -e

# 显示执行的命令
set -x

# 构建镜像
docker-compose build

# 停止并删除旧容器
docker-compose down

# 启动新容器
docker-compose up -d

# 显示容器状态
docker-compose ps

# 显示日志
docker-compose logs -f 