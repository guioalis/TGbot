import logging
from functools import wraps
from fastapi import HTTPException
from typing import Callable, Any
from utils.logger import logger

logger = logging.getLogger(__name__)

def handle_errors(func: Callable) -> Callable:
    """错误处理装饰器"""
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            # 直接重新抛出 HTTP 异常
            raise
        except Exception as e:
            # 记录错误并转换为 HTTP 异常
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    return wrapper

def validate_admin(user_id: int) -> bool:
    """验证是否是管理员"""
    from utils.config import config
    return user_id in config.ADMIN_IDS

def format_uptime(seconds: float) -> str:
    """格式化运行时间"""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{days}天 {hours}小时 {minutes}分钟"

def validate_request(func: Callable) -> Callable:
    """请求验证装饰器"""
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            # 在这里添加请求验证逻辑
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Validation error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
    return wrapper 