from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from utils.logger import logger
from utils.helpers import handle_errors
from models import storage
from utils.config import config
from typing import Dict, Any

router = APIRouter()

@router.get("/stats")
@handle_errors
async def get_stats():
    """获取系统统计信息"""
    try:
        stats = {
            "total_groups": len(storage.get_all_groups()),
            "total_banned": len(storage.get_banned_users()),
            "ai_enabled_groups": len([g for g in storage.get_all_groups() if g.get('ai_enabled')]),
            "system_uptime": storage.get_uptime(),
            "environment": "vercel" if config.IS_VERCEL else "local"
        }
        return JSONResponse(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def telegram_webhook(request: Request):
    """处理 Telegram webhook"""
    try:
        update_data = await request.json()
        from api.bot import bot_handler
        success = await bot_handler.process_update(update_data)
        
        if success:
            return JSONResponse({"status": "success"})
        else:
            logger.error("Failed to process update")
            raise HTTPException(status_code=500, detail="Failed to process update")
            
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai_config")
@handle_errors
async def update_ai_config(request: Request):
    """更新AI配置"""
    data = await request.json()
    
    # 验证配置
    if 'temperature' in data:
        temp = float(data['temperature'])
        if not 0 <= temp <= 1:
            return JSONResponse(
                {"error": "Temperature must be between 0 and 1"}, 
                status_code=400
            )
    
    if 'max_tokens' in data:
        tokens = int(data['max_tokens'])
        if not 100 <= tokens <= 2000:
            return JSONResponse(
                {"error": "Max tokens must be between 100 and 2000"}, 
                status_code=400
            )
    
    storage.update_ai_config(data)
    return JSONResponse({"status": "success"}) 