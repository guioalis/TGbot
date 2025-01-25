from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv
import logging
from models import storage
import asyncio

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 配置
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(',')))

# 创建 FastAPI 应用
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 创建 Telegram 应用
telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Telegram 命令处理函数
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('👋 喵哥AI群管机器人已启动！使用 /help 查看命令列表。')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🤖 可用命令列表：
/start - 启动机器人
/help - 显示帮助信息
/enable_ai - 启用AI回复
/disable_ai - 禁用AI回复
"""
    await update.message.reply_text(help_text)

async def enable_ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    group_data = storage.get_group(chat_id)
    group_data['ai_enabled'] = True
    storage.save_group(chat_id, group_data)
    await update.message.reply_text('✅ AI回复已启用！')

async def disable_ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    group_data = storage.get_group(chat_id)
    group_data['ai_enabled'] = False
    storage.save_group(chat_id, group_data)
    await update.message.reply_text('❌ AI回复已禁用！')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    chat_id = update.effective_chat.id
    group_data = storage.get_group(chat_id)
    
    if not group_data.get('ai_enabled', False):
        return
    
    await update.message.reply_text('收到消息！')

# 初始化 Telegram 处理器
telegram_app.add_handler(CommandHandler("start", start_command))
telegram_app.add_handler(CommandHandler("help", help_command))
telegram_app.add_handler(CommandHandler("enable_ai", enable_ai_command))
telegram_app.add_handler(CommandHandler("disable_ai", disable_ai_command))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# FastAPI 路由
@app.get("/")
async def index(request: Request):
    """渲染管理界面"""
    groups = storage.get_all_groups()
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "groups": groups}
    )

@app.get("/api/groups")
async def get_groups():
    """获取群组列表"""
    try:
        groups = storage.get_all_groups()
        return JSONResponse(groups)
    except Exception as e:
        logger.error(f"Error in get_groups: {str(e)}")
        return JSONResponse(
            {"error": "Failed to fetch groups"}, 
            status_code=500
        )

@app.post("/api/groups/{chat_id}")
async def update_group(chat_id: int, request: Request):
    """更新群组设置"""
    try:
        data = await request.json()
        storage.save_group(chat_id, data)
        return JSONResponse({"status": "success"})
    except Exception as e:
        logger.error(f"Error in update_group: {str(e)}")
        return JSONResponse(
            {"error": "Failed to update group"}, 
            status_code=500
        )

@app.get("/api/banned_users")
async def get_banned_users():
    """获取被禁言用户列表"""
    try:
        storage.remove_expired_bans()
        banned = storage.get_banned_users()
        return JSONResponse(banned)
    except Exception as e:
        logger.error(f"Error in get_banned_users: {str(e)}")
        return JSONResponse(
            {"error": "Failed to fetch banned users"}, 
            status_code=500
        )

@app.post("/api/webhook")
async def telegram_webhook(request: Request):
    """处理 Telegram webhook"""
    try:
        update_data = await request.json()
        update = Update.de_json(update_data, telegram_app.bot)
        await telegram_app.process_update(update)
        return Response('OK', status_code=200)
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return Response(str(e), status_code=500)

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return JSONResponse({
        "status": "healthy",
        "environment": "vercel" if os.getenv('VERCEL') else 'local',
        "timestamp": storage.get_timestamp()
    }) 