import logging
import sys
from utils.config import config

def setup_logger():
    # 创建日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 设置日志级别
    log_level = logging.DEBUG if config.DEBUG else logging.INFO
    
    # 配置根日志记录器
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log', encoding='utf-8')
        ]
    )
    
    # 创建应用日志记录器
    logger = logging.getLogger('miao_bot')
    logger.setLevel(log_level)
    
    return logger

logger = setup_logger() 