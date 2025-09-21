#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫相关API接口
"""

from flask import Blueprint, request, current_app
from app.extensions import db
from app.models.city import City
from app.utils.response import success_response, error_response
from app.data_sources.data_manager import DataSourceManager
import logging

logger = logging.getLogger(__name__)

# 创建爬虫蓝图
crawler_bp = Blueprint('crawler', __name__)

def get_data_manager():
    """获取数据源管理器实例"""
    if not hasattr(current_app, '_data_manager'):
        baidu_key = current_app.config.get('BAIDU_MAP_AK')
        amap_key = current_app.config.get('AMAP_KEY')
        current_app._data_manager = DataSourceManager(baidu_key, amap_key)
    return current_app._data_manager

@crawler_bp.route('/status', methods=['GET'])
def get_data_source_status():
    """获取数据源状态"""
    try:
        data_manager = get_data_manager()
        stats = data_manager.get_stats()
        
        return success_response(stats, '获取数据源状态成功')
        
    except Exception as e:
        logger.error(f"获取数据源状态失败: {str(e)}")
        return error_response(f'获取数据源状态失败: {str(e)}', 500)

@crawler_bp.route('/test', methods=['GET'])
def test_data_sources():
    """测试数据源连通性"""
    try:
        data_manager = get_data_manager()
        results = data_manager.test_connections()
        
        return success_response(results, '数据源测试完成')
        
    except Exception as e:
        logger.error(f"测试数据源失败: {str(e)}")
        return error_response(f'测试数据源失败: {str(e)}', 500)

@crawler_bp.route('/crawl-city', methods=['POST'])
def crawl_city_data():
    """爬取指定城市的数据"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 400)
        
        city_id = data.get('cityId')
        city_name = data.get('cityName')
        crawlers = data.get('crawlers')  # 可选，指定使用的爬虫
        update_existing = data.get('updateExisting', False)
        
        if not city_id or not city_name:
            return error_response('城市ID和名称不能为空', 400)
        
        # 验证城市是否存在
        city = City.query.get(city_id)
        if not city:
            return error_response('指定的城市不存在', 404)
        
        data_manager = get_data_manager()
        result = data_manager.fetch_city_data(
            city_id=city_id,
            city_name=city_name,
            data_sources=crawlers,
            update_existing=update_existing
        )
        
        if result['success']:
            return success_response(result, '数据爬取成功')
        else:
            return error_response(f"数据爬取失败: {result.get('error', '未知错误')}", 500)
        
    except Exception as e:
        logger.error(f"爬取城市数据失败: {str(e)}")
        return error_response(f'爬取城市数据失败: {str(e)}', 500)

@crawler_bp.route('/batch-crawl', methods=['POST'])
def batch_crawl_cities():
    """批量爬取多个城市的数据"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 400)
        
        city_ids = data.get('cityIds', [])
        crawlers = data.get('crawlers')
        update_existing = data.get('updateExisting', False)
        
        if not city_ids:
            return error_response('城市ID列表不能为空', 400)
        
        # 验证城市是否存在
        cities = City.query.filter(City.id.in_(city_ids)).all()
        if len(cities) != len(city_ids):
            return error_response('部分城市不存在', 404)
        
        crawler_manager = get_crawler_manager()
        results = []
        
        for city in cities:
            logger.info(f"开始爬取城市: {city.name}")
            result = crawler_manager.crawl_city_data(
                city_id=city.id,
                city_name=city.name,
                crawlers=crawlers,
                update_existing=update_existing
            )
            results.append(result)
        
        # 统计结果
        success_count = sum(1 for r in results if r['success'])
        total_areas = sum(r.get('areas_count', 0) for r in results if r['success'])
        total_stores = sum(r.get('stores_count', 0) for r in results if r['success'])
        
        summary = {
            'total_cities': len(city_ids),
            'success_count': success_count,
            'failed_count': len(city_ids) - success_count,
            'total_areas_crawled': total_areas,
            'total_stores_crawled': total_stores,
            'results': results
        }
        
        return success_response(summary, f'批量爬取完成，成功 {success_count}/{len(city_ids)} 个城市')
        
    except Exception as e:
        logger.error(f"批量爬取城市数据失败: {str(e)}")
        return error_response(f'批量爬取城市数据失败: {str(e)}', 500)

@crawler_bp.route('/crawl-area-stores', methods=['POST'])
def crawl_area_stores():
    """爬取指定商圈的店铺数据"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 400)
        
        area_id = data.get('areaId')
        crawlers = data.get('crawlers')
        update_existing = data.get('updateExisting', False)
        
        if not area_id:
            return error_response('商圈ID不能为空', 400)
        
        # 验证商圈是否存在
        from app.models.business_area import BusinessArea
        area = BusinessArea.query.get(area_id)
        if not area:
            return error_response('指定的商圈不存在', 404)
        
        crawler_manager = get_crawler_manager()
        
        # 使用私有方法爬取店铺数据
        stores_count = crawler_manager._crawl_area_stores(
            area_id=area.id,
            area_name=area.name,
            area_lat=area.latitude,
            area_lng=area.longitude,
            crawler_names=crawlers or list(crawler_manager.crawlers.keys()),
            update_existing=update_existing
        )
        
        result = {
            'area_id': area_id,
            'area_name': area.name,
            'stores_count': stores_count
        }
        
        return success_response(result, f'成功爬取商圈 {area.name} 的 {stores_count} 个店铺')
        
    except Exception as e:
        logger.error(f"爬取商圈店铺数据失败: {str(e)}")
        return error_response(f'爬取商圈店铺数据失败: {str(e)}', 500)

@crawler_bp.route('/schedule-task', methods=['POST'])
def schedule_crawl_task():
    """调度爬虫任务"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 400)
        
        task_type = data.get('taskType')  # 'city' 或 'area'
        target_ids = data.get('targetIds', [])
        schedule_time = data.get('scheduleTime')  # ISO格式时间字符串
        crawlers = data.get('crawlers')
        update_existing = data.get('updateExisting', False)
        
        if not task_type or not target_ids:
            return error_response('任务类型和目标ID不能为空', 400)
        
        # 这里可以集成Celery或APScheduler来实现定时任务
        # 暂时返回成功响应，表示任务已调度
        
        task_info = {
            'task_id': f"crawl_task_{len(target_ids)}_{task_type}",
            'task_type': task_type,
            'target_count': len(target_ids),
            'schedule_time': schedule_time,
            'status': 'scheduled'
        }
        
        return success_response(task_info, '爬虫任务调度成功')
        
    except Exception as e:
        logger.error(f"调度爬虫任务失败: {str(e)}")
        return error_response(f'调度爬虫任务失败: {str(e)}', 500)

@crawler_bp.route('/data-quality', methods=['GET'])
def check_data_quality():
    """检查数据质量"""
    try:
        from app.models.business_area import BusinessArea, Store
        from sqlalchemy import func
        
        # 统计数据质量指标
        total_areas = BusinessArea.query.count()
        areas_with_coords = BusinessArea.query.filter(
            BusinessArea.longitude.isnot(None),
            BusinessArea.latitude.isnot(None)
        ).count()
        
        total_stores = Store.query.count()
        stores_with_rating = Store.query.filter(Store.rating > 0).count()
        stores_with_phone = Store.query.filter(Store.phone.isnot(None)).count()
        
        # 按城市统计
        city_stats = db.session.query(
            City.name,
            func.count(BusinessArea.id).label('area_count')
        ).outerjoin(BusinessArea).group_by(City.id).all()
        
        quality_report = {
            'areas': {
                'total': total_areas,
                'with_coordinates': areas_with_coords,
                'coordinate_completeness': round(areas_with_coords / total_areas * 100, 2) if total_areas > 0 else 0
            },
            'stores': {
                'total': total_stores,
                'with_rating': stores_with_rating,
                'with_phone': stores_with_phone,
                'rating_completeness': round(stores_with_rating / total_stores * 100, 2) if total_stores > 0 else 0,
                'phone_completeness': round(stores_with_phone / total_stores * 100, 2) if total_stores > 0 else 0
            },
            'city_distribution': [
                {'city_name': city_name, 'area_count': area_count}
                for city_name, area_count in city_stats
            ]
        }
        
        return success_response(quality_report, '数据质量检查完成')
        
    except Exception as e:
        logger.error(f"检查数据质量失败: {str(e)}")
        return error_response(f'检查数据质量失败: {str(e)}', 500)
