#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一响应格式工具
"""

from flask import jsonify
from datetime import datetime

def success_response(data=None, message='success', code=200):
    """成功响应"""
    response = {
        'code': code,
        'message': message,
        'data': data,
        'timestamp': int(datetime.now().timestamp())
    }
    return jsonify(response), 200

def error_response(message='error', code=400, data=None):
    """错误响应"""
    response = {
        'code': code,
        'message': message,
        'data': data,
        'timestamp': int(datetime.now().timestamp())
    }
    return jsonify(response), code

def paginated_response(items, total, page, per_page, message='success'):
    """分页响应"""
    total_pages = (total + per_page - 1) // per_page
    
    response = {
        'code': 200,
        'message': message,
        'data': {
            'list': items,
            'total': total,
            'page': page,
            'pageSize': per_page,
            'totalPages': total_pages,
            'hasNext': page < total_pages,
            'hasPrev': page > 1
        },
        'timestamp': int(datetime.now().timestamp())
    }
    return jsonify(response), 200
