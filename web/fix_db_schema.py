#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库模式修复脚本
"""

import os
import sys
from flask_migrate import migrate, upgrade, stamp
from app import create_app
from app.extensions import db

def check_column_exists(table_name, column_name):
    """检查列是否存在"""
    inspector = db.inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def fix_database_schema():
    """修复数据库模式"""
    app = create_app()
    
    with app.app_context():
        print("🔍 检查数据库模式...")
        
        # 检查business_areas表的review_count列
        if not check_column_exists('business_areas', 'review_count'):
            print("❌ business_areas表缺少review_count列")
            
            # 直接执行SQL添加列
            print("🔧 添加review_count列...")
            try:
                db.engine.execute(
                    "ALTER TABLE business_areas ADD COLUMN review_count INTEGER DEFAULT 0"
                )
                print("✅ review_count列添加成功")
            except Exception as e:
                print(f"❌ 添加review_count列失败: {e}")
                return False
        else:
            print("✅ business_areas表的review_count列已存在")
        
        # 检查其他可能缺失的列
        required_columns = {
            'business_areas': ['review_count', 'facilities', 'transportation', 'images', 'tags'],
            'stores': ['images', 'tags', 'facilities']
        }
        
        for table_name, columns in required_columns.items():
            print(f"🔍 检查{table_name}表...")
            inspector = db.inspect(db.engine)
            
            try:
                existing_columns = [col['name'] for col in inspector.get_columns(table_name)]
                print(f"  现有列: {', '.join(existing_columns)}")
                
                missing_columns = [col for col in columns if col not in existing_columns]
                if missing_columns:
                    print(f"  ❌ 缺失列: {', '.join(missing_columns)}")
                else:
                    print(f"  ✅ 所有必需列都存在")
                    
            except Exception as e:
                print(f"  ❌ 检查{table_name}表失败: {e}")
        
        # 尝试标记当前迁移状态
        print("🏷️  标记迁移状态...")
        try:
            # 获取最新的迁移版本
            from flask_migrate import current, heads
            current_rev = current()
            head_rev = heads()
            
            print(f"  当前版本: {current_rev}")
            print(f"  最新版本: {head_rev}")
            
            if current_rev != head_rev:
                print("🔄 执行数据库升级...")
                upgrade()
                print("✅ 数据库升级完成")
            else:
                print("✅ 数据库已是最新版本")
                
        except Exception as e:
            print(f"❌ 迁移状态检查失败: {e}")
            # 如果迁移失败，尝试强制标记当前状态
            try:
                print("🏷️  强制标记迁移状态...")
                stamp('head')
                print("✅ 迁移状态标记成功")
            except Exception as e2:
                print(f"❌ 强制标记也失败: {e2}")
        
        print("🎉 数据库模式修复完成！")
        return True

def reset_and_recreate():
    """重置并重新创建数据库"""
    app = create_app()
    
    with app.app_context():
        print("⚠️  警告：即将重置数据库，所有数据将被删除！")
        confirm = input("请输入 'YES' 确认重置: ")
        
        if confirm != 'YES':
            print("❌ 操作已取消")
            return False
        
        print("🗑️  删除所有表...")
        db.drop_all()
        
        print("🏗️  重新创建所有表...")
        db.create_all()
        
        print("🏷️  标记迁移状态...")
        try:
            stamp('head')
            print("✅ 迁移状态标记成功")
        except Exception as e:
            print(f"❌ 迁移状态标记失败: {e}")
        
        print("📊 插入初始数据...")
        try:
            from init_db import insert_initial_data
            insert_initial_data()
            print("✅ 初始数据插入成功")
        except Exception as e:
            print(f"❌ 初始数据插入失败: {e}")
        
        print("🎉 数据库重置完成！")
        return True

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'reset':
            reset_and_recreate()
        else:
            print("用法:")
            print("  python fix_db_schema.py       # 修复数据库模式")
            print("  python fix_db_schema.py reset # 重置数据库")
    else:
        fix_database_schema()
