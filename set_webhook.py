import requests
import os
from dotenv import load_dotenv

load_dotenv()

def set_webhook():
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    VERCEL_URL = os.getenv('VERCEL_URL', 'your-vercel-url.vercel.app')
    
    webhook_url = f"https://{VERCEL_URL}/api/webhook"
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
    
    response = requests.post(api_url, json={'url': webhook_url})
    print(response.json())

if __name__ == '__main__':
    set_webhook() 