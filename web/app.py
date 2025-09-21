#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
城市商圈消费热度可视化分析系统 - Flask API服务
主应用入口文件
"""

import os
from flask import Flask
from flask_cors import CORS
from app import create_app

# 创建Flask应用实例
app = create_app()

# 启用CORS跨域支持
CORS(app, 
     origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

if __name__ == '__main__':
    # 开发环境配置
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.environ.get('PORT', 3000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"启动城市商圈消费热度分析API服务")
    print(f"服务地址: http://{host}:{port}")
    print(f"调试模式: {'开启' if debug_mode else '关闭'}")
    print(f"CORS支持: 已启用")
    
    app.run(
        host=host,
        port=port,
        debug=debug_mode,
        threaded=True
    )
