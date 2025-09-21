#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化基础数据脚本
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions import db
from app.models.city import City

def init_cities():
    """初始化城市数据"""
    cities_data = [
        {
            'id': '110000',
            'name': '北京',
            'code': 'BJ',
            'level': 'city',
            'longitude': 116.4074,
            'latitude': 39.9042,
            'is_hot': True,
            'pinyin': 'beijing',
            'pinyin_abbr': 'bj'
        },
        {
            'id': '310000',
            'name': '上海',
            'code': 'SH',
            'level': 'city',
            'longitude': 121.4737,
            'latitude': 31.2304,
            'is_hot': True,
            'pinyin': 'shanghai',
            'pinyin_abbr': 'sh'
        },
        {
            'id': '440100',
            'name': '广州',
            'code': 'GZ',
            'level': 'city',
            'longitude': 113.2644,
            'latitude': 23.1291,
            'is_hot': True,
            'pinyin': 'guangzhou',
            'pinyin_abbr': 'gz'
        },
        {
            'id': '440300',
            'name': '深圳',
            'code': 'SZ',
            'level': 'city',
            'longitude': 114.0579,
            'latitude': 22.5431,
            'is_hot': True,
            'pinyin': 'shenzhen',
            'pinyin_abbr': 'sz'
        },
        {
            'id': '330100',
            'name': '杭州',
            'code': 'HZ',
            'level': 'city',
            'longitude': 120.1551,
            'latitude': 30.2741,
            'is_hot': True,
            'pinyin': 'hangzhou',
            'pinyin_abbr': 'hz'
        },
        {
            'id': '320100',
            'name': '南京',
            'code': 'NJ',
            'level': 'city',
            'longitude': 118.7969,
            'latitude': 32.0603,
            'is_hot': True,
            'pinyin': 'nanjing',
            'pinyin_abbr': 'nj'
        },
        {
            'id': '420100',
            'name': '武汉',
            'code': 'WH',
            'level': 'city',
            'longitude': 114.3055,
            'latitude': 30.5928,
            'is_hot': True,
            'pinyin': 'wuhan',
            'pinyin_abbr': 'wh'
        },
        {
            'id': '510100',
            'name': '成都',
            'code': 'CD',
            'level': 'city',
            'longitude': 104.0657,
            'latitude': 30.6595,
            'is_hot': True,
            'pinyin': 'chengdu',
            'pinyin_abbr': 'cd'
        },
        {
            'id': '610100',
            'name': '西安',
            'code': 'XA',
            'level': 'city',
            'longitude': 108.9398,
            'latitude': 34.3416,
            'is_hot': True,
            'pinyin': 'xian',
            'pinyin_abbr': 'xa'
        },
        {
            'id': '500000',
            'name': '重庆',
            'code': 'CQ',
            'level': 'city',
            'longitude': 106.5507,
            'latitude': 29.5647,
            'is_hot': True,
            'pinyin': 'chongqing',
            'pinyin_abbr': 'cq'
        }
    ]
    
    for city_data in cities_data:
        existing_city = City.query.get(city_data['id'])
        if not existing_city:
            city = City(**city_data)
            db.session.add(city)
            print(f"添加城市: {city_data['name']}")
        else:
            print(f"城市已存在: {city_data['name']}")
    
    db.session.commit()
    print(f"城市数据初始化完成，共 {len(cities_data)} 个城市")

def main():
    """主函数"""
    print("开始初始化基础数据...")
    
    app = create_app()
    
    with app.app_context():
        # 创建数据库表
        db.create_all()
        print("数据库表创建完成")
        
        # 初始化城市数据
        init_cities()
        
        print("基础数据初始化完成！")

if __name__ == '__main__':
    main()
