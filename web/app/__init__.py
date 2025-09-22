#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask应用工厂函数
"""

import os
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config.config import Config
from app.extensions import db, migrate, jwt
from app.utils.response import success_response, error_response

def create_app(config_class=Config):
    """创建Flask应用实例"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # 初始化限流器
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"]
    )
    
    # 注册蓝图
    from app.api.auth import auth_bp
    from app.api.cities import cities_bp
    from app.api.business import business_bp
    from app.api.analytics import analytics_bp
    from app.api.crawler import crawler_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(cities_bp, url_prefix='/api/cities')
    app.register_blueprint(business_bp, url_prefix='/api/business-areas')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(crawler_bp, url_prefix='/api/crawler')
    
    # 添加兼容性路由 - 将 /api/business 重定向到 /api/business-areas
    @app.route('/api/business/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    def business_redirect(path):
        from flask import request, redirect, url_for
        # 重定向到正确的端点
        return redirect(f'/api/business-areas/{path}?{request.query_string.decode()}', code=301)
    
    # 注册错误处理器
    @app.errorhandler(404)
    def not_found(error):
        return error_response('请求的资源不存在', 404)
    
    @app.errorhandler(500)
    def internal_error(error):
        return error_response('服务器内部错误', 500)
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return error_response('请求过于频繁，请稍后再试', 429)
    
    # 健康检查接口
    @app.route('/api/health')
    def health_check():
        return success_response({
            'status': 'healthy',
            'service': '城市商圈消费热度分析API',
            'version': '1.0.0'
        })
    
    # API文档接口
    @app.route('/api/docs')
    def api_docs():
        return success_response({
            'title': '城市商圈消费热度可视化分析系统 API',
            'version': '1.0.0',
            'description': '提供城市、商圈、数据分析等相关接口',
            'endpoints': {
                'auth': '/api/auth - 用户认证相关接口',
                'cities': '/api/cities - 城市数据相关接口',
                'business': '/api/business-areas - 商圈数据相关接口',
                'analytics': '/api/analytics - 数据分析相关接口',
                'crawler': '/api/crawler - 数据爬虫相关接口'
            }
        })
    
    # 注册CLI命令
    from app.crawler.commands import register_commands
    register_commands(app)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app
