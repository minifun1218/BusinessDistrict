#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask应用工厂函数（修复CORS预检OPTIONS与限流冲突）
"""

import os
from flask import Flask, jsonify, request, make_response
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from config.config import Config
from app.extensions import db, migrate, jwt
from app.utils.response import success_response, error_response

def create_app(config_class=Config):
    """创建Flask应用实例"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config_class)

    # ===== 初始化扩展 =====
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # ===== CORS 设置（仅作用于 /api/*，更安全也更高效）=====
    # 注意：支持凭据的话必须把 origins 写成明确来源；当前前后端本地调试一般不需要凭据
    CORS(
        app,
        resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173", "*"]}},
        supports_credentials=False,
        allow_headers=[
            "Content-Type", "Authorization", "X-Requested-With",
            "Accept", "Origin", "X-CSRF-Token"
        ],
        expose_headers=["Content-Type", "Authorization", "Content-Length", "ETag"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        max_age=86400,  # 预检结果缓存1天，减少预检次数
    )

    # ===== 限流器（对OPTIONS预检放行，否则可能返回429/401导致浏览器CORS失败）=====
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"]
    )

    @limiter.request_filter
    def _bypass_for_cors_preflight():
        # 任何 OPTIONS 预检不计入限流，直接放行
        return request.method.upper() == "OPTIONS"

    @limiter.request_filter
    def _bypass_for_health_and_docs():
        # 健康检查/文档不计流，避免CI探活或前端轮询触发限流
        p = request.path or ""
        return p.startswith("/api/health") or p.startswith("/api/docs")

    # ===== 在到达路由前，优先处理 CORS 预检 =====
    @app.before_request
    def _early_ok_for_options():
        # 某些扩展（鉴权/限流/蓝图未注册OPTIONS）可能拦截OPTIONS，这里直接200短路
        if request.method.upper() == "OPTIONS":
            resp = make_response("", 200)
            # Flask-CORS通常会自动添加必要CORS头，这里兜底再加一遍（无副作用）
            origin = request.headers.get("Origin", "*")
            req_headers = request.headers.get("Access-Control-Request-Headers", "")
            req_method = request.headers.get("Access-Control-Request-Method", "")
            resp.headers.setdefault("Access-Control-Allow-Origin", origin if origin else "*")
            resp.headers.setdefault("Vary", "Origin")
            resp.headers.setdefault("Access-Control-Allow-Credentials", "false")
            resp.headers.setdefault("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS,PATCH")
            if req_headers:
                resp.headers.setdefault("Access-Control-Allow-Headers", req_headers)
            if req_method:
                # 一些前端环境会检查回显的method；这里返回完整集合更兼容
                resp.headers.setdefault("Access-Control-Allow-Method", req_method)
            resp.headers.setdefault("Access-Control-Max-Age", "86400")
            return resp
        # 非OPTIONS正常走后续流程
        return None

    # ===== 蓝图注册 =====
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
    
    # 兼容性路由 - 将 /api/business 重定向到 /api/business-areas
    @app.route('/api/business/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    def business_redirect(path):
        from flask import request, redirect
        # 预检请求直接200返回（避免301重定向影响预检）
        if request.method.upper() == "OPTIONS":
            return "", 200
        # 非预检再做重定向
        qs = request.query_string.decode() if request.query_string else ""
        target = f"/api/business-areas/{path}" + (f"?{qs}" if qs else "")
        return redirect(target, code=307)  # 307 保留方法与body，较 301/302 更安全

    # ===== 错误处理器 =====
    @app.errorhandler(404)
    def not_found(error):
        return error_response('请求的资源不存在', 404)
    
    @app.errorhandler(500)
    def internal_error(error):
        return error_response('服务器内部错误', 500)
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        # 若真触发限流，也明确返回JSON
        return error_response('请求过于频繁，请稍后再试', 429)

    # ===== 兜底：为所有响应补齐必要CORS头（极端情况下有用）=====
    @app.after_request
    def _ensure_cors_headers(resp):
        # 仅对 /api/* 兜底
        try:
            if (request.path or "").startswith("/api/"):
                origin = request.headers.get("Origin", None)
                if origin:
                    resp.headers.setdefault("Access-Control-Allow-Origin", origin)
                    resp.headers.setdefault("Vary", "Origin")
                else:
                    resp.headers.setdefault("Access-Control-Allow-Origin", "*")
                resp.headers.setdefault("Access-Control-Allow-Credentials", "false")
                resp.headers.setdefault("Access-Control-Expose-Headers", "Content-Type, Authorization, Content-Length, ETag")
        except Exception:
            pass
        return resp

    # 健康检查
    @app.route('/api/health')
    def health_check():
        return success_response({
            'status': 'healthy',
            'service': '城市商圈消费热度分析API',
            'version': '1.0.0'
        })
    
    # API文档
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
