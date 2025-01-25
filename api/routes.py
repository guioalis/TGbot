from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from utils.helpers import handle_errors
from models import storage
from utils.config import config
from typing import Dict, Any

router = APIRouter()

@router.get("/stats")
@handle_errors
async def get_stats():
    """获取系统统计信息"""
    stats = {
        "total_groups": len(storage.get_all_groups()),
        "total_banned": len(storage.get_banned_users()),
        "ai_enabled_groups": len([g for g in storage.get_all_groups() if g.get('ai_enabled')]),
        "system_uptime": storage.get_uptime(),
        "environment": "vercel" if config.IS_VERCEL else "local"
    }
    return JSONResponse(stats)

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