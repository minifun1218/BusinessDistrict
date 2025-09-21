#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据分析相关API接口
"""

import random
from datetime import datetime, timedelta
from flask import Blueprint, request
from sqlalchemy import func, desc
from app.extensions import db
from app.models.city import City
from app.models.business_area import BusinessArea, Store
from app.utils.response import success_response, error_response

# 创建数据分析蓝图
analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/city/<city_id>', methods=['GET'])
def get_city_analytics(city_id):
    """获取城市整体分析数据"""
    try:
        city = City.query.get(city_id)
        if not city:
            return error_response('城市不存在', 404)
        
        # 获取城市商圈统计
        business_areas = city.business_areas.all()
        total_stores = sum(area.store_count for area in business_areas)
        avg_rating = sum(area.rating for area in business_areas if area.rating > 0) / max(len([area for area in business_areas if area.rating > 0]), 1)
        total_hot_value = sum(area.hot_value for area in business_areas)
        
        analytics_data = {
            'city_info': city.to_dict(),
            'overview': {
                'total_business_areas': len(business_areas),
                'total_stores': total_stores,
                'avg_rating': round(avg_rating, 2),
                'total_hot_value': total_hot_value,
                'active_areas': len([area for area in business_areas if area.hot_value > 5000])
            },
            'area_distribution': {
                'by_type': dict(
                    db.session.query(BusinessArea.type, func.count(BusinessArea.id))
                    .filter_by(city_id=city_id)
                    .group_by(BusinessArea.type)
                    .all()
                ),
                'by_level': dict(
                    db.session.query(BusinessArea.level, func.count(BusinessArea.id))
                    .filter_by(city_id=city_id)
                    .group_by(BusinessArea.level)
                    .all()
                )
            }
        }
        
        return success_response(analytics_data, '获取城市分析数据成功')
        
    except Exception as e:
        return error_response(f'获取城市分析数据失败: {str(e)}', 500)

@analytics_bp.route('/hot-ranking', methods=['GET'])
def get_hot_ranking_data():
    """获取热度排行数据"""
    try:
        city_id = request.args.get('cityId', '')
        limit = int(request.args.get('limit', 10))
        
        query = BusinessArea.query
        if city_id:
            query = query.filter_by(city_id=city_id)
        
        areas = query.order_by(desc(BusinessArea.hot_value)).limit(limit).all()
        
        ranking_data = []
        for i, area in enumerate(areas):
            # 模拟增长率数据
            growth_rate = round(random.uniform(-5, 25), 1)
            ranking_data.append({
                'name': area.name,
                'hotValue': area.hot_value,
                'value': area.hot_value,
                'growthRate': growth_rate,
                'rank': i + 1
            })
        
        return success_response(ranking_data, '获取热度排行数据成功')
        
    except Exception as e:
        return error_response(f'获取热度排行数据失败: {str(e)}', 500)

@analytics_bp.route('/hourly-flow', methods=['GET'])
def get_hourly_flow_data():
    """获取24小时客流数据"""
    try:
        city_id = request.args.get('cityId', '')
        date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # 生成24小时客流模拟数据
        hours = [f"{i:02d}:00" for i in range(24)]
        
        # 工作日客流模式
        weekday_flow = [
            120, 80, 60, 45, 35, 50, 180, 320, 280, 350, 420, 580,
            750, 680, 520, 480, 620, 890, 1200, 980, 750, 520, 380, 220
        ]
        
        # 周末客流模式
        weekend_flow = [
            200, 120, 80, 60, 45, 60, 150, 280, 380, 520, 680, 850,
            1100, 1350, 1200, 980, 850, 1180, 1450, 1280, 950, 680, 450, 320
        ]
        
        # 根据城市调整数据
        if city_id:
            city = City.query.get(city_id)
            if city:
                # 根据城市规模调整客流量
                multiplier = 1.0
                if city.population:
                    if city.population > 10000000:  # 超大城市
                        multiplier = 1.5
                    elif city.population > 5000000:  # 大城市
                        multiplier = 1.2
                    elif city.population < 1000000:  # 小城市
                        multiplier = 0.8
                
                weekday_flow = [int(x * multiplier) for x in weekday_flow]
                weekend_flow = [int(x * multiplier) for x in weekend_flow]
        
        flow_data = {
            'hours': hours,
            'weekday': weekday_flow,
            'weekend': weekend_flow,
            'date': date
        }
        
        return success_response(flow_data, '获取24小时客流数据成功')
        
    except Exception as e:
        return error_response(f'获取24小时客流数据失败: {str(e)}', 500)

@analytics_bp.route('/category-distribution', methods=['GET'])
def get_category_distribution():
    """获取消费类型分布数据"""
    try:
        city_id = request.args.get('cityId', '')
        
        # 构建查询
        if city_id:
            # 通过商圈关联查询该城市的店铺分类分布
            category_data = db.session.query(
                Store.category,
                func.count(Store.id).label('count'),
                func.sum(Store.avg_price * Store.review_count).label('total_value')
            ).join(BusinessArea).filter(
                BusinessArea.city_id == city_id
            ).group_by(Store.category).all()
        else:
            # 全局统计
            category_data = db.session.query(
                Store.category,
                func.count(Store.id).label('count'),
                func.sum(Store.avg_price * Store.review_count).label('total_value')
            ).group_by(Store.category).all()
        
        # 定义分类映射和颜色
        category_mapping = {
            'restaurant': {'name': '餐饮美食', 'color': '#ff6b6b'},
            'retail': {'name': '购物零售', 'color': '#4ecdc4'},
            'entertainment': {'name': '休闲娱乐', 'color': '#45b7d1'},
            'service': {'name': '生活服务', 'color': '#96ceb4'}
        }
        
        distribution_data = []
        for category, count, total_value in category_data:
            mapping = category_mapping.get(category, {'name': category, 'color': '#dda0dd'})
            distribution_data.append({
                'name': mapping['name'],
                'value': int(total_value or 0),
                'count': count,
                'color': mapping['color']
            })
        
        # 如果没有数据，返回模拟数据
        if not distribution_data:
            distribution_data = [
                {'name': '餐饮美食', 'value': 3500, 'count': 1250, 'color': '#ff6b6b'},
                {'name': '购物零售', 'value': 2800, 'count': 890, 'color': '#4ecdc4'},
                {'name': '休闲娱乐', 'value': 1900, 'count': 650, 'color': '#45b7d1'},
                {'name': '生活服务', 'value': 1200, 'count': 420, 'color': '#96ceb4'},
                {'name': '酒店住宿', 'value': 800, 'count': 180, 'color': '#ffeaa7'},
                {'name': '其他', 'value': 600, 'count': 150, 'color': '#dda0dd'}
            ]
        
        return success_response(distribution_data, '获取消费类型分布数据成功')
        
    except Exception as e:
        return error_response(f'获取消费类型分布数据失败: {str(e)}', 500)

@analytics_bp.route('/sentiment-analysis', methods=['GET'])
def get_sentiment_analysis():
    """获取情感分析数据"""
    try:
        city_id = request.args.get('cityId', '')
        
        # 基于评分计算情感分析（模拟）
        if city_id:
            stores = db.session.query(Store).join(BusinessArea).filter(
                BusinessArea.city_id == city_id
            ).all()
        else:
            stores = Store.query.all()
        
        if stores:
            total_stores = len(stores)
            high_rating = len([s for s in stores if s.rating >= 4.0])
            medium_rating = len([s for s in stores if 3.0 <= s.rating < 4.0])
            low_rating = len([s for s in stores if s.rating < 3.0])
            
            sentiment_data = {
                'positive': round(high_rating / total_stores * 100, 1),
                'neutral': round(medium_rating / total_stores * 100, 1),
                'negative': round(low_rating / total_stores * 100, 1)
            }
        else:
            # 默认数据
            sentiment_data = {
                'positive': 68.5,
                'neutral': 22.3,
                'negative': 9.2
            }
        
        return success_response(sentiment_data, '获取情感分析数据成功')
        
    except Exception as e:
        return error_response(f'获取情感分析数据失败: {str(e)}', 500)

@analytics_bp.route('/consumption-trend', methods=['GET'])
def get_consumption_trend():
    """获取消费趋势数据"""
    try:
        city_id = request.args.get('cityId', '')
        days = int(request.args.get('days', 30))
        
        # 生成最近N天的日期
        end_date = datetime.now()
        dates = []
        sales_data = []
        customer_data = []
        
        for i in range(days):
            date = end_date - timedelta(days=days-1-i)
            dates.append(date.strftime('%m-%d'))
            
            # 模拟销售额和客流量数据
            base_sales = random.randint(12000, 18000)
            base_customers = random.randint(2500, 4000)
            
            # 周末数据通常更高
            if date.weekday() >= 5:  # 周末
                base_sales = int(base_sales * 1.3)
                base_customers = int(base_customers * 1.4)
            
            sales_data.append(base_sales)
            customer_data.append(base_customers)
        
        trend_data = {
            'dates': dates,
            'sales': sales_data,
            'customers': customer_data
        }
        
        return success_response(trend_data, '获取消费趋势数据成功')
        
    except Exception as e:
        return error_response(f'获取消费趋势数据失败: {str(e)}', 500)

@analytics_bp.route('/radar-comparison', methods=['POST'])
def get_radar_comparison_data():
    """获取雷达图对比数据"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 400)
        
        area_ids = data.get('areaIds', [])
        
        if not area_ids:
            return error_response('商圈ID列表不能为空', 400)
        
        # 获取商圈信息
        areas = BusinessArea.query.filter(BusinessArea.id.in_(area_ids)).all()
        
        # 雷达图指标
        indicators = [
            {'name': '客流量', 'max': 100},
            {'name': '消费水平', 'max': 100},
            {'name': '用户评价', 'max': 100},
            {'name': '交通便利', 'max': 100},
            {'name': '配套设施', 'max': 100},
            {'name': '品牌丰富度', 'max': 100}
        ]
        
        radar_data = []
        for area in areas:
            # 计算各项指标得分
            values = [
                min(100, max(0, area.customer_flow / 100)),  # 客流量
                min(100, max(0, area.avg_consumption / 10)),  # 消费水平
                min(100, max(0, area.rating * 20)),  # 用户评价
                random.randint(60, 95),  # 交通便利（模拟）
                min(100, len(area.facilities or []) * 15),  # 配套设施
                min(100, max(0, area.store_count / 5))  # 品牌丰富度
            ]
            
            radar_data.append({
                'name': area.name,
                'value': values
            })
        
        comparison_data = {
            'indicators': indicators,
            'data': radar_data
        }
        
        return success_response(comparison_data, '获取雷达图对比数据成功')
        
    except Exception as e:
        return error_response(f'获取雷达图对比数据失败: {str(e)}', 500)

@analytics_bp.route('/heatmap', methods=['GET'])
def get_heatmap_data():
    """获取热力图数据"""
    try:
        city_id = request.args.get('cityId', '')
        zoom = int(request.args.get('zoom', 10))
        
        # 构建查询
        query = BusinessArea.query
        if city_id:
            query = query.filter_by(city_id=city_id)
        
        areas = query.all()
        
        heatmap_data = []
        for area in areas:
            heatmap_data.append({
                'name': area.name,
                'longitude': area.longitude,
                'latitude': area.latitude,
                'hotValue': area.hot_value,
                'value': area.hot_value,
                'type': area.type,
                'level': area.level,
                'rating': area.rating,
                'storeCount': area.store_count
            })
        
        return success_response(heatmap_data, '获取热力图数据成功')
        
    except Exception as e:
        return error_response(f'获取热力图数据失败: {str(e)}', 500)

@analytics_bp.route('/realtime/<city_id>', methods=['GET'])
def get_realtime_data(city_id):
    """获取实时数据"""
    try:
        city = City.query.get(city_id)
        if not city:
            return error_response('城市不存在', 404)
        
        # 模拟实时数据
        current_time = datetime.now()
        hour = current_time.hour
        
        # 根据时间段调整实时数据
        if 9 <= hour <= 11:  # 上午高峰
            flow_multiplier = 1.2
        elif 12 <= hour <= 14:  # 午餐高峰
            flow_multiplier = 1.5
        elif 18 <= hour <= 21:  # 晚餐高峰
            flow_multiplier = 1.8
        else:
            flow_multiplier = 0.8
        
        realtime_data = {
            'timestamp': current_time.isoformat(),
            'current_flow': int(random.randint(800, 1200) * flow_multiplier),
            'total_areas': city.business_areas.count(),
            'active_areas': random.randint(15, 25),
            'peak_area': {
                'name': '三里屯',
                'flow': int(random.randint(200, 400) * flow_multiplier)
            },
            'trend': 'up' if flow_multiplier > 1 else 'down',
            'growth_rate': round((flow_multiplier - 1) * 100, 1)
        }
        
        return success_response(realtime_data, '获取实时数据成功')
        
    except Exception as e:
        return error_response(f'获取实时数据失败: {str(e)}', 500)