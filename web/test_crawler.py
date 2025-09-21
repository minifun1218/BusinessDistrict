#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫功能测试脚本
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions import db
from app.models.city import City
from app.crawler.crawler_manager import CrawlerManager

def test_crawler_basic():
    """测试爬虫基本功能"""
    print("=== 测试爬虫基本功能 ===")
    
    app = create_app()
    
    with app.app_context():
        # 初始化爬虫管理器
        baidu_key = app.config.get('BAIDU_MAP_AK')
        amap_key = app.config.get('AMAP_KEY')
        
        with CrawlerManager(baidu_key, amap_key) as crawler_manager:
            # 测试爬虫连通性
            print("1. 测试爬虫连通性...")
            results = crawler_manager.test_crawlers()
            
            for crawler_name, result in results.items():
                status = "✅" if result['status'] == 'ok' else "❌"
                print(f"   {status} {crawler_name}: {result['status']}")
            
            # 获取统计信息
            print("\n2. 获取爬虫统计信息...")
            stats = crawler_manager.get_crawler_stats()
            print(f"   可用爬虫: {', '.join(stats['available_crawlers'])}")
            
            return True

def test_crawler_with_mock_city():
    """使用模拟城市测试爬虫"""
    print("\n=== 测试爬虫数据爬取 ===")
    
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
        
        # 初始化爬虫管理器
        baidu_key = app.config.get('BAIDU_MAP_AK')
        amap_key = app.config.get('AMAP_KEY')
        
        with CrawlerManager(baidu_key, amap_key) as crawler_manager:
            print("1. 测试爬取城市数据...")
            
            # 只使用大众点评爬虫（模拟数据）进行测试
            result = crawler_manager.crawl_city_data(
                city_id=test_city.id,
                city_name=test_city.name,
                crawlers=['dianping'],
                update_existing=True
            )
            
            if result['success']:
                print(f"   ✅ 爬取成功!")
                print(f"   商圈数量: {result['areas_count']}")
                print(f"   店铺数量: {result['stores_count']}")
                print(f"   使用爬虫: {', '.join(result['crawlers_used'])}")
                return True
            else:
                print(f"   ❌ 爬取失败: {result.get('error')}")
                return False

def test_api_endpoints():
    """测试API接口"""
    print("\n=== 测试API接口 ===")
    
    app = create_app()
    client = app.test_client()
    
    with app.app_context():
        # 测试爬虫状态接口
        print("1. 测试爬虫状态接口...")
        response = client.get('/api/crawler/status')
        
        if response.status_code == 200:
            print("   ✅ 状态接口正常")
            data = response.get_json()
            print(f"   可用爬虫: {', '.join(data['data']['available_crawlers'])}")
        else:
            print(f"   ❌ 状态接口异常: {response.status_code}")
        
        # 测试爬虫测试接口
        print("\n2. 测试爬虫测试接口...")
        response = client.get('/api/crawler/test')
        
        if response.status_code == 200:
            print("   ✅ 测试接口正常")
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
    print("开始测试爬虫系统...")
    
    try:
        # 基本功能测试
        if not test_crawler_basic():
            print("❌ 基本功能测试失败")
            return False
        
        # 数据爬取测试
        if not test_crawler_with_mock_city():
            print("❌ 数据爬取测试失败")
            return False
        
        # API接口测试
        test_api_endpoints()
        
        print("\n🎉 所有测试完成!")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    main()
