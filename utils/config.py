import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_API_URL = os.getenv('GEMINI_API_URL')
    ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(',')))
    
    # AI配置默认值
    DEFAULT_AI_CONFIG = {
        'temperature': 0.7,
        'max_tokens': 1000,
        'system_prompt': 'You are a helpful assistant.'
    }
    
    # 环境配置
    IS_VERCEL = bool(os.getenv('VERCEL'))
    DEBUG = not IS_VERCEL
    
    @classmethod
    def get_webhook_url(cls):
        if cls.IS_VERCEL:
            return f"https://{os.getenv('VERCEL_URL')}/api/webhook"
        return "http://localhost:8000/api/webhook"

config = Config() 