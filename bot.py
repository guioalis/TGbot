import os
from telegram import Update, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import requests
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Group, BannedUser, engine
import asyncio

# 加载环境变量
load_dotenv()

# 配置
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_API_URL = os.getenv('GEMINI_API_URL')

# 初始化数据库会话
db = Session(engine)

# 存储群组配置
group_settings = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('喵哥AI群管机器人已启动！使用 /help 查看命令列表。')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
可用命令列表：
/start - 启动机器人
/help - 显示帮助信息
/settings - 查看当前群组设置
/enable_ai - 启用AI回复
/disable_ai - 禁用AI回复
"""
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    chat_id = update.message.chat_id
    
    # 检查是否启用了AI回复
    if chat_id not in group_settings or not group_settings[chat_id].get('ai_enabled', False):
        return
    
    # 调用Gemini API
    headers = {
        'Authorization': f'Bearer {GEMINI_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": update.message.text
            }
        ],
        "model": "gemini-2.0-flash-exp"
    }
    
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=data)
        response_data = response.json()
        if 'choices' in response_data and len(response_data['choices']) > 0:
            ai_response = response_data['choices'][0]['message']['content']
            await update.message.reply_text(ai_response)
    except Exception as e:
        print(f"Error calling Gemini API: {e}")

async def enable_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    group_settings[chat_id] = {'ai_enabled': True}
    await update.message.reply_text('AI回复已启用！')

async def disable_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    group_settings[chat_id] = {'ai_enabled': False}
    await update.message.reply_text('AI回复已禁用！')

async def setup_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """初始化或更新群组设置"""
    chat = update.effective_chat
    if chat.type in ['group', 'supergroup']:
        group = db.query(Group).filter_by(chat_id=chat.id).first()
        if not group:
            group = Group(
                chat_id=chat.id,
                title=chat.title,
                ai_config={
                    'temperature': 0.7,
                    'max_tokens': 1000,
                    'system_prompt': 'You are a helpful assistant.'
                }
            )
            db.add(group)
        else:
            group.title = chat.title
        db.commit()
        await update.message.reply_text('群组设置已更新!')

async def set_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """设置欢迎消息"""
    if not context.args:
        await update.message.reply_text('请提供欢迎消息内容!')
        return
    
    group = db.query(Group).filter_by(chat_id=update.effective_chat.id).first()
    if group:
        group.welcome_message = ' '.join(context.args)
        db.commit()
        await update.message.reply_text('欢迎消息已设置!')

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """禁言用户"""
    if not context.args or not update.message.reply_to_message:
        await update.message.reply_text('请回复要禁言的用户消息并提供禁言时长(分钟)!')
        return
    
    try:
        duration = int(context.args[0])
        user = update.message.reply_to_message.from_user
        reason = ' '.join(context.args[1:]) if len(context.args) > 1 else '未指定原因'
        
        until_date = datetime.now() + timedelta(minutes=duration)
        
        # 添加到数据库
        banned = BannedUser(
            chat_id=update.effective_chat.id,
            user_id=user.id,
            banned_until=until_date,
            reason=reason
        )
        db.add(banned)
        db.commit()
        
        # 在Telegram中实际禁言
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            user.id,
            until_date=until_date,
            permissions=ChatPermissions(can_send_messages=False)
        )
        
        await update.message.reply_text(f'已禁言用户 {user.name} {duration}分钟\n原因: {reason}')
    except Exception as e:
        await update.message.reply_text(f'禁言失败: {str(e)}')

async def delete_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """删除消息"""
    if not update.message.reply_to_message:
        await update.message.reply_text('请回复要删除的消息!')
        return
    
    try:
        await context.bot.delete_message(
            update.effective_chat.id,
            update.message.reply_to_message.message_id
        )
        await update.message.delete()
    except Exception as e:
        await update.message.reply_text(f'删除失败: {str(e)}')

async def set_ai_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """设置AI配置"""
    if not context.args or len(context.args) < 2:
        await update.message.reply_text('请提供配置项和值! 例如: /set_ai_config temperature 0.8')
        return
    
    group = db.query(Group).filter_by(chat_id=update.effective_chat.id).first()
    if group:
        key = context.args[0]
        value = context.args[1]
        
        if key in ['temperature', 'max_tokens']:
            try:
                value = float(value)
            except:
                await update.message.reply_text('请提供有效的数值!')
                return
        
        if not group.ai_config:
            group.ai_config = {}
        
        group.ai_config[key] = value
        db.commit()
        await update.message.reply_text(f'AI配置已更新: {key} = {value}')

async def auto_delete_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理自动删除消息"""
    group = db.query(Group).filter_by(chat_id=update.effective_chat.id).first()
    if group and group.auto_delete_time > 0:
        await asyncio.sleep(group.auto_delete_time)
        try:
            await update.message.delete()
        except:
            pass

def main():
    # 创建应用
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # 添加处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("enable_ai", enable_ai))
    application.add_handler(CommandHandler("disable_ai", disable_ai))
    application.add_handler(CommandHandler("setup", setup_group))
    application.add_handler(CommandHandler("setwelcome", set_welcome))
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("delete", delete_message))
    application.add_handler(CommandHandler("set_ai_config", set_ai_config))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # 添加自动删除处理器
    application.add_handler(MessageHandler(filters.ALL, auto_delete_handler))

    # 启动机器人
    application.run_polling()

if __name__ == '__main__':
    main() 