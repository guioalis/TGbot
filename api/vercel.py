try:
    import sys
    import os
    import logging
    
    # 配置基本日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # 添加项目根目录到 Python 路径
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(root_dir)
    
    # 记录 Python 路径和当前目录
    logger.info(f"Python path: {sys.path}")
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info(f"Root directory: {root_dir}")
    
    # 尝试导入依赖
    try:
        import fastapi
        logger.info("FastAPI imported successfully")
    except ImportError as e:
        logger.error(f"Failed to import FastAPI: {e}")
        raise
    
    # 导入应用
    from main import app
    logger.info("Main app imported successfully")
    
    # 导出 handler
    handler = app

except Exception as e:
    logging.error(f"Error in vercel.py: {str(e)}")
    raise

# Vercel 无服务器函数入口点
handler = app 