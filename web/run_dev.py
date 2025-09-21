#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开发环境启动脚本
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask
from flask_cors import CORS
from app import create_app
from app.extensions import db
from app.models.city import City

def init_basic_data():
    """初始化基础数据"""
    # 检查是否已有城市数据
    if City.query.count() == 0:
        print("正在初始化城市数据...")
        cities_data = [
            {'id': '110000', 'name': '北京', 'code': 'BJ', 'level': 'city', 'longitude': 116.4074, 'latitude': 39.9042, 'is_hot': True, 'pinyin': 'beijing', 'pinyin_abbr': 'bj'},
            {'id': '310000', 'name': '上海', 'code': 'SH', 'level': 'city', 'longitude': 121.4737, 'latitude': 31.2304, 'is_hot': True, 'pinyin': 'shanghai', 'pinyin_abbr': 'sh'},
            {'id': '440100', 'name': '广州', 'code': 'GZ', 'level': 'city', 'longitude': 113.2644, 'latitude': 23.1291, 'is_hot': True, 'pinyin': 'guangzhou', 'pinyin_abbr': 'gz'},
            {'id': '440300', 'name': '深圳', 'code': 'SZ', 'level': 'city', 'longitude': 114.0579, 'latitude': 22.5431, 'is_hot': True, 'pinyin': 'shenzhen', 'pinyin_abbr': 'sz'},
            {'id': '330100', 'name': '杭州', 'code': 'HZ', 'level': 'city', 'longitude': 120.1551, 'latitude': 30.2741, 'is_hot': True, 'pinyin': 'hangzhou', 'pinyin_abbr': 'hz'},
        ]
        
        for city_data in cities_data:
            city = City(**city_data)
            db.session.add(city)
        
        db.session.commit()
        print(f"已初始化 {len(cities_data)} 个城市")
    else:
        print(f"数据库中已有 {City.query.count()} 个城市")

def main():
    """主函数"""
    print("🚀 启动开发服务器...")
    
    try:
        # 创建应用
        app = create_app()
        
        # 配置CORS - 允许所有来源（仅开发环境）
        CORS(app, 
             origins="*",  # 开发环境允许所有来源
             supports_credentials=True,
             allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
             methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'])
        
        # 添加CORS预检请求处理
        @app.before_request
        def handle_preflight():
            from flask import request
            if request.method == "OPTIONS":
                from flask import make_response
                response = make_response()
                response.headers.add("Access-Control-Allow-Origin", "*")
                response.headers.add('Access-Control-Allow-Headers', "*")
                response.headers.add('Access-Control-Allow-Methods', "*")
                return response
        
        # 添加响应头
        @app.after_request
        def after_request(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
            response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
            return response
        
        # 初始化数据库
        with app.app_context():
            db.create_all()
            init_basic_data()
        
        print("✅ 服务器配置完成")
        print(f"📍 API地址: http://localhost:3000")
        print(f"🏥 健康检查: http://localhost:3000/api/health")
        print(f"📚 API文档: http://localhost:3000/api/docs")
        print(f"🌐 CORS: 已启用（开发模式）")
        print("按 Ctrl+C 停止服务器")
        
        # 启动服务器
        app.run(
            host='0.0.0.0',
            port=3000,
            debug=True,
            threaded=True
        )
        
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
