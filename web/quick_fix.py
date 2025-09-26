#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速修复数据库问题
"""

from app import create_app
from app.extensions import db

def quick_fix():
    """快速修复数据库问题"""
    app = create_app()
    
    with app.app_context():
        try:
            # 方法1：添加缺失的列
            print("🔧 添加缺失的review_count列...")
            db.engine.execute(
                "ALTER TABLE business_areas ADD COLUMN review_count INTEGER DEFAULT 0"
            )
            print("✅ review_count列添加成功")
            
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("✅ review_count列已存在")
            else:
                print(f"❌ 添加列失败: {e}")
                
                # 方法2：如果添加列失败，尝试重建表结构
                print("🔄 尝试重建表结构...")
                try:
                    # 创建所有表（如果不存在）
                    db.create_all()
                    print("✅ 表结构创建/更新成功")
                except Exception as e2:
                    print(f"❌ 重建表结构失败: {e2}")
                    return False
        
        print("🎉 数据库快速修复完成！")
        return True

if __name__ == '__main__':
    quick_fix()
