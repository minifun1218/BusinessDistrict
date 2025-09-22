#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从region.json导入所有城市数据到数据库
"""

import json
import os
import sys
import hashlib

# 尝试导入pypinyin，如果没有安装则使用简单的拼音生成
try:
    from pypinyin import lazy_pinyin, Style
    HAS_PYPINYIN = True
except ImportError:
    HAS_PYPINYIN = False
    print("警告: 未安装pypinyin库，将使用简单的拼音生成方法")

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.city import City
from app.extensions import db


def generate_pinyin(name):
    """生成拼音和拼音缩写"""
    if HAS_PYPINYIN:
        try:
            # 生成完整拼音
            pinyin_list = lazy_pinyin(name, style=Style.NORMAL)
            pinyin = ''.join(pinyin_list)
            
            # 生成拼音缩写
            pinyin_abbr_list = lazy_pinyin(name, style=Style.FIRST_LETTER)
            pinyin_abbr = ''.join(pinyin_abbr_list).upper()
            
            return pinyin, pinyin_abbr
        except:
            pass
    
    # 简单的拼音生成方法（当pypinyin不可用时）
    # 去掉常见的地名后缀
    clean_name = name.replace('市', '').replace('区', '').replace('县', '').replace('省', '')
    pinyin = clean_name.lower()
    pinyin_abbr = clean_name[:2].upper() if len(clean_name) >= 2 else clean_name.upper()
    
    return pinyin, pinyin_abbr


def generate_city_id(name, level, parent_id=None):
    """生成城市ID"""
    # 使用名称和层级生成唯一ID
    base_string = f"{name}_{level}_{parent_id or ''}"
    hash_obj = hashlib.md5(base_string.encode('utf-8'))
    return hash_obj.hexdigest()[:10]


def generate_city_code(name, level, parent_code=None, index=0):
    """生成城市代码"""
    # 根据层级和索引生成代码
    if level == 'province':
        # 省级代码：两位数字 + 0000
        return f"{(index + 1):02d}0000"
    elif level == 'city':
        # 市级代码：在省代码基础上 + 两位数字 + 00
        if parent_code:
            province_code = parent_code[:2]
            return f"{province_code}{(index + 1):02d}00"
        else:
            return f"{(index + 1):04d}00"
    else:  # district
        # 区县代码：在市代码基础上 + 两位数字
        if parent_code:
            city_code = parent_code[:4]
            return f"{city_code}{(index + 1):02d}"
        else:
            return f"{(index + 1):06d}"


def parse_districts(districts_data, parent_id=None, parent_code=None, level_map=None):
    """递归解析区域数据"""
    if level_map is None:
        level_map = {'province': 'city', 'city': 'district', 'district': 'district'}
    
    cities = []
    
    for index, district in enumerate(districts_data):
        name = district['name']
        center = district['center']
        current_level = district['level']
        
        # 映射level到数据库格式
        db_level = level_map.get(current_level, current_level)
        if db_level == 'country':
            continue  # 跳过国家级别
        
        # 生成ID和代码
        city_id = generate_city_id(name, db_level, parent_id)
        city_code = generate_city_code(name, db_level, parent_code, index)
        
        # 生成拼音
        pinyin, pinyin_abbr = generate_pinyin(name)
        
        # 判断是否为热门城市
        hot_cities = ['北京', '上海', '广州', '深圳', '杭州', '南京', '武汉', '成都', '天津', '重庆']
        is_hot = any(hot_city in name for hot_city in hot_cities)
        
        # 根据城市名称判断经济水平
        high_economic_cities = ['北京', '上海', '广州', '深圳', '杭州', '南京', '苏州', '宁波', '厦门']
        if any(city in name for city in high_economic_cities):
            economic_level = 'high'
        elif any(city in name for city in ['成都', '武汉', '西安', '青岛', '郑州', '济南']):
            economic_level = 'medium'
        else:
            economic_level = 'low'
        
        city_data = {
            'id': city_id,
            'name': name,
            'code': city_code,
            'level': db_level,
            'parent_id': parent_id,
            'longitude': center['longitude'],
            'latitude': center['latitude'],
            'population': None,  # region.json中没有人口数据
            'area': None,  # region.json中没有面积数据
            'economic_level': economic_level,
            'is_hot': is_hot,
            'pinyin': pinyin,
            'pinyin_abbr': pinyin_abbr
        }
        
        cities.append(city_data)
        
        # 递归处理子区域
        if district.get('districts'):
            sub_cities = parse_districts(
                district['districts'], 
                city_id, 
                city_code,  # 传递当前城市代码作为父代码
                level_map
            )
            cities.extend(sub_cities)
    
    return cities


def import_cities_from_json():
    """从JSON文件导入城市数据"""
    
    # 读取JSON文件
    json_file_path = os.path.join(os.path.dirname(__file__), 'region.json')
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"错误: 找不到文件 {json_file_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"错误: JSON文件格式错误 - {e}")
        return False
    
    # 检查是否已有数据
    existing_count = City.query.count()
    if existing_count > 0:
        print(f"数据库中已有 {existing_count} 条城市数据")
        response = input("是否清空现有数据并重新导入？(y/N): ")
        if response.lower() != 'y':
            print("取消导入")
            return False
        
        # 清空现有数据
        try:
            City.query.delete()
            db.session.commit()
            print("已清空现有城市数据")
        except Exception as e:
            db.session.rollback()
            print(f"清空数据失败: {str(e)}")
            return False
    
    # 解析数据
    print("开始解析城市数据...")
    
    # 获取所有省份/直辖市数据
    districts_data = data.get('districts', [])
    
    # 解析所有城市数据
    all_cities = parse_districts(districts_data)
    
    print(f"共解析出 {len(all_cities)} 个城市/区县数据")
    
    # 批量导入数据库
    try:
        batch_size = 1000
        total_imported = 0
        
        for i in range(0, len(all_cities), batch_size):
            batch = all_cities[i:i + batch_size]
            
            for city_data in batch:
                city = City(**city_data)
                db.session.add(city)
            
            db.session.commit()
            total_imported += len(batch)
            print(f"已导入 {total_imported}/{len(all_cities)} 条数据...")
        
        print(f"成功导入 {total_imported} 条城市数据！")
        
        # 打印统计信息
        province_count = City.query.filter_by(level='province').count()
        city_count = City.query.filter_by(level='city').count() 
        district_count = City.query.filter_by(level='district').count()
        
        print(f"统计信息:")
        print(f"  省份/直辖市: {province_count}")
        print(f"  城市: {city_count}")
        print(f"  区县: {district_count}")
        print(f"  总计: {province_count + city_count + district_count}")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"导入数据失败: {str(e)}")
        return False


if __name__ == '__main__':
    from app import create_app
    
    app = create_app()
    with app.app_context():
        success = import_cities_from_json()
        if success:
            print("城市数据导入完成！")
        else:
            print("城市数据导入失败！")
