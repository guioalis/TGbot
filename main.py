from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from api import router as api_router
from utils.config import config
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 创建应用
app = FastAPI(
    title="喵哥AI群管机器人",
    description="Telegram群管理机器人，集成AI对话功能",
    version="1.0.0"
)

# 挂载静态文件和模板
app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")
templates = Jinja2Templates(directory=config.TEMPLATE_DIR)

# 添加API路由
app.include_router(api_router, prefix="/api")

@app.get("/")
async def index(request: Request):
    """渲染管理界面"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """健康检查"""
    from models import storage
    return {
        "status": "healthy",
        "environment": "vercel" if config.IS_VERCEL else "local",
        "timestamp": storage.get_timestamp()
    } 