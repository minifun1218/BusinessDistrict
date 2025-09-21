#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动服务器脚本
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions import db

def main():
    """启动服务器"""
    print("正在启动城市商圈消费热度分析API服务...")
    
    try:
        # 创建应用实例
        app = create_app()
        
        # 初始化数据库
        with app.app_context():
            db.create_all()
            print("数据库初始化完成")
        
        # 启动服务器
        print("服务器启动成功！")
        print("API地址: http://localhost:3000")
        print("健康检查: http://localhost:3000/api/health")
        print("API文档: http://localhost:3000/api/docs")
        print("按 Ctrl+C 停止服务器")
        
        app.run(
            host='0.0.0.0',
            port=3000,
            debug=True,
            threaded=True
        )
        
    except Exception as e:
        print(f"启动服务器失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
