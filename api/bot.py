from flask import Response, request
from telegram import Update, TelegramError
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import logging
import asyncio
from models import storage
from utils.config import config
from utils.helpers import handle_errors, validate_admin
from utils.logger import logger
from typing import Optional, Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

class BotHandler:
    def __init__(self):
        self.app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        self.setup_handlers()
    
    @handle_errors
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            await update.message.reply_text('👋 喵哥AI群管机器人已启动！使用 /help 查看命令列表。')
        except TelegramError as e:
            logger.error(f"Telegram error in start_command: {e}")
            raise
    
    @handle_errors
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            help_text = """
            🤖 可用命令列表：
            /start - 启动机器人
            /help - 显示帮助信息
            /enable_ai - 启用AI回复
            /disable_ai - 禁用AI回复
            """
            await update.message.reply_text(help_text)
        except TelegramError as e:
            logger.error(f"Telegram error in help_command: {e}")
            raise
    
    @handle_errors
    async def enable_ai_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            chat_id = update.effective_chat.id
            group_data = storage.get_group(chat_id)
            group_data['ai_enabled'] = True
            storage.save_group(chat_id, group_data)
            await update.message.reply_text('✅ AI回复已启用！')
        except Exception as e:
            logger.error(f"Error in enable_ai_command: {e}")
            await update.message.reply_text('❌ 启用AI回复失败，请稍后重试')
            raise
    
    @handle_errors
    async def disable_ai_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        group_data = storage.get_group(chat_id)
        group_data['ai_enabled'] = False
        storage.save_group(chat_id, group_data)
        await update.message.reply_text('AI回复已禁用！')
    
    @handle_errors
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            if not update.message or not update.message.text:
                return
            
            chat_id = update.effective_chat.id
            group_data = storage.get_group(chat_id)
            
            if not group_data.get('ai_enabled', False):
                return
            
            # 处理消息
            await self.process_message(update, context)
            
        except Exception as e:
            logger.error(f"Error in handle_message: {e}")
            # 不要在普通消息处理中显示错误
    
    def setup_handlers(self):
        """设置所有命令处理器"""
        try:
            self.app.add_handler(CommandHandler("start", self.start_command))
            self.app.add_handler(CommandHandler("help", self.help_command))
            self.app.add_handler(CommandHandler("enable_ai", self.enable_ai_command))
            self.app.add_handler(CommandHandler("disable_ai", self.disable_ai_command))
            self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        except Exception as e:
            logger.error(f"Error setting up handlers: {e}")
            raise
    
    async def process_update(self, update_data: Dict[str, Any]) -> bool:
        """处理更新"""
        try:
            update = Update.de_json(update_data, self.app.bot)
            await self.app.process_update(update)
            return True
        except Exception as e:
            logger.error(f"Error processing update: {e}")
            return False

# 创建全局机器人处理器实例
bot_handler = BotHandler()

def webhook_handler(request):
    """Webhook 处理函数"""
    try:
        update_data = request.get_json()
        
        # 使用事件循环处理更新
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(bot_handler.process_update(update_data))
        loop.close()
        
        if success:
            return Response('OK', status=200)
        else:
            return Response('Failed to process update', status=500)
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return Response(str(e), status=500) 