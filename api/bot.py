from flask import Flask, Response, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import json
from models import storage
import logging
import asyncio
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# 机器人命令处理函数
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('喵哥AI群管机器人已启动！使用 /help 查看命令列表。')

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
    await update.message.reply_text('AI回复已启用！')

async def disable_ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    group_data = storage.get_group(chat_id)
    group_data['ai_enabled'] = False
    storage.save_group(chat_id, group_data)
    await update.message.reply_text('AI回复已禁用！')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    chat_id = update.effective_chat.id
    group_data = storage.get_group(chat_id)
    
    if not group_data.get('ai_enabled', False):
        return
    
    # 处理消息...
    await update.message.reply_text('收到消息！')

def create_application():
    """创建机器人应用实例"""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # 添加命令处理器
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("enable_ai", enable_ai_command))
    application.add_handler(CommandHandler("disable_ai", disable_ai_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    return application

async def handle_update(update_data: dict):
    """处理 Telegram 更新"""
    try:
        application = create_application()
        await application.initialize()
        update = Update.de_json(update_data, application.bot)
        await application.process_update(update)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error handling update: {str(e)}")
        return {"status": "error", "message": str(e)}

def webhook_handler(request):
    """Webhook 处理函数"""
    try:
        update_data = request.get_json()
        asyncio.run(handle_update(update_data))
        return Response('OK', status=200)
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return Response(str(e), status=500) 