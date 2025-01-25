import os
import sys
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from api import router as api_router
from utils.config import config
from utils.logger import logger

# 配置日志
logger.info("Starting application...")

# 创建应用
app = FastAPI(
    title="喵哥AI群管机器人",
    description="Telegram群管理机器人，集成AI对话功能",
    version="1.0.0"
)

# 在生产环境中禁用静态文件服务
if not config.IS_VERCEL:
    app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")
    templates = Jinja2Templates(directory=config.TEMPLATE_DIR)

# 添加API路由
app.include_router(api_router, prefix="/api")

@app.get("/")
async def index():
    """健康检查"""
    return {"status": "healthy"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "environment": "vercel" if config.IS_VERCEL else "local",
        "timestamp": config.get_timestamp()
    } 