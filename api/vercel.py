try:
    import sys
    import os
    import logging
    from pathlib import Path
    
    # 配置基本日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # 添加项目根目录到 Python 路径
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(root_dir)
    
    # 添加 .pip 目录到 Python 路径
    pip_dir = os.path.join(root_dir, '.pip')
    if os.path.exists(pip_dir):
        sys.path.append(pip_dir)
    
    # 记录环境信息
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Python path: {sys.path}")
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info(f"Directory contents: {os.listdir('.')}")
    logger.info(f"Root directory: {root_dir}")
    if os.path.exists('.pip'):
        logger.info(f"Pip directory contents: {os.listdir('.pip')}")
    
    # 尝试导入依赖
    try:
        import fastapi
        logger.info("FastAPI imported successfully")
    except ImportError as e:
        logger.error(f"Failed to import FastAPI: {e}")
        # 尝试手动安装
        import subprocess
        logger.info("Attempting to install FastAPI...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi==0.95.2"])
        import fastapi
    
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