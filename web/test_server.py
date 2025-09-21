#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Flask服务器
"""

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)

# 启用CORS
CORS(app, origins=['http://localhost:5173', 'http://127.0.0.1:5173'])

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'status': 'healthy',
            'service': '城市商圈消费热度分析API',
            'version': '1.0.0'
        }
    })

@app.route('/api/cities/hot', methods=['GET'])
def get_hot_cities():
    return jsonify({
        'code': 200,
        'message': '获取热门城市成功',
        'data': [
            {'id': 'beijing', 'name': '北京', 'code': '110000'},
            {'id': 'shanghai', 'name': '上海', 'code': '310000'},
            {'id': 'guangzhou', 'name': '广州', 'code': '440100'},
            {'id': 'shenzhen', 'name': '深圳', 'code': '440300'}
        ]
    })

@app.route('/api/analytics/hot-ranking', methods=['GET'])
def get_hot_ranking():
    return jsonify({
        'code': 200,
        'message': '获取热度排行成功',
        'data': [
            {'name': '三里屯', 'hotValue': 9500, 'growthRate': 15.2},
            {'name': '王府井', 'hotValue': 8800, 'growthRate': 8.7},
            {'name': '西单', 'hotValue': 8200, 'growthRate': 12.1}
        ]
    })

if __name__ == '__main__':
    print("🚀 启动测试Flask服务器")
    print("📍 服务地址: http://127.0.0.1:3000")
    print("💚 健康检查: http://127.0.0.1:3000/api/health")
    
    app.run(host='127.0.0.1', port=3000, debug=True)
