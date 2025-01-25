from flask import Flask, render_template, jsonify, request, Response
from telegram import Update, ChatPermissions, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError
import os
from dotenv import load_dotenv
import requests
import json
from datetime import datetime, timedelta
import asyncio
import logging
from functools import wraps
from api.bot import webhook_handler
from models import storage

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 配置
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_API_URL = os.getenv('GEMINI_API_URL')
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(',')))  # 管理员ID列表

app = Flask(__name__)

# 装饰器：检查是否是管理员
def admin_required(f):
    @wraps(f)
    async def decorated_function(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("此命令仅管理员可用！")
            return
        return await f(update, context, *args, **kwargs)
    return decorated_function

# 装饰器：错误处理
def handle_telegram_error(f):
    @wraps(f)
    async def decorated_function(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            return await f(update, context, *args, **kwargs)
        except TelegramError as e:
            logger.error(f"Telegram error in {f.__name__}: {str(e)}")
            await update.message.reply_text(f"操作失败: {str(e)}")
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}")
            await update.message.reply_text("发生错误，请稍后重试")
    return decorated_function

# Telegram机器人功能
async def setup_commands(application: Application):
    """设置机器人命令列表"""
    commands = [
        BotCommand("start", "启动机器人"),
        BotCommand("help", "显示帮助信息"),
        BotCommand("settings", "查看当前群组设置"),
        BotCommand("enable_ai", "启用AI回复"),
        BotCommand("disable_ai", "禁用AI回复"),
        BotCommand("setup", "初始化群组设置"),
        BotCommand("setwelcome", "设置欢迎消息"),
        BotCommand("ban", "禁言用户"),
        BotCommand("delete", "删除消息"),
        BotCommand("set_ai_config", "设置AI参数")
    ]
    await application.bot.set_my_commands(commands)

@handle_telegram_error
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理/start命令"""
    welcome_text = (
        f'👋 你好！我是喵哥AI群管机器人\n'
        f'🤖 我可以帮助管理群组并提供AI对话功能\n'
        f'📝 使用 /help 查看完整命令列表'
    )
    await update.message.reply_text(welcome_text)

@handle_telegram_error
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理/help命令"""
    help_text = """
🤖 喵哥AI群管机器人命令列表：

基础命令：
/start - 启动机器人
/help - 显示此帮助信息
/settings - 查看当前群组设置

AI功能：
/enable_ai - 启用AI回复
/disable_ai - 禁用AI回复
/set_ai_config - 设置AI参数

群管理：
/setup - 初始化群组设置
/setwelcome - 设置欢迎消息
/ban - 禁言用户
/delete - 删除消息

🔧 管理员可以通过网页后台进行更多设置
"""
    await update.message.reply_text(help_text)

# ... (从bot.py复制其他所有机器人处理函数) ...

# Flask路由
@app.route('/')
def index():
    """渲染管理界面"""
    try:
        groups = storage.get_all_groups()
        return render_template('index.html', groups=groups)
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/groups', methods=['GET'])
def get_groups():
    """获取群组列表"""
    try:
        groups = storage.get_all_groups()
        return jsonify(groups)
    except Exception as e:
        logger.error(f"Error in get_groups: {str(e)}")
        return jsonify({"error": "Failed to fetch groups"}), 500

@app.route('/api/groups/<int:chat_id>', methods=['POST'])
def update_group(chat_id):
    """更新群组设置"""
    try:
        data = request.json
        storage.save_group(chat_id, data)
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"Error in update_group: {str(e)}")
        return jsonify({"error": "Failed to update group"}), 500

@app.route('/api/banned_users', methods=['GET'])
def get_banned_users():
    """获取被禁言用户列表"""
    try:
        storage.remove_expired_bans()  # 清理过期的禁言
        banned = storage.get_banned_users()
        return jsonify(banned)
    except Exception as e:
        logger.error(f"Error in get_banned_users: {str(e)}")
        return jsonify({"error": "Failed to fetch banned users"}), 500

@app.route('/health')
def health_check():
    """健康检查端点"""
    try:
        # 检查存储是否可用
        storage.get_all_groups()
        return jsonify({
            "status": "healthy",
            "storage": "connected",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": "vercel" if os.getenv('VERCEL') else 'local'
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

# Webhook 路由
@app.route('/api/webhook', methods=['POST'])
def telegram_webhook():
    """处理 Telegram webhook"""
    return webhook_handler(request)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 