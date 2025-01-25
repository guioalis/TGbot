import json
import os
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class Storage:
    def __init__(self):
        # Vercel 环境使用 /tmp 目录
        self.base_dir = '/tmp' if os.getenv('VERCEL') else 'data'
        self.groups_file = f'{self.base_dir}/groups.json'
        self.banned_file = f'{self.base_dir}/banned.json'
        
        # 创建数据目录
        os.makedirs(self.base_dir, exist_ok=True)
        
        # 初始化存储文件
        self._init_files()
    
    def _init_files(self):
        """初始化存储文件"""
        try:
            if not os.path.exists(self.groups_file):
                self._save_groups({})
            if not os.path.exists(self.banned_file):
                self._save_banned([])
        except Exception as e:
            logger.error(f"Error initializing storage files: {e}")
    
    def _load_groups(self) -> Dict:
        try:
            if os.path.exists(self.groups_file):
                with open(self.groups_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading groups: {e}")
        return {}
    
    def _save_groups(self, data: Dict):
        try:
            with open(self.groups_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving groups: {e}")
    
    def _load_banned(self) -> List:
        try:
            with open(self.banned_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _save_banned(self, data: List):
        with open(self.banned_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_group(self, chat_id: int) -> dict:
        groups = self._load_groups()
        return groups.get(str(chat_id), {})
    
    def save_group(self, chat_id: int, data: dict):
        groups = self._load_groups()
        groups[str(chat_id)] = data
        self._save_groups(groups)
    
    def get_all_groups(self) -> List[dict]:
        groups = self._load_groups()
        return [
            {"chat_id": int(chat_id), **data}
            for chat_id, data in groups.items()
        ]
    
    def add_banned_user(self, chat_id: int, user_id: int, banned_until: str, reason: str):
        banned = self._load_banned()
        banned.append({
            "chat_id": chat_id,
            "user_id": user_id,
            "banned_until": banned_until,
            "reason": reason
        })
        self._save_banned(banned)
    
    def get_banned_users(self) -> List[dict]:
        return self._load_banned()
    
    def remove_expired_bans(self):
        banned = self._load_banned()
        current_time = datetime.utcnow().isoformat()
        active_bans = [
            ban for ban in banned
            if ban["banned_until"] > current_time
        ]
        self._save_banned(active_bans)

# 创建全局存储实例
storage = Storage() 