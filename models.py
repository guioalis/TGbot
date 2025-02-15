import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from utils.config import config

logger = logging.getLogger(__name__)

class Storage:
    def __init__(self):
        # 使用内存存储
        self._groups: Dict[str, Dict[str, Any]] = {}
        self._banned: List[Dict[str, Any]] = []
        self.start_time: datetime = datetime.utcnow()
        self.ai_config: Dict[str, Any] = config.DEFAULT_AI_CONFIG.copy()
    
    def get_group(self, chat_id: int) -> Dict[str, Any]:
        return self._groups.get(str(chat_id), {})
    
    def save_group(self, chat_id: int, data: Dict[str, Any]) -> None:
        self._groups[str(chat_id)] = data
    
    def get_all_groups(self) -> List[dict]:
        return [
            {"chat_id": int(chat_id), **data}
            for chat_id, data in self._groups.items()
        ]
    
    def add_banned_user(self, chat_id: int, user_id: int, banned_until: str, reason: str):
        self._banned.append({
            "chat_id": chat_id,
            "user_id": user_id,
            "banned_until": banned_until,
            "reason": reason
        })
    
    def get_banned_users(self) -> List[dict]:
        self.remove_expired_bans()
        return self._banned
    
    def remove_expired_bans(self):
        current_time = datetime.utcnow().isoformat()
        self._banned = [
            ban for ban in self._banned
            if ban["banned_until"] > current_time
        ]

    def get_timestamp(self) -> str:
        """获取当前时间戳"""
        return datetime.utcnow().isoformat()

    def update_ai_config(self, config: Dict[str, Any]):
        """更新AI配置"""
        self.ai_config.update(config)

    def get_uptime(self) -> str:
        """获取系统运行时间"""
        return (datetime.utcnow() - self.start_time).total_seconds()

# 创建全局存储实例
storage = Storage() 