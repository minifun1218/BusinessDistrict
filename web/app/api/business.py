#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商圈相关API接口
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from sqlalchemy import or_, desc, func
from app.extensions import db
from app.models.business_area import BusinessArea
from app.models.store import Store
from app.models.city import City
from app.utils.response import success_response, error_response, paginated_response
import logging

logger = logging.getLogger(__name__)

# 创建商圈蓝图
business_bp = Blueprint('business', __name__)

@business_bp.route('', methods=['GET', 'OPTIONS'])
def get_business_areas():
    """获取商圈列表"""
    try:
        # 获取查询参数
        city_id = request.args.get('cityId', '')
        area_type = request.args.get('type', '')
        level = request.args.get('level', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('pageSize', 20))
        sort_by = request.args.get('sortBy', 'hot_value')  # 排序字段
        sort_order = request.args.get('sortOrder', 'desc')  # 排序顺序
        
        # 构建查询
        query = BusinessArea.query
        
        # 城市筛选
        if city_id:
            query = query.filter_by(city_id=city_id)
        
        # 类型筛选
        if area_type:
            query = query.filter_by(type=area_type)
        
        # 级别筛选
        if level:
            query = query.filter_by(level=level)
        
        # 排序
        if sort_by == 'hot_value':
            order_column = BusinessArea.hot_value
        elif sort_by == 'rating':
            order_column = BusinessArea.rating
        elif sort_by == 'customer_flow':
            order_column = BusinessArea.customer_flow
        else:
            order_column = BusinessArea.hot_value
        
        if sort_order == 'desc':
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(order_column)
        
        # 分页查询
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
            message='获取商圈列表成功'
        )
        
    except Exception as e:
        return error_response(f'获取商圈列表失败: {str(e)}', 500)

@business_bp.route('/<area_id>', methods=['GET', 'OPTIONS'])
def get_business_area_by_id(area_id):
    """根据ID获取商圈详情"""
    try:
        area = BusinessArea.query.get(area_id)
        
        if not area:
            return error_response('商圈不存在', 404)
        
        # 获取商圈详细信息，包括店铺统计
        area_dict = area.to_dict()
        area_dict['store_statistics'] = {
            'total_stores': area.stores.count(),
            'by_category': dict(
                db.session.query(Store.category, func.count(Store.id))
                .filter_by(business_area_id=area_id)
                .group_by(Store.category)
                .all()
            ),
            'avg_rating': db.session.query(func.avg(Store.rating)).filter_by(business_area_id=area_id).scalar() or 0,
            'recommended_count': area.stores.filter_by(is_recommended=True).count()
        }
        
        return success_response(area_dict, '获取商圈详情成功')
        
    except Exception as e:
        return error_response(f'获取商圈详情失败: {str(e)}', 500)

@business_bp.route('/search', methods=['GET', 'OPTIONS'])
def search_business_areas():
    """搜索商圈"""
    try:
        keyword = request.args.get('keyword', '').strip()
        city_id = request.args.get('cityId', '')
        area_type = request.args.get('type', '')
        
        if not keyword:
            return error_response('搜索关键词不能为空', 400)
        
        # 构建查询
        query = BusinessArea.query.filter(BusinessArea.name.contains(keyword))
        
        if city_id:
            query = query.filter_by(city_id=city_id)
        
        if area_type:
            query = query.filter_by(type=area_type)
        
        # 按热度值排序，限制结果数量
        areas = query.order_by(desc(BusinessArea.hot_value)).limit(20).all()
        
        return success_response(
            [area.to_dict() for area in areas],
            '搜索商圈成功'
        )
        
    except Exception as e:
        return error_response(f'搜索商圈失败: {str(e)}', 500)

@business_bp.route('/hot-ranking', methods=['GET', 'OPTIONS'])
def get_hot_ranking():
    """获取商圈热度排行"""
    try:
        city_id = request.args.get('cityId', '')
        limit = int(request.args.get('limit', 10))
        
        # 构建查询
        query = BusinessArea.query
        
        if city_id:
            query = query.filter_by(city_id=city_id)
        
        # 按热度值排序
        areas = query.order_by(desc(BusinessArea.hot_value)).limit(limit).all()
        
        # 计算增长率（这里使用模拟数据）
        ranking_data = []
        for i, area in enumerate(areas):
            area_dict = area.to_dict()
            # 模拟增长率计算
            import random
            area_dict['growthRate'] = round(random.uniform(-5, 20), 1)
            area_dict['rank'] = i + 1
            ranking_data.append(area_dict)
        
        return success_response(ranking_data, '获取商圈热度排行成功')
        
    except Exception as e:
        return error_response(f'获取商圈热度排行失败: {str(e)}', 500)

@business_bp.route('/<area_id>/stats', methods=['GET', 'OPTIONS'])
def get_business_area_stats(area_id):
    """获取商圈统计数据"""
    try:
        area = BusinessArea.query.get(area_id)
        
        if not area:
            return error_response('商圈不存在', 404)
        
        # 获取统计数据
        stats = {
            'basic_info': area.to_dict(),
            'store_count': area.stores.count(),
            'category_distribution': dict(
                db.session.query(Store.category, func.count(Store.id))
                .filter_by(business_area_id=area_id)
                .group_by(Store.category)
                .all()
            ),
            'rating_distribution': {
                'avg_rating': db.session.query(func.avg(Store.rating)).filter_by(business_area_id=area_id).scalar() or 0,
                'high_rating_count': area.stores.filter(Store.rating >= 4.0).count(),
                'medium_rating_count': area.stores.filter(Store.rating >= 3.0, Store.rating < 4.0).count(),
                'low_rating_count': area.stores.filter(Store.rating < 3.0).count()
            },
            'price_distribution': {
                'avg_price': db.session.query(func.avg(Store.avg_price)).filter_by(business_area_id=area_id).scalar() or 0,
                'high_price_count': area.stores.filter(Store.avg_price >= 100).count(),
                'medium_price_count': area.stores.filter(Store.avg_price >= 50, Store.avg_price < 100).count(),
                'low_price_count': area.stores.filter(Store.avg_price < 50).count()
            }
        }
        
        return success_response(stats, '获取商圈统计数据成功')
        
    except Exception as e:
        return error_response(f'获取商圈统计数据失败: {str(e)}', 500)

@business_bp.route('/<area_id>/stores', methods=['GET', 'OPTIONS'])
def get_stores_by_area(area_id):
    """获取商圈内店铺列表"""
    try:
        area = BusinessArea.query.get(area_id)
        
        if not area:
            return error_response('商圈不存在', 404)
        
        # 获取查询参数
        category = request.args.get('category', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('pageSize', 20))
        sort_by = request.args.get('sortBy', 'rating')
        
        # 构建查询
        query = area.stores
        
        if category:
            query = query.filter_by(category=category)
        
        # 排序
        if sort_by == 'rating':
            query = query.order_by(desc(Store.rating))
        elif sort_by == 'price':
            query = query.order_by(Store.avg_price)
        elif sort_by == 'review_count':
            query = query.order_by(desc(Store.review_count))
        
        # 分页
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        stores = [store.to_dict() for store in pagination.items]
        
        return paginated_response(
            items=stores,
            total=pagination.total,
            page=page,
            per_page=per_page,
            message='获取商圈店铺列表成功'
        )
        
    except Exception as e:
        return error_response(f'获取商圈店铺列表失败: {str(e)}', 500)

@business_bp.route('/compare', methods=['POST', 'OPTIONS'])
def compare_business_areas():
    """商圈对比"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 400)
        
        area_ids = data.get('areaIds', [])
        
        if not area_ids or len(area_ids) < 2:
            return error_response('至少需要选择2个商圈进行对比', 400)
        
        if len(area_ids) > 5:
            return error_response('最多只能对比5个商圈', 400)
        
        # 获取商圈信息
        areas = BusinessArea.query.filter(BusinessArea.id.in_(area_ids)).all()
        
        if len(areas) != len(area_ids):
            return error_response('部分商圈不存在', 404)
        
        # 构建对比数据
        comparison_data = {
            'indicators': [
                {'name': '客流量', 'max': 100},
                {'name': '消费水平', 'max': 100},
                {'name': '用户评价', 'max': 100},
                {'name': '交通便利', 'max': 100},
                {'name': '配套设施', 'max': 100},
                {'name': '品牌丰富度', 'max': 100}
            ],
            'data': []
        }
        
        for area in areas:
            # 计算各项指标（这里使用模拟数据）
            import random
            area_data = {
                'name': area.name,
                'value': [
                    min(100, area.customer_flow / 100),  # 客流量
                    min(100, area.avg_consumption / 10),  # 消费水平
                    area.rating * 20,  # 用户评价
                    random.randint(60, 95),  # 交通便利（模拟）
                    len(area.facilities or []) * 10,  # 配套设施
                    min(100, area.store_count / 5)  # 品牌丰富度
                ]
            }
            comparison_data['data'].append(area_data)
        
        return success_response(comparison_data, '商圈对比数据获取成功')
        
    except Exception as e:
        return error_response(f'商圈对比失败: {str(e)}', 500)

@business_bp.route('/nearby', methods=['GET', 'OPTIONS'])
def get_nearby_business_areas():
    """获取附近商圈"""
    try:
        longitude = float(request.args.get('longitude', 0))
        latitude = float(request.args.get('latitude', 0))
        radius = int(request.args.get('radius', 5000))  # 默认5公里
        
        if not longitude or not latitude:
            return error_response('经纬度坐标不能为空', 400)
        
        # 简化的距离计算（实际应用中应使用地理空间查询）
        areas = BusinessArea.query.all()
        nearby_areas = []
        
        for area in areas:
            # 简单的距离计算（实际应使用Haversine公式）
            distance = ((area.longitude - longitude) ** 2 + (area.latitude - latitude) ** 2) ** 0.5 * 111000
            
            if distance <= radius:
                area_dict = area.to_dict()
                area_dict['distance'] = round(distance)
                nearby_areas.append(area_dict)
        
        # 按距离排序
        nearby_areas.sort(key=lambda x: x['distance'])
        
        return success_response(nearby_areas[:20], '获取附近商圈成功')  # 限制返回20个
        
    except ValueError:
        return error_response('坐标格式不正确', 400)
    except Exception as e:
        return error_response(f'获取附近商圈失败: {str(e)}', 500)

@business_bp.route('/search-and-save', methods=['POST', 'OPTIONS'])
def search_and_save_business_areas():
    """搜索并保存商圈数据（用于地图点击搜索）"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 400)
        
        longitude = float(data.get('longitude', 0))
        latitude = float(data.get('latitude', 0))
        radius = int(data.get('radius', 1000))
        city_id = data.get('cityId', '')
        search_areas = data.get('searchAreas', [])  # 从地图搜索得到的商圈数据
        
        if not longitude or not latitude:
            return error_response('经纬度坐标不能为空', 400)
        
        # 首先检查数据库中是否已有该坐标附近的数据
        existing_areas = []
        tolerance = 0.001  # 坐标容差，约100米
        
        # 查找附近已存在的商圈
        nearby_existing = BusinessArea.query.filter(
            db.and_(
                BusinessArea.longitude.between(longitude - tolerance, longitude + tolerance),
                BusinessArea.latitude.between(latitude - tolerance, latitude + tolerance)
            )
        ).all()
        
        if nearby_existing:
            # 如果数据库中已有附近数据，直接返回
            logger.info(f"从数据库返回附近商圈数据: {len(nearby_existing)}个")
            existing_areas = []
            for area in nearby_existing:
                area_dict = area.to_dict()
                # 计算精确距离
                distance = ((area.longitude - longitude) ** 2 + (area.latitude - latitude) ** 2) ** 0.5 * 111000
                area_dict['distance'] = round(distance)
                if distance <= radius:
                    existing_areas.append(area_dict)
            
            existing_areas.sort(key=lambda x: x['distance'])
            return success_response({
                'areas': existing_areas[:20],
                'source': 'database',
                'cached': True
            }, '从缓存获取附近商圈成功')
        
        # 如果数据库中没有数据，保存新搜索的数据
        saved_areas = []
        if search_areas:
            for area_data in search_areas:
                try:
                    # 生成唯一ID
                    import uuid
                    area_id = f"area_{uuid.uuid4().hex[:12]}"
                    
                    # 构建商圈数据
                    business_area_data = {
                        'id': area_id,
                        'name': area_data.get('name', ''),
                        'city_id': city_id or 'beijing',
                        'type': determine_area_type(area_data.get('category', '')),
                        'level': 'C',  # 默认等级
                        'longitude': float(area_data.get('longitude', longitude)),
                        'latitude': float(area_data.get('latitude', latitude)),
                        'hot_value': area_data.get('hotValue', 50),
                        'avg_consumption': area_data.get('avgConsumption', 0),
                        'store_count': area_data.get('storeCount', 0),
                        'address': area_data.get('address', ''),
                        'tags': area_data.get('tags', [])
                    }
                    
                    # 创建商圈记录
                    business_area = BusinessArea(**business_area_data)
                    db.session.add(business_area)
                    
                    # 添加距离信息
                    area_dict = business_area_data.copy()
                    distance = area_data.get('distance', 0)
                    area_dict['distance'] = distance
                    saved_areas.append(area_dict)
                    
                    logger.info(f"保存商圈: {area_data.get('name', 'Unknown')}")
                    
                except Exception as e:
                    logger.error(f"保存商圈数据失败: {str(e)}")
                    continue
            
            # 提交数据库事务
            try:
                db.session.commit()
                logger.info(f"成功保存 {len(saved_areas)} 个商圈到数据库")
            except Exception as e:
                db.session.rollback()
                logger.error(f"数据库提交失败: {str(e)}")
                return error_response('保存商圈数据失败', 500)
        
        # 按距离排序
        saved_areas.sort(key=lambda x: x.get('distance', 0))
        
        return success_response({
            'areas': saved_areas[:20],
            'source': 'search_and_save',
            'cached': False
        }, f'搜索并保存 {len(saved_areas)} 个商圈成功')
        
    except ValueError:
        return error_response('坐标格式不正确', 400)
    except Exception as e:
        logger.error(f"搜索并保存商圈失败: {str(e)}")
        return error_response(f'搜索并保存商圈失败: {str(e)}', 500)

def determine_area_type(category):
    """根据类别确定商圈类型"""
    if not category:
        return 'mixed'
    
    category = category.lower()
    if '购物' in category or 'shopping' in category or '商场' in category:
        return 'shopping'
    elif '餐饮' in category or '美食' in category or 'dining' in category:
        return 'dining'
    elif '娱乐' in category or 'entertainment' in category:
        return 'entertainment'
    else:
        return 'mixed'

@business_bp.route('/<area_id>/crawl-details', methods=['POST', 'OPTIONS'])
def crawl_area_details(area_id):
    """爬取商圈详细数据（大众点评等）"""
    from datetime import datetime, timedelta
    from app.crawler.data_sources.dianping_crawler import DianpingCrawler
    
    try:
        # 验证商圈是否存在
        area = BusinessArea.query.get(area_id)
        if not area:
            return error_response('商圈不存在', 404)
        
        # 检查是否有近2天内的数据
        two_days_ago = datetime.utcnow() - timedelta(days=2)
        recent_update = area.updated_at and area.updated_at > two_days_ago
        
        # 检查是否有详细的评价和店铺数据
        has_detailed_data = (
            area.stores.count() > 0 and 
            area.rating > 0 and 
            area.review_count > 0
        )
        
        if recent_update and has_detailed_data:
            logger.info(f"商圈 {area.name} 数据较新，直接返回缓存数据")
            return success_response({
                'area': area.to_dict(),
                'cached': True,
                'data_source': 'database',
                'last_updated': area.updated_at.isoformat() if area.updated_at else None
            }, '从缓存获取商圈详细数据成功')
        
        # 如果数据过期或不完整，启动爬虫获取最新数据
        logger.info(f"开始爬取商圈 {area.name} 的详细数据")
        
        # 初始化大众点评爬虫
        crawler = DianpingCrawler()
        
        # 爬取商圈详细信息
        area_details = crawler.search_area_by_name(area.name, area.city.name if area.city else '北京')
        
        if area_details:
            # 更新商圈基本信息
            area.rating = area_details.get('rating', area.rating)
            area.review_count = area_details.get('review_count', 0)
            area.hot_value = area_details.get('hot_value', area.hot_value)
            area.description = area_details.get('description', area.description)
            area.updated_at = datetime.utcnow()
            
            # 获取商圈评价
            reviews = crawler.get_area_reviews(area_id)
            if reviews:
                # 这里可以将评价存储到单独的评价表中
                logger.info(f"获取到 {len(reviews)} 条商圈评价")
            
            # 爬取商圈内的店铺数据
            stores_data = crawler.get_stores(
                area_id, 
                area.name,
                area.latitude,
                area.longitude
            )
            
            if stores_data:
                # 清除旧的店铺数据（可选）
                existing_stores = Store.query.filter_by(business_area_id=area_id).all()
                for store in existing_stores:
                    db.session.delete(store)
                
                # 添加新的店铺数据
                for store_data in stores_data:
                    try:
                        store = Store(**store_data)
                        db.session.add(store)
                        logger.info(f"添加店铺: {store_data.get('name', 'Unknown')}")
                    except Exception as e:
                        logger.error(f"添加店铺失败: {str(e)}")
                        continue
                
                # 更新商圈统计信息
                area.store_count = len(stores_data)
                
                # 计算平均评分和消费水平
                if stores_data:
                    avg_rating = sum(s.get('rating', 0) for s in stores_data) / len(stores_data)
                    avg_price = sum(s.get('avg_price', 0) for s in stores_data) / len(stores_data)
                    area.rating = round(avg_rating, 1) if avg_rating > 0 else area.rating
                    area.avg_consumption = round(avg_price, 2) if avg_price > 0 else area.avg_consumption
            
            # 提交数据库更改
            try:
                db.session.commit()
                logger.info(f"成功更新商圈 {area.name} 的详细数据")
                
                # 返回更新后的数据
                updated_area = area.to_dict()
                
                # 添加额外的统计信息
                updated_area.update({
                    'store_statistics': {
                        'total_stores': area.stores.count(),
                        'by_category': dict(
                            db.session.query(Store.category, func.count(Store.id))
                            .filter_by(business_area_id=area_id)
                            .group_by(Store.category)
                            .all()
                        ),
                        'avg_rating': db.session.query(func.avg(Store.rating)).filter_by(business_area_id=area_id).scalar() or 0,
                        'recommended_count': area.stores.filter_by(is_recommended=True).count()
                    },
                    'reviews_sample': reviews[:5] if reviews else [],  # 返回前5条评价作为样本
                    'cached': False,
                    'data_source': 'dianping_crawler',
                    'crawl_time': datetime.utcnow().isoformat()
                })
                
                return success_response(updated_area, f'成功爬取并更新商圈 {area.name} 的详细数据')
                
            except Exception as e:
                db.session.rollback()
                logger.error(f"保存商圈数据失败: {str(e)}")
                return error_response('保存商圈数据失败', 500)
        else:
            logger.warning(f"未能获取商圈 {area.name} 的详细数据")
            return error_response('未能获取商圈详细数据，请稍后重试', 500)
        
    except Exception as e:
        logger.error(f"爬取商圈详情失败: {str(e)}")
        return error_response(f'爬取商圈详情失败: {str(e)}', 500)


@business_bp.route('/areas/<int:area_id>/stores', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_area_stores(area_id):
    """获取商圈内的商家"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        category = request.args.get('category')
        
        # 验证商圈是否存在
        area = BusinessArea.query.get_or_404(area_id)
        
        query = Store.query.filter(Store.business_area_id == area_id)
        
        if category:
            query = query.filter(Store.category == category)
        
        # 按热度值排序
        query = query.order_by(Store.hot_value.desc())
        
        # 分页查询
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        stores = []
        for store in pagination.items:
            stores.append({
                'id': store.id,
                'name': store.name,
                'category': store.category,
                'longitude': float(store.longitude) if store.longitude else None,
                'latitude': float(store.latitude) if store.latitude else None,
                'hot_value': store.hot_value,
                'avg_consumption': float(store.avg_consumption) if store.avg_consumption else None,
                'rating': float(store.rating) if store.rating else None,
                'review_count': store.review_count
            })
        
        return success_response({
            'area_info': {
                'id': area.id,
                'name': area.name,
                'hot_value': area.hot_value,
                'avg_consumption': float(area.avg_consumption) if area.avg_consumption else None
            },
            'stores': stores,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"获取商圈商家失败: {str(e)}")
        return error_response('获取商圈商家失败', 500)


@business_bp.route('/areas/<int:area_id>/analytics', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_area_analytics(area_id):
    """获取商圈分析数据"""
    try:
        # 验证商圈是否存在
        area = BusinessArea.query.get_or_404(area_id)
        
        # 获取商圈内的商家
        stores = Store.query.filter(Store.business_area_id == area_id).all()
        
        # 计算统计数据
        total_stores = len(stores)
        avg_hot_value = sum(store.hot_value for store in stores) / total_stores if total_stores > 0 else 0
        avg_consumption = sum(float(store.avg_consumption or 0) for store in stores) / total_stores if total_stores > 0 else 0
        avg_rating = sum(float(store.rating or 0) for store in stores) / total_stores if total_stores > 0 else 0
        total_reviews = sum(store.review_count for store in stores)
        
        # 分类统计
        category_stats = {}
        for store in stores:
            category = store.category or '其他'
            if category not in category_stats:
                category_stats[category] = {'count': 0, 'hot_value': 0}
            category_stats[category]['count'] += 1
            category_stats[category]['hot_value'] += store.hot_value
        
        # 转换为列表格式
        category_distribution = []
        for category, stats in category_stats.items():
            category_distribution.append({
                'name': category,
                'count': stats['count'],
                'avg_hot_value': stats['hot_value'] / stats['count'],
                'percentage': round(stats['count'] / total_stores * 100, 2) if total_stores > 0 else 0
            })
        
        return success_response({
            'area_info': {
                'id': area.id,
                'name': area.name,
                'city_name': area.city.name if area.city else None,
                'longitude': float(area.longitude),
                'latitude': float(area.latitude),
                'hot_value': area.hot_value
            },
            'statistics': {
                'total_stores': total_stores,
                'avg_hot_value': round(avg_hot_value, 2),
                'avg_consumption': round(avg_consumption, 2),
                'avg_rating': round(avg_rating, 2),
                'total_reviews': total_reviews
            },
            'category_distribution': category_distribution
        })
        
    except Exception as e:
        logger.error(f"获取商圈分析数据失败: {str(e)}")
        return error_response('获取商圈分析数据失败', 500)