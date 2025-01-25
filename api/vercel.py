try:
    import sys
    import os
    
    # 添加项目根目录到 Python 路径
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from main import app
    
    # 导出 handler 供 Vercel 使用
    handler = app

except Exception as e:
    import logging
    logging.error(f"Error in vercel.py: {str(e)}")
    raise

# Vercel 无服务器函数入口点
handler = app 