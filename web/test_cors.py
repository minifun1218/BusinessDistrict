#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORS测试脚本 - 验证所有分析接口是否正常工作
"""

import requests
import json

BASE_URL = "http://localhost:3000/api"

def test_cors_options(endpoint):
    """测试OPTIONS预检请求"""
    url = f"{BASE_URL}/{endpoint}"
    headers = {
        'Origin': 'http://localhost:5173',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type'
    }
    
    try:
        response = requests.options(url, headers=headers)
        print(f"✅ OPTIONS {endpoint}: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ OPTIONS {endpoint}: {str(e)}")
        return False

def test_get_request(endpoint):
    """测试GET请求"""
    url = f"{BASE_URL}/{endpoint}"
    
    try:
        response = requests.get(url)
        print(f"✅ GET {endpoint}: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ GET {endpoint}: {str(e)}")
        return False

def test_post_request(endpoint, data=None):
    """测试POST请求"""
    url = f"{BASE_URL}/{endpoint}"
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, json=data or {})
        print(f"✅ POST {endpoint}: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ POST {endpoint}: {str(e)}")
        return False

def main():
    print("🚀 开始测试CORS和API接口...")
    print("=" * 50)
    
    # 测试健康检查
    print("📊 测试基础接口:")
    test_get_request("health")
    
    print("\n📈 测试分析接口:")
    
    # 测试所有分析接口
    analytics_endpoints = [
        "analytics/hot-ranking",
        "analytics/hourly-flow", 
        "analytics/category-distribution",
        "analytics/sentiment-analysis",
        "analytics/consumption-trend",
        "analytics/radar-comparison",
        "analytics/heatmap"
    ]
    
    for endpoint in analytics_endpoints:
        # 测试OPTIONS
        test_cors_options(endpoint)
        # 测试GET
        test_get_request(endpoint)
        
        # 对于支持POST的接口，也测试POST
        if 'radar-comparison' in endpoint:
            test_post_request(endpoint, {"areaIds": []})
        
        print()
    
    print("🎉 CORS和API测试完成！")

if __name__ == "__main__":
    main()
