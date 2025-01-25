import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

class Config:
    # 基本配置
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_API_URL = os.getenv('GEMINI_API_URL')
    ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(',')))
    
    # AI配置默认值
    DEFAULT_AI_CONFIG: Dict[str, Any] = {
        'temperature': 0.7,
        'max_tokens': 1000,
        'system_prompt': 'You are a helpful assistant.'
    }
    
    # 环境配置
    IS_VERCEL = bool(os.getenv('VERCEL'))
    DEBUG = not IS_VERCEL
    PORT = int(os.getenv('PORT', 8000))
    
    # Web配置
    STATIC_DIR = 'static'
    TEMPLATE_DIR = 'templates'
    
    @classmethod
    def get_webhook_url(cls) -> str:
        if cls.IS_VERCEL:
            return f"https://{os.getenv('VERCEL_URL')}/api/webhook"
        return f"http://localhost:{cls.PORT}/api/webhook"

config = Config() 