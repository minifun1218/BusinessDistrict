#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据源系统测试脚本
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions import db
from app.models.city import City
from app.data_sources.data_manager import DataSourceManager

def test_data_sources_basic():
    """测试数据源基本功能"""
    print("=== 测试数据源基本功能 ===")
    
    app = create_app()
    
    with app.app_context():
        # 初始化数据源管理器
        baidu_key = app.config.get('BAIDU_MAP_AK')
        amap_key = app.config.get('AMAP_KEY')
        
        with DataSourceManager(baidu_key, amap_key) as data_manager:
            # 测试数据源连通性
            print("1. 测试数据源连通性...")
            results = data_manager.test_connections()
            
            for source_name, result in results.items():
                status = "✅" if result['status'] == 'ok' else "❌"
                print(f"   {status} {source_name}: {result['status']} - {result.get('message', '')}")
            
            # 获取统计信息
            print("\n2. 获取数据源统计信息...")
            stats = data_manager.get_stats()
            print(f"   可用数据源: {', '.join(stats['available_sources'])}")
            
            return True

def test_mock_city_data():
    """使用模拟数据测试数据获取"""
    print("\n=== 测试数据获取功能 ===")
    
    app = create_app()
    
    with app.app_context():
        # 确保有测试城市数据
        test_city = City.query.filter_by(name='北京').first()
        if not test_city:
            test_city = City(
                id='110000',
                name='北京',
                code='BJ',
                level='city',
                longitude=116.4074,
                latitude=39.9042,
                is_hot=True,
                pinyin='beijing',
                pinyin_abbr='bj'
            )
            db.session.add(test_city)
            db.session.commit()
            print("   创建测试城市: 北京")
        
        # 初始化数据源管理器
        baidu_key = app.config.get('BAIDU_MAP_AK')
        amap_key = app.config.get('AMAP_KEY')
        
        with DataSourceManager(baidu_key, amap_key) as data_manager:
            print("1. 测试获取城市数据...")
            
            # 只使用大众点评模拟数据进行测试
            result = data_manager.fetch_city_data(
                city_id=test_city.id,
                city_name=test_city.name,
                data_sources=['dianping'],
                update_existing=True
            )
            
            if result['success']:
                print(f"   ✅ 数据获取成功!")
                print(f"   商圈数量: {result['areas_count']}")
                print(f"   店铺数量: {result['stores_count']}")
                print(f"   使用数据源: {', '.join(result['data_sources_used'])}")
                return True
            else:
                print(f"   ❌ 数据获取失败: {result.get('error')}")
                return False

def test_api_endpoints():
    """测试API接口"""
    print("\n=== 测试API接口 ===")
    
    app = create_app()
    client = app.test_client()
    
    with app.app_context():
        # 测试数据源状态接口
        print("1. 测试数据源状态接口...")
        response = client.get('/api/crawler/status')
        
        if response.status_code == 200:
            print("   ✅ 状态接口正常")
            data = response.get_json()
            print(f"   可用数据源: {', '.join(data['data']['available_sources'])}")
        else:
            print(f"   ❌ 状态接口异常: {response.status_code}")
        
        # 测试数据源测试接口
        print("\n2. 测试数据源连接接口...")
        response = client.get('/api/crawler/test')
        
        if response.status_code == 200:
            print("   ✅ 测试接口正常")
            data = response.get_json()
            for source, result in data['data'].items():
                status = "✅" if result['status'] == 'ok' else "❌"
                print(f"   {status} {source}: {result['status']}")
        else:
            print(f"   ❌ 测试接口异常: {response.status_code}")
        
        # 测试数据质量接口
        print("\n3. 测试数据质量接口...")
        response = client.get('/api/crawler/data-quality')
        
        if response.status_code == 200:
            print("   ✅ 数据质量接口正常")
            data = response.get_json()
            areas_info = data['data']['areas']
            stores_info = data['data']['stores']
            print(f"   商圈总数: {areas_info['total']}")
            print(f"   店铺总数: {stores_info['total']}")
        else:
            print(f"   ❌ 数据质量接口异常: {response.status_code}")

def main():
    """主测试函数"""
    print("开始测试数据源系统...")
    print("注意：这是使用官方开放API的数据源系统，不是爬虫！")
    
    try:
        # 基本功能测试
        if not test_data_sources_basic():
            print("❌ 基本功能测试失败")
            return False
        
        # 数据获取测试
        if not test_mock_city_data():
            print("❌ 数据获取测试失败")
            return False
        
        # API接口测试
        test_api_endpoints()
        
        print("\n🎉 所有测试完成!")
        print("\n📋 系统特点:")
        print("   ✅ 使用官方开放API，合规安全")
        print("   ✅ 支持多数据源并发获取")
        print("   ✅ 自动数据去重和合并")
        print("   ✅ 完善的错误处理机制")
        print("   ✅ 支持增量和全量更新")
        
        print("\n📚 使用说明:")
        print("   1. 配置API密钥 (BAIDU_MAP_AK, AMAP_KEY)")
        print("   2. 调用 /api/crawler/crawl-city 获取城市数据")
        print("   3. 查看 DATA_SOURCES_README.md 了解详细用法")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    main()
