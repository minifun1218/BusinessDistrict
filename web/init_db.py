#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
使用Flask-Migrate进行数据库迁移
"""

import os
import sys
from flask_migrate import init, migrate, upgrade
from app import create_app
from app.extensions import db

def init_database():
    """初始化数据库"""
    app = create_app()
    
    with app.app_context():
        print("🚀 开始初始化数据库...")
        
        # 检查是否已经初始化过migrations目录
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        
        if not os.path.exists(migrations_dir):
            print("📁 初始化Flask-Migrate...")
            try:
                init()
                print("✅ Flask-Migrate初始化成功")
            except Exception as e:
                print(f"❌ Flask-Migrate初始化失败: {e}")
                return False
        else:
            print("📁 Flask-Migrate已初始化，跳过...")
        
        # 生成迁移脚本
        print("📝 生成数据库迁移脚本...")
        try:
            migrate(message='Initial migration - 创建所有表')
            print("✅ 迁移脚本生成成功")
        except Exception as e:
            print(f"❌ 迁移脚本生成失败: {e}")
            # 如果迁移脚本生成失败，可能是没有变化，继续执行
        
        # 执行迁移
        print("🔄 执行数据库迁移...")
        try:
            upgrade()
            print("✅ 数据库迁移执行成功")
        except Exception as e:
            print(f"❌ 数据库迁移执行失败: {e}")
            return False
        
        # 插入初始数据
        print("📊 插入初始数据...")
        try:
            insert_initial_data()
            print("✅ 初始数据插入成功")
        except Exception as e:
            print(f"❌ 初始数据插入失败: {e}")
            return False
        
        print("🎉 数据库初始化完成！")
        return True

def insert_initial_data():
    """插入初始数据"""
    from app.models import City, SystemConfig
    
    # 检查是否已有数据
    if City.query.first():
        print("📊 数据库中已有数据，跳过初始数据插入")
        return
    
    # 插入城市数据
    cities_data = [
        {
            'id': 'beijing',
            'name': '北京',
            'code': '110000',
            'level': 'city',
            'longitude': 116.4074,
            'latitude': 39.9042,
            'pinyin': 'beijing',
            'pinyin_abbr': 'bj',
            'is_hot': True
        },
        {
            'id': 'shanghai',
            'name': '上海',
            'code': '310000',
            'level': 'city',
            'longitude': 121.4737,
            'latitude': 31.2304,
            'pinyin': 'shanghai',
            'pinyin_abbr': 'sh',
            'is_hot': True
        },
        {
            'id': 'guangzhou',
            'name': '广州',
            'code': '440100',
            'level': 'city',
            'longitude': 113.2644,
            'latitude': 23.1291,
            'pinyin': 'guangzhou',
            'pinyin_abbr': 'gz',
            'is_hot': True
        },
        {
            'id': 'shenzhen',
            'name': '深圳',
            'code': '440300',
            'level': 'city',
            'longitude': 114.0579,
            'latitude': 22.5431,
            'pinyin': 'shenzhen',
            'pinyin_abbr': 'sz',
            'is_hot': True
        },
        {
            'id': 'hangzhou',
            'name': '杭州',
            'code': '330100',
            'level': 'city',
            'longitude': 120.1614,
            'latitude': 30.2936,
            'pinyin': 'hangzhou',
            'pinyin_abbr': 'hz',
            'is_hot': True
        },
        {
            'id': 'nanjing',
            'name': '南京',
            'code': '320100',
            'level': 'city',
            'longitude': 118.7969,
            'latitude': 32.0603,
            'pinyin': 'nanjing',
            'pinyin_abbr': 'nj',
            'is_hot': True
        },
        {
            'id': 'wuhan',
            'name': '武汉',
            'code': '420100',
            'level': 'city',
            'longitude': 114.2734,
            'latitude': 30.5801,
            'pinyin': 'wuhan',
            'pinyin_abbr': 'wh',
            'is_hot': True
        },
        {
            'id': 'chengdu',
            'name': '成都',
            'code': '510100',
            'level': 'city',
            'longitude': 104.0668,
            'latitude': 30.5728,
            'pinyin': 'chengdu',
            'pinyin_abbr': 'cd',
            'is_hot': True
        }
    ]
    
    for city_data in cities_data:
        city = City(**city_data)
        db.session.add(city)
    
    # 插入系统配置
    system_configs = [
        {
            'config_key': 'crawl_delay_min',
            'config_value': '2',
            'config_type': 'integer',
            'description': '爬虫最小延迟时间（秒）',
            'is_public': False
        },
        {
            'config_key': 'crawl_delay_max',
            'config_value': '5',
            'config_type': 'integer',
            'description': '爬虫最大延迟时间（秒）',
            'is_public': False
        },
        {
            'config_key': 'cache_expire_days',
            'config_value': '2',
            'config_type': 'integer',
            'description': '数据缓存过期天数',
            'is_public': False
        },
        {
            'config_key': 'max_search_results',
            'config_value': '50',
            'config_type': 'integer',
            'description': '最大搜索结果数',
            'is_public': True
        },
        {
            'config_key': 'default_search_radius',
            'config_value': '1000',
            'config_type': 'integer',
            'description': '默认搜索半径（米）',
            'is_public': True
        },
        {
            'config_key': 'site_name',
            'config_value': '城市商圈消费热度分析系统',
            'config_type': 'string',
            'description': '网站名称',
            'is_public': True
        },
        {
            'config_key': 'enable_user_registration',
            'config_value': 'true',
            'config_type': 'boolean',
            'description': '是否允许用户注册',
            'is_public': True
        }
    ]
    
    for config_data in system_configs:
        config = SystemConfig(**config_data)
        db.session.add(config)
    
    # 提交事务
    db.session.commit()
    print(f"✅ 插入了 {len(cities_data)} 个城市和 {len(system_configs)} 个系统配置")

def reset_database():
    """重置数据库（谨慎使用）"""
    app = create_app()
    
    with app.app_context():
        print("⚠️  警告：即将重置数据库，所有数据将被删除！")
        confirm = input("请输入 'YES' 确认重置: ")
        
        if confirm != 'YES':
            print("❌ 操作已取消")
            return False
        
        print("🗑️  删除所有表...")
        db.drop_all()
        
        print("📁 删除migrations目录...")
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        if os.path.exists(migrations_dir):
            import shutil
            shutil.rmtree(migrations_dir)
        
        print("🔄 重新初始化数据库...")
        return init_database()

def check_database():
    """检查数据库状态"""
    app = create_app()
    
    with app.app_context():
        from app.models import City, BusinessArea, Store, User, SystemConfig
        
        print("📊 数据库状态检查:")
        print(f"  城市数量: {City.query.count()}")
        print(f"  商圈数量: {BusinessArea.query.count()}")
        print(f"  店铺数量: {Store.query.count()}")
        print(f"  用户数量: {User.query.count()}")
        print(f"  系统配置数量: {SystemConfig.query.count()}")
        
        # 检查表是否存在
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"  数据库表数量: {len(tables)}")
        print(f"  表列表: {', '.join(tables)}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'reset':
            reset_database()
        elif command == 'check':
            check_database()
        else:
            print("用法:")
            print("  python init_db.py          # 初始化数据库")
            print("  python init_db.py reset    # 重置数据库")
            print("  python init_db.py check    # 检查数据库状态")
    else:
        init_database()
