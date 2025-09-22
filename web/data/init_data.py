#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化数据脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..app import create_app
from ..app.extensions import db
from ..app.models.city import City
from ..app.models.business_area import BusinessArea, Store
from ..app.models.user import User
from ..app.utils.auth import hash_password

def init_cities():
    """初始化城市数据"""
    cities_data = [
        # 直辖市
        {
            'id': 'beijing', 'name': '北京', 'code': '110000', 'level': 'city',
            'longitude': 116.4074, 'latitude': 39.9042, 'population': 21540000,
            'area': 16410.54, 'economic_level': 'high', 'is_hot': True,
            'pinyin': 'beijing', 'pinyin_abbr': 'BJ'
        },
        {
            'id': 'shanghai', 'name': '上海', 'code': '310000', 'level': 'city',
            'longitude': 121.4737, 'latitude': 31.2304, 'population': 24280000,
            'area': 6340.5, 'economic_level': 'high', 'is_hot': True,
            'pinyin': 'shanghai', 'pinyin_abbr': 'SH'
        },
        {
            'id': 'guangzhou', 'name': '广州', 'code': '440100', 'level': 'city',
            'longitude': 113.2644, 'latitude': 23.1291, 'population': 15300000,
            'area': 7434.4, 'economic_level': 'high', 'is_hot': True,
            'pinyin': 'guangzhou', 'pinyin_abbr': 'GZ'
        },
        {
            'id': 'shenzhen', 'name': '深圳', 'code': '440300', 'level': 'city',
            'longitude': 114.0579, 'latitude': 22.5431, 'population': 13440000,
            'area': 1997.47, 'economic_level': 'high', 'is_hot': True,
            'pinyin': 'shenzhen', 'pinyin_abbr': 'SZ'
        },
        {
            'id': 'hangzhou', 'name': '杭州', 'code': '330100', 'level': 'city',
            'longitude': 120.1551, 'latitude': 30.2741, 'population': 11940000,
            'area': 16853.57, 'economic_level': 'high', 'is_hot': True,
            'pinyin': 'hangzhou', 'pinyin_abbr': 'HZ'
        },
        {
            'id': 'nanjing', 'name': '南京', 'code': '320100', 'level': 'city',
            'longitude': 118.7969, 'latitude': 32.0603, 'population': 9314000,
            'area': 6587.02, 'economic_level': 'high', 'is_hot': True,
            'pinyin': 'nanjing', 'pinyin_abbr': 'NJ'
        },
        {
            'id': 'wuhan', 'name': '武汉', 'code': '420100', 'level': 'city',
            'longitude': 114.2998, 'latitude': 30.5844, 'population': 11210000,
            'area': 8569.15, 'economic_level': 'medium', 'is_hot': True,
            'pinyin': 'wuhan', 'pinyin_abbr': 'WH'
        },
        {
            'id': 'chengdu', 'name': '成都', 'code': '510100', 'level': 'city',
            'longitude': 104.0665, 'latitude': 30.5723, 'population': 16330000,
            'area': 14335, 'economic_level': 'medium', 'is_hot': True,
            'pinyin': 'chengdu', 'pinyin_abbr': 'CD'
        }
    ]
    
    for city_data in cities_data:
        existing_city = City.query.get(city_data['id'])
        if not existing_city:
            city = City(**city_data)
            db.session.add(city)
    
    db.session.commit()
    print(f"✅ 已初始化 {len(cities_data)} 个城市数据")

def init_business_areas():
    """初始化商圈数据"""
    business_areas_data = [
        # 北京商圈
        {
            'id': 'sanlitun', 'name': '三里屯', 'city_id': 'beijing',
            'type': 'mixed', 'level': 'A',
            'longitude': 116.4551, 'latitude': 39.9364,
            'hot_value': 9500, 'avg_consumption': 280.5, 'customer_flow': 15000,
            'store_count': 450, 'rating': 4.6,
            'address': '北京市朝阳区三里屯路',
            'description': '北京最具活力的时尚购物娱乐区域',
            'facilities': ['地铁站', '停车场', '电影院', 'KTV', '健身房'],
            'tags': ['时尚', '夜生活', '国际化', '年轻人']
        },
        {
            'id': 'wangfujing', 'name': '王府井', 'city_id': 'beijing',
            'type': 'shopping', 'level': 'A',
            'longitude': 116.4074, 'latitude': 39.9170,
            'hot_value': 8800, 'avg_consumption': 320.0, 'customer_flow': 18000,
            'store_count': 380, 'rating': 4.5,
            'address': '北京市东城区王府井大街',
            'description': '北京著名的商业步行街',
            'facilities': ['地铁站', '停车场', '商场', '餐厅'],
            'tags': ['传统', '购物', '步行街', '历史']
        },
        {
            'id': 'xidan', 'name': '西单', 'city_id': 'beijing',
            'type': 'shopping', 'level': 'A',
            'longitude': 116.3770, 'latitude': 39.9065,
            'hot_value': 8200, 'avg_consumption': 250.8, 'customer_flow': 14500,
            'store_count': 320, 'rating': 4.4,
            'address': '北京市西城区西单北大街',
            'description': '年轻人喜爱的购物天堂',
            'facilities': ['地铁站', '商场', '电影院', '美食城'],
            'tags': ['年轻', '时尚', '购物', '美食']
        },
        # 上海商圈
        {
            'id': 'nanjinglu', 'name': '南京路', 'city_id': 'shanghai',
            'type': 'shopping', 'level': 'A',
            'longitude': 121.4737, 'latitude': 31.2304,
            'hot_value': 9200, 'avg_consumption': 350.0, 'customer_flow': 20000,
            'store_count': 500, 'rating': 4.7,
            'address': '上海市黄浦区南京东路',
            'description': '中华商业第一街',
            'facilities': ['地铁站', '步行街', '百货公司', '老字号'],
            'tags': ['历史', '购物', '步行街', '老字号']
        },
        {
            'id': 'xintiandi', 'name': '新天地', 'city_id': 'shanghai',
            'type': 'mixed', 'level': 'A',
            'longitude': 121.4690, 'latitude': 31.2197,
            'hot_value': 8900, 'avg_consumption': 420.0, 'customer_flow': 12000,
            'store_count': 280, 'rating': 4.8,
            'address': '上海市黄浦区新天地',
            'description': '融合历史文化与现代时尚的休闲娱乐区',
            'facilities': ['酒吧街', '精品店', '餐厅', '咖啡厅'],
            'tags': ['文化', '休闲', '小资', '夜生活']
        }
    ]
    
    for area_data in business_areas_data:
        existing_area = BusinessArea.query.get(area_data['id'])
        if not existing_area:
            area = BusinessArea(**area_data)
            db.session.add(area)
    
    db.session.commit()
    print(f"✅ 已初始化 {len(business_areas_data)} 个商圈数据")

def init_stores():
    """初始化店铺数据"""
    stores_data = [
        # 三里屯店铺
        {
            'id': 'sanlitun_restaurant_001', 'name': '海底捞火锅(三里屯店)',
            'business_area_id': 'sanlitun', 'category': 'restaurant', 'sub_category': '火锅',
            'longitude': 116.4555, 'latitude': 39.9360,
            'rating': 4.6, 'review_count': 2580, 'avg_price': 128.0,
            'phone': '010-64161234', 'address': '朝阳区三里屯路19号三里屯太古里',
            'opening_hours': '11:00-02:00', 'description': '知名连锁火锅品牌',
            'tags': ['火锅', '服务好', '排队', '24小时'],
            'is_recommended': True
        },
        {
            'id': 'sanlitun_retail_001', 'name': 'Apple Store(三里屯店)',
            'business_area_id': 'sanlitun', 'category': 'retail', 'sub_category': '数码',
            'longitude': 116.4548, 'latitude': 39.9368,
            'rating': 4.8, 'review_count': 1850, 'avg_price': 5000.0,
            'phone': '010-64162000', 'address': '朝阳区三里屯路11号三里屯太古里',
            'opening_hours': '10:00-22:00', 'description': '苹果官方零售店',
            'tags': ['苹果', '数码', '体验', '高端'],
            'is_recommended': True
        },
        # 王府井店铺
        {
            'id': 'wangfujing_restaurant_001', 'name': '全聚德烤鸭店(王府井店)',
            'business_area_id': 'wangfujing', 'category': 'restaurant', 'sub_category': '中餐',
            'longitude': 116.4080, 'latitude': 39.9175,
            'rating': 4.3, 'review_count': 3200, 'avg_price': 180.0,
            'phone': '010-65112418', 'address': '东城区王府井大街9号',
            'opening_hours': '11:00-21:30', 'description': '百年老字号烤鸭店',
            'tags': ['烤鸭', '老字号', '传统', '游客'],
            'is_recommended': True
        }
    ]
    
    for store_data in stores_data:
        existing_store = Store.query.get(store_data['id'])
        if not existing_store:
            store = Store(**store_data)
            db.session.add(store)
    
    db.session.commit()
    print(f"✅ 已初始化 {len(stores_data)} 个店铺数据")

def init_users():
    """初始化用户数据"""
    users_data = [
        {
            'username': 'admin',
            'email': 'admin@business-district.com',
            'password': 'admin123',
            'nickname': '系统管理员',
            'is_active': True,
            'vip_level': 5
        },
        {
            'username': 'demo',
            'email': 'demo@business-district.com',
            'password': 'demo123',
            'nickname': '演示用户',
            'is_active': True,
            'city': '北京'
        }
    ]
    
    for user_data in users_data:
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if not existing_user:
            password = user_data.pop('password')
            user = User(**user_data)
            user.password_hash = hash_password(password)
            db.session.add(user)
    
    db.session.commit()
    print(f"✅ 已初始化 {len(users_data)} 个用户数据")

def main():
    """主函数"""
    app = create_app()
    
    with app.app_context():
        print("🚀 开始初始化数据库数据...")
        
        # 创建所有表
        db.create_all()
        print("✅ 数据库表创建完成")
        
        # 初始化数据
        init_cities()
        init_business_areas()
        init_stores()
        init_users()
        
        print("🎉 数据初始化完成！")
        print("\n📊 数据统计:")
        print(f"   城市数量: {City.query.count()}")
        print(f"   商圈数量: {BusinessArea.query.count()}")
        print(f"   店铺数量: {Store.query.count()}")
        print(f"   用户数量: {User.query.count()}")
        
        print("\n👤 测试账号:")
        print("   管理员: admin / admin123")
        print("   演示用户: demo / demo123")

if __name__ == '__main__':
    main()
