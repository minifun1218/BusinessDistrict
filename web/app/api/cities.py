#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
城市相关API接口
"""

from flask import Blueprint, request
from sqlalchemy import or_
from app.extensions import db
from app.models.city import City
from app.utils.response import success_response, error_response, paginated_response

# 创建城市蓝图
cities_bp = Blueprint('cities', __name__)

@cities_bp.route('', methods=['GET', 'OPTIONS'])
def get_cities():
    """获取城市列表"""
    try:
        # 获取查询参数
        level = request.args.get('level', 'city')  # 默认获取城市级别
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('pageSize', 20))
        keyword = request.args.get('keyword', '').strip()
        
        # 构建查询
        query = City.query.filter_by(level=level)
        
        # 关键词搜索
        if keyword:
            query = query.filter(
                or_(
                    City.name.contains(keyword),
                    City.pinyin.contains(keyword.lower()),
                    City.pinyin_abbr.contains(keyword.upper())
                )
            )
        
        # 分页查询
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        cities = [city.to_dict() for city in pagination.items]
        
        return paginated_response(
            items=cities,
            total=pagination.total,
            page=page,
            per_page=per_page,
            message='获取城市列表成功'
        )
        
    except Exception as e:
        return error_response(f'获取城市列表失败: {str(e)}', 500)

@cities_bp.route('/hot', methods=['GET', 'OPTIONS'])
def get_hot_cities():
    """获取热门城市"""
    try:
        cities = City.query.filter_by(is_hot=True, level='city').order_by(City.name).all()
        
        return success_response(
            [city.to_dict() for city in cities],
            '获取热门城市成功'
        )
        
    except Exception as e:
        return error_response(f'获取热门城市失败: {str(e)}', 500)

@cities_bp.route('/<city_id>', methods=['GET', 'OPTIONS'])
def get_city_by_id(city_id):
    """根据ID获取城市信息"""
    try:
        city = City.query.get(city_id)
        
        if not city:
            return error_response('城市不存在', 404)
        
        return success_response(city.to_dict(), '获取城市信息成功')
        
    except Exception as e:
        return error_response(f'获取城市信息失败: {str(e)}', 500)

@cities_bp.route('/search', methods=['GET', 'OPTIONS'])
def search_cities():
    """搜索城市"""
    try:
        keyword = request.args.get('keyword', '').strip()
        
        if not keyword:
            return error_response('搜索关键词不能为空', 400)
        
        # 搜索城市（支持名称、拼音搜索）
        cities = City.query.filter(
            City.level == 'city',
            or_(
                City.name.contains(keyword),
                City.pinyin.contains(keyword.lower()),
                City.pinyin_abbr.contains(keyword.upper())
            )
        ).limit(20).all()
        
        return success_response(
            [city.to_dict() for city in cities],
            '搜索城市成功'
        )
        
    except Exception as e:
        return error_response(f'搜索城市失败: {str(e)}', 500)

@cities_bp.route('/location', methods=['GET', 'OPTIONS'])
def get_city_by_location():
    """根据坐标获取城市信息"""
    try:
        longitude = float(request.args.get('longitude', 0))
        latitude = float(request.args.get('latitude', 0))
        
        if not longitude or not latitude:
            return error_response('经纬度坐标不能为空', 400)
        
        # 这里简化处理，实际应用中需要使用地理空间查询
        # 找到距离最近的城市（简单的距离计算）
        cities = City.query.filter_by(level='city').all()
        
        if not cities:
            return error_response('未找到相关城市', 404)
        
        # 计算距离并找到最近的城市
        min_distance = float('inf')
        nearest_city = None
        
        for city in cities:
            # 简单的欧几里得距离计算
            distance = ((city.longitude - longitude) ** 2 + (city.latitude - latitude) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                nearest_city = city
        
        if nearest_city:
            return success_response(nearest_city.to_dict(), '获取定位城市成功')
        else:
            return error_response('未找到附近的城市', 404)
        
    except ValueError:
        return error_response('坐标格式不正确', 400)
    except Exception as e:
        return error_response(f'获取定位城市失败: {str(e)}', 500)

@cities_bp.route('/provinces', methods=['GET', 'OPTIONS'])
def get_provinces():
    """获取省份列表"""
    try:
        provinces = City.query.filter_by(level='province').order_by(City.name).all()
        
        return success_response(
            [province.to_dict() for province in provinces],
            '获取省份列表成功'
        )
        
    except Exception as e:
        return error_response(f'获取省份列表失败: {str(e)}', 500)

@cities_bp.route('/province/<province_id>', methods=['GET', 'OPTIONS'])
def get_cities_by_province(province_id):
    """根据省份ID获取城市列表"""
    try:
        cities = City.query.filter_by(parent_id=province_id, level='city').order_by(City.name).all()
        
        return success_response(
            [city.to_dict() for city in cities],
            '获取省份城市列表成功'
        )
        
    except Exception as e:
        return error_response(f'获取省份城市列表失败: {str(e)}', 500)

@cities_bp.route('/<city_id>/districts', methods=['GET', 'OPTIONS'])
def get_districts_by_city(city_id):
    """根据城市ID获取区县列表"""
    try:
        districts = City.query.filter_by(parent_id=city_id, level='district').order_by(City.name).all()
        
        return success_response(
            [district.to_dict() for district in districts],
            '获取城市区县列表成功'
        )
        
    except Exception as e:
        return error_response(f'获取城市区县列表失败: {str(e)}', 500)

@cities_bp.route('/<city_id>/stats', methods=['GET', 'OPTIONS'])
def get_city_stats(city_id):
    """获取城市统计信息"""
    try:
        city = City.query.get(city_id)
        
        if not city:
            return error_response('城市不存在', 404)
        
        # 统计商圈数量
        business_area_count = city.business_areas.count()
        
        # 这里可以添加更多统计信息
        stats = {
            'city': city.to_dict(),
            'business_area_count': business_area_count,
            'total_stores': sum(area.store_count for area in city.business_areas),
            'avg_rating': round(sum(area.rating for area in city.business_areas if area.rating > 0) / 
                              max(len([area for area in city.business_areas if area.rating > 0]), 1), 2),
            'total_hot_value': sum(area.hot_value for area in city.business_areas)
        }
        
        return success_response(stats, '获取城市统计信息成功')
        
    except Exception as e:
        return error_response(f'获取城市统计信息失败: {str(e)}', 500)

@cities_bp.route('/<city_id>/business-areas', methods=['GET', 'OPTIONS'])
def get_city_business_areas(city_id):
    """获取城市商圈概览"""
    try:
        city = City.query.get(city_id)
        
        if not city:
            return error_response('城市不存在', 404)
        
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('pageSize', 20))
        area_type = request.args.get('type', '')
        
        # 构建查询
        query = city.business_areas
        
        if area_type:
            query = query.filter_by(type=area_type)
        
        # 按热度值排序
        query = query.order_by(db.desc('hot_value'))
        
        # 分页
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        business_areas = [area.to_dict() for area in pagination.items]
        
        return paginated_response(
            items=business_areas,
            total=pagination.total,
            page=page,
            per_page=per_page,
            message='获取城市商圈概览成功'
        )
        
    except Exception as e:
        return error_response(f'获取城市商圈概览失败: {str(e)}', 500)