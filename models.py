from sqlalchemy import create_engine, Column, Integer, String, Boolean, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()
engine = create_engine('sqlite:///bot.db')
Session = sessionmaker(bind=engine)

class Group(Base):
    __tablename__ = 'groups'
    
    chat_id = Column(Integer, primary_key=True)
    title = Column(String)
    ai_enabled = Column(Boolean, default=False)
    welcome_message = Column(String)
    auto_delete_time = Column(Integer, default=0)  # 自动删除消息的时间(秒),0表示不删除
    ai_config = Column(JSON)  # AI相关配置
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class BannedUser(Base):
    __tablename__ = 'banned_users'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    user_id = Column(Integer)
    banned_until = Column(DateTime)
    reason = Column(String)

# 创建数据库表
Base.metadata.create_all(engine) 