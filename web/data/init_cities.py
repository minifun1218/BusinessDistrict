#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化城市数据
"""

from app.models.city import City
from app.extensions import db

def init_cities():
    """初始化城市数据"""
    
    # 检查是否已有数据
    if City.query.first():
        print("城市数据已存在，跳过初始化")
        return
    
    # 热门城市数据
    cities_data = [
        {
            'id': 'beijing',
            'name': '北京',
            'code': '110000',
            'level': 'city',
            'longitude': 116.4074,
            'latitude': 39.9042,
            'population': 21542000,
            'area': 16410.54,
            'economic_level': 'high',
            'is_hot': True,
            'pinyin': 'beijing',
            'pinyin_abbr': 'BJ'
        },
        {
            'id': 'shanghai',
            'name': '上海',
            'code': '310000',
            'level': 'city',
            'longitude': 121.4737,
            'latitude': 31.2304,
            'population': 26317104,
            'area': 6340.5,
            'economic_level': 'high',
            'is_hot': True,
            'pinyin': 'shanghai',
            'pinyin_abbr': 'SH'
        },
        {
            'id': 'guangzhou',
            'name': '广州',
            'code': '440100',
            'level': 'city',
            'longitude': 113.2644,
            'latitude': 23.1291,
            'population': 15906000,
            'area': 7434.4,
            'economic_level': 'high',
            'is_hot': True,
            'pinyin': 'guangzhou',
            'pinyin_abbr': 'GZ'
        },
        {
            'id': 'shenzhen',
            'name': '深圳',
            'code': '440300',
            'level': 'city',
            'longitude': 114.0579,
            'latitude': 22.5431,
            'population': 13438800,
            'area': 1997.47,
            'economic_level': 'high',
            'is_hot': True,
            'pinyin': 'shenzhen',
            'pinyin_abbr': 'SZ'
        },
        {
            'id': 'hangzhou',
            'name': '杭州',
            'code': '330100',
            'level': 'city',
            'longitude': 120.1614,
            'latitude': 30.2936,
            'population': 12196000,
            'area': 16853.57,
            'economic_level': 'high',
            'is_hot': True,
            'pinyin': 'hangzhou',
            'pinyin_abbr': 'HZ'
        },
        {
            'id': 'nanjing',
            'name': '南京',
            'code': '320100',
            'level': 'city',
            'longitude': 118.7969,
            'latitude': 32.0603,
            'population': 9423400,
            'area': 6587.02,
            'economic_level': 'high',
            'is_hot': True,
            'pinyin': 'nanjing',
            'pinyin_abbr': 'NJ'
        },
        {
            'id': 'wuhan',
            'name': '武汉',
            'code': '420100',
            'level': 'city',
            'longitude': 114.2734,
            'latitude': 30.5801,
            'population': 13648000,
            'area': 8569.15,
            'economic_level': 'high',
            'is_hot': True,
            'pinyin': 'wuhan',
            'pinyin_abbr': 'WH'
        },
        {
            'id': 'chengdu',
            'name': '成都',
            'code': '510100',
            'level': 'city',
            'longitude': 104.0668,
            'latitude': 30.5728,
            'population': 21192000,
            'area': 14335,
            'economic_level': 'high',
            'is_hot': True,
            'pinyin': 'chengdu',
            'pinyin_abbr': 'CD'
        },
        {
            'id': 'tianjin',
            'name': '天津',
            'code': '120000',
            'level': 'city',
            'longitude': 117.1901,
            'latitude': 39.1084,
            'population': 15618000,
            'area': 11966.45,
            'economic_level': 'high',
            'is_hot': True,
            'pinyin': 'tianjin',
            'pinyin_abbr': 'TJ'
        },
        {
            'id': 'chongqing',
            'name': '重庆',
            'code': '500000',
            'level': 'city',
            'longitude': 106.9123,
            'latitude': 29.4316,
            'population': 32054159,
            'area': 82402.95,
            'economic_level': 'high',
            'is_hot': True,
            'pinyin': 'chongqing',
            'pinyin_abbr': 'CQ'
        },
        {
            'id': 'suzhou',
            'name': '苏州',
            'code': '320500',
            'level': 'city',
            'longitude': 120.6195,
            'latitude': 31.3114,
            'population': 12952000,
            'area': 8657.32,
            'economic_level': 'high',
            'is_hot': False,
            'pinyin': 'suzhou',
            'pinyin_abbr': 'SZ'
        },
        {
            'id': 'xian',
            'name': '西安',
            'code': '610100',
            'level': 'city',
            'longitude': 108.9402,
            'latitude': 34.3416,
            'population': 12952907,
            'area': 10752,
            'economic_level': 'medium',
            'is_hot': False,
            'pinyin': 'xian',
            'pinyin_abbr': 'XA'
        },
        {
            'id': 'qingdao',
            'name': '青岛',
            'code': '370200',
            'level': 'city',
            'longitude': 120.3826,
            'latitude': 36.0671,
            'population': 10071722,
            'area': 11293,
            'economic_level': 'medium',
            'is_hot': False,
            'pinyin': 'qingdao',
            'pinyin_abbr': 'QD'
        },
        {
            'id': 'zhengzhou',
            'name': '郑州',
            'code': '410100',
            'level': 'city',
            'longitude': 113.6254,
            'latitude': 34.7466,
            'population': 12600574,
            'area': 7567.18,
            'economic_level': 'medium',
            'is_hot': False,
            'pinyin': 'zhengzhou',
            'pinyin_abbr': 'ZZ'
        },
        {
            'id': 'dalian',
            'name': '大连',
            'code': '210200',
            'level': 'city',
            'longitude': 121.6147,
            'latitude': 38.9140,
            'population': 7450785,
            'area': 12573.85,
            'economic_level': 'medium',
            'is_hot': False,
            'pinyin': 'dalian',
            'pinyin_abbr': 'DL'
        },
        {
            'id': 'xiamen',
            'name': '厦门',
            'code': '350200',
            'level': 'city',
            'longitude': 118.1689,
            'latitude': 24.4905,
            'population': 5163970,
            'area': 1700.61,
            'economic_level': 'high',
            'is_hot': False,
            'pinyin': 'xiamen',
            'pinyin_abbr': 'XM'
        },
        {
            'id': 'jinan',
            'name': '济南',
            'code': '370100',
            'level': 'city',
            'longitude': 117.0009,
            'latitude': 36.6758,
            'population': 9202432,
            'area': 10244.45,
            'economic_level': 'medium',
            'is_hot': False,
            'pinyin': 'jinan',
            'pinyin_abbr': 'JN'
        },
        {
            'id': 'ningbo',
            'name': '宁波',
            'code': '330200',
            'level': 'city',
            'longitude': 121.5440,
            'latitude': 29.8683,
            'population': 9404283,
            'area': 9816,
            'economic_level': 'high',
            'is_hot': False,
            'pinyin': 'ningbo',
            'pinyin_abbr': 'NB'
        }
    ]
    
    # 批量插入城市数据
    try:
        for city_data in cities_data:
            city = City(**city_data)
            db.session.add(city)
        
        db.session.commit()
        print(f"成功初始化 {len(cities_data)} 个城市数据")
        
    except Exception as e:
        db.session.rollback()
        print(f"初始化城市数据失败: {str(e)}")
        raise

if __name__ == '__main__':
    from app import create_app
    
    app = create_app()
    with app.app_context():
        init_cities()
