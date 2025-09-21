#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度地图开放API客户端 - 使用官方Web API获取POI和商圈数据
官方文档：https://lbsyun.baidu.com/index.php?title=webapi
"""

import json
import logging
import hashlib
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode
from ..base_client import BaseDataClient

logger = logging.getLogger(__name__)

class BaiduMapClient(BaseDataClient):
    """百度地图开放API客户端"""
    
    def __init__(self, api_key: str):
        super().__init__("百度地图开放API", api_key)
        self.base_url = "https://api.map.baidu.com"
        
        # 商圈相关的行业分类
        self.business_area_industries = [
            '购物',
            '商务大厦', 
            '购物中心',
            '商场',
            '百货商店'
        ]
        
        # 店铺类型映射
        self.store_category_mapping = {
            '美食': 'restaurant',
            '购物': 'retail',
            '休闲娱乐': 'entertainment',
            '生活服务': 'service',
            '酒店': 'service',
            '景点': 'entertainment',
            '汽车服务': 'service',
            '医疗': 'service',
            '教育培训': 'service',
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """测试API连接"""
        try:
            # 使用地理编码API测试连接
            result = self._get_city_center('北京市')
            if result:
                return {'status': 'ok', 'message': '百度地图API连接正常'}
            else:
                return {'status': 'failed', 'message': '百度地图API响应异常'}
        except Exception as e:
            return {'status': 'error', 'message': f'百度地图API连接失败: {str(e)}'}
    
    def get_business_areas(self, city_id: str, city_name: str) -> List[Dict[str, Any]]:
        """获取城市商圈数据"""
        try:
            logger.info(f"开始获取 {city_name} 的商圈数据")
            
            # 1. 先获取城市中心坐标
            city_center = self._get_city_center(city_name)
            if not city_center:
                logger.error(f"无法获取城市 {city_name} 的中心坐标")
                return []
            
            # 2. 搜索商圈
            business_areas = []
            
            # 搜索不同类型的商圈
            search_keywords = [
                '商圈',
                '商业区', 
                '购物中心',
                '商场',
                '步行街',
                '商业广场',
                '万达广场',
                '银泰城',
                '大悦城'
            ]
            
            for keyword in search_keywords:
                areas = self._search_places(
                    query=keyword,
                    region=city_name,
                    page_size=20
                )
                business_areas.extend(areas)
            
            # 3. 数据去重和处理
            unique_areas = self._deduplicate_areas(business_areas)
            
            # 4. 转换为标准格式
            result = []
            for area in unique_areas:
                area_data = self._format_business_area(area, city_id)
                if area_data:
                    result.append(area_data)
            
            logger.info(f"成功获取 {city_name} 的 {len(result)} 个商圈")
            return result
            
        except Exception as e:
            logger.error(f"获取 {city_name} 商圈数据失败: {str(e)}")
            return []
    
    def get_stores(self, area_id: str, area_name: str, area_lat: float, area_lng: float) -> List[Dict[str, Any]]:
        """获取商圈内的店铺数据"""
        try:
            logger.info(f"开始获取商圈 {area_name} 的店铺数据")
            
            stores = []
            
            # 搜索不同类型的店铺
            search_configs = [
                {'query': '美食', 'radius': 2000, 'page_size': 20},
                {'query': '购物', 'radius': 2000, 'page_size': 20},
                {'query': '休闲娱乐', 'radius': 1500, 'page_size': 15},
                {'query': '生活服务', 'radius': 1000, 'page_size': 15},
                {'query': '酒店', 'radius': 2000, 'page_size': 10},
            ]
            
            for config in search_configs:
                category_stores = self._search_nearby(
                    location=f"{area_lat},{area_lng}",
                    query=config['query'],
                    radius=config['radius'],
                    page_size=config['page_size']
                )
                stores.extend(category_stores)
            
            # 数据去重和处理
            unique_stores = self._deduplicate_stores(stores)
            
            # 转换为标准格式
            result = []
            for store in unique_stores:
                store_data = self._format_store(store, area_id)
                if store_data:
                    result.append(store_data)
            
            logger.info(f"成功获取商圈 {area_name} 的 {len(result)} 个店铺")
            return result
            
        except Exception as e:
            logger.error(f"获取商圈 {area_name} 店铺数据失败: {str(e)}")
            return []
    
    def _get_city_center(self, city_name: str) -> Optional[Dict[str, float]]:
        """获取城市中心坐标"""
        try:
            url = f"{self.base_url}/geocoding/v3/"
            params = {
                'address': city_name,
                'output': 'json',
                'ak': self.api_key
            }
            
            response = self.make_request(url, params=params)
            data = response.json()
            
            if data.get('status') == 0 and data.get('result'):
                location = data['result']['location']
                return {
                    'lng': location['lng'],
                    'lat': location['lat']
                }
            return None
            
        except Exception as e:
            logger.error(f"获取城市中心坐标失败: {str(e)}")
            return None
    
    def _search_places(self, query: str, region: str = None, 
                      page_size: int = 20, page_num: int = 0) -> List[Dict[str, Any]]:
        """搜索地点 - 区域检索"""
        try:
            url = f"{self.base_url}/place/v2/search"
            params = {
                'query': query,
                'output': 'json',
                'ak': self.api_key,
                'page_size': page_size,
                'page_num': page_num,
                'scope': 2  # 返回详细信息
            }
            
            if region:
                params['region'] = region
            
            response = self.make_request(url, params=params)
            data = response.json()
            
            if data.get('status') == 0 and data.get('results'):
                return data['results']
            return []
            
        except Exception as e:
            logger.error(f"搜索地点失败: {str(e)}")
            return []
    
    def _search_nearby(self, location: str, query: str, 
                      radius: int = 2000, page_size: int = 20) -> List[Dict[str, Any]]:
        """周边搜索"""
        try:
            url = f"{self.base_url}/place/v2/search"
            params = {
                'query': query,
                'location': location,
                'radius': radius,
                'output': 'json',
                'ak': self.api_key,
                'page_size': page_size,
                'page_num': 0,
                'scope': 2
            }
            
            response = self.make_request(url, params=params)
            data = response.json()
            
            if data.get('status') == 0 and data.get('results'):
                return data['results']
            return []
            
        except Exception as e:
            logger.error(f"周边搜索失败: {str(e)}")
            return []
    
    def _get_place_detail(self, uid: str) -> Optional[Dict[str, Any]]:
        """获取地点详情"""
        try:
            url = f"{self.base_url}/place/v2/detail"
            params = {
                'uid': uid,
                'output': 'json',
                'ak': self.api_key,
                'scope': 2  # 获取详细信息
            }
            
            response = self.make_request(url, params=params)
            data = response.json()
            
            if data.get('status') == 0 and data.get('result'):
                return data['result']
            return None
            
        except Exception as e:
            logger.error(f"获取地点详情失败: {str(e)}")
            return None
    
    def _deduplicate_areas(self, areas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """商圈数据去重"""
        seen = set()
        unique_areas = []
        
        for area in areas:
            # 使用名称和坐标作为去重标识
            location = area.get('location', {})
            lat = location.get('lat', 0)
            lng = location.get('lng', 0)
            key = f"{area.get('name', '')}_{lat:.4f}_{lng:.4f}"
            
            if key not in seen:
                seen.add(key)
                unique_areas.append(area)
        
        return unique_areas
    
    def _deduplicate_stores(self, stores: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """店铺数据去重"""
        seen = set()
        unique_stores = []
        
        for store in stores:
            # 使用名称和坐标作为去重标识
            location = store.get('location', {})
            lat = location.get('lat', 0)
            lng = location.get('lng', 0)
            key = f"{store.get('name', '')}_{lat:.4f}_{lng:.4f}"
            
            if key not in seen:
                seen.add(key)
                unique_stores.append(store)
        
        return unique_stores
    
    def _format_business_area(self, area: Dict[str, Any], city_id: str) -> Optional[Dict[str, Any]]:
        """格式化商圈数据"""
        try:
            name = area.get('name', '')
            location = area.get('location', {})
            
            if not name or not location:
                return None
            
            lat = location.get('lat', 0)
            lng = location.get('lng', 0)
            
            # 生成ID
            area_id = hashlib.md5(f"{city_id}_{name}_{lat}_{lng}".encode()).hexdigest()[:16]
            
            # 获取详细信息
            detail = None
            if area.get('uid'):
                detail = self._get_place_detail(area['uid'])
            
            return {
                'id': area_id,
                'name': name,
                'city_id': city_id,
                'type': self._determine_area_type(name, area.get('detail_info', {})),
                'level': self._determine_area_level(area),
                'longitude': float(lng),
                'latitude': float(lat),
                'address': area.get('address', ''),
                'hot_value': self._calculate_hot_value(area, detail),
                'avg_consumption': self._estimate_consumption(area),
                'customer_flow': self._estimate_customer_flow(area),
                'store_count': 0,
                'rating': 0.0,
                'description': self._extract_description(area, detail),
                'facilities': self._extract_facilities(detail) if detail else [],
                'transportation': [],
                'tags': self._extract_tags(area, detail),
                'images': []
            }
            
        except Exception as e:
            logger.error(f"格式化商圈数据失败: {str(e)}")
            return None
    
    def _format_store(self, store: Dict[str, Any], area_id: str) -> Optional[Dict[str, Any]]:
        """格式化店铺数据"""
        try:
            name = store.get('name', '')
            location = store.get('location', {})
            
            if not name or not location:
                return None
            
            lat = location.get('lat', 0)
            lng = location.get('lng', 0)
            
            # 生成ID
            store_id = hashlib.md5(f"{area_id}_{name}_{lat}_{lng}".encode()).hexdigest()[:16]
            
            # 获取详细信息
            detail = None
            if store.get('uid'):
                detail = self._get_place_detail(store['uid'])
            
            return {
                'id': store_id,
                'name': name,
                'business_area_id': area_id,
                'category': self._determine_store_category(store.get('detail_info', {})),
                'sub_category': None,
                'longitude': float(lng),
                'latitude': float(lat),
                'rating': self._extract_rating(detail) if detail else 4.0,
                'review_count': 0,
                'avg_price': self._estimate_price(store),
                'phone': self._extract_phone(detail) if detail else None,
                'address': store.get('address', ''),
                'opening_hours': None,
                'description': self._extract_description(store, detail),
                'images': [],
                'tags': self._extract_tags(store, detail),
                'facilities': self._extract_facilities(detail) if detail else [],
                'is_recommended': self._is_recommended(store)
            }
            
        except Exception as e:
            logger.error(f"格式化店铺数据失败: {str(e)}")
            return None
    
    def _determine_area_type(self, name: str, detail_info: Dict[str, Any]) -> str:
        """判断商圈类型"""
        if any(keyword in name for keyword in ['购物', '商场', '百货']):
            return 'shopping'
        elif any(keyword in name for keyword in ['美食', '餐饮']):
            return 'dining'
        elif any(keyword in name for keyword in ['娱乐', '休闲']):
            return 'entertainment'
        else:
            return 'mixed'
    
    def _determine_area_level(self, area: Dict[str, Any]) -> str:
        """判断商圈级别"""
        name = area.get('name', '')
        
        if any(keyword in name for keyword in ['万达', '银泰', '大悦城', '龙湖', '华润']):
            return 'A'
        elif any(keyword in name for keyword in ['购物中心', '广场', '商场']):
            return 'B'
        else:
            return 'C'
    
    def _determine_store_category(self, detail_info: Dict[str, Any]) -> str:
        """判断店铺类别"""
        tag = detail_info.get('tag', '')
        for key, category in self.store_category_mapping.items():
            if key in tag:
                return category
        return 'service'  # 默认服务类
    
    def _calculate_hot_value(self, area: Dict[str, Any], detail: Dict[str, Any]) -> int:
        """计算热度值"""
        base_score = 50
        name = area.get('name', '')
        
        # 根据名称知名度调整
        if any(keyword in name for keyword in ['万达', '银泰', '大悦城', '龙湖', '华润']):
            base_score += 30
        elif any(keyword in name for keyword in ['购物中心', '广场', '商场']):
            base_score += 20
        
        # 根据详细信息调整
        if detail:
            # 可以根据评论数、评分等调整热度
            pass
        
        return min(100, max(0, base_score))
    
    def _estimate_consumption(self, area: Dict[str, Any]) -> float:
        """估算平均消费"""
        name = area.get('name', '')
        if any(keyword in name for keyword in ['万达', '银泰', '大悦城']):
            return 160.0
        elif '购物中心' in name:
            return 130.0
        elif '步行街' in name:
            return 85.0
        else:
            return 110.0
    
    def _estimate_customer_flow(self, area: Dict[str, Any]) -> int:
        """估算客流量"""
        hot_value = self._calculate_hot_value(area, None)
        return int(hot_value * 900)
    
    def _estimate_price(self, store: Dict[str, Any]) -> float:
        """估算价格"""
        detail_info = store.get('detail_info', {})
        tag = detail_info.get('tag', '')
        
        if '美食' in tag:
            return 75.0
        elif '购物' in tag:
            return 200.0
        elif '娱乐' in tag:
            return 110.0
        else:
            return 55.0
    
    def _extract_description(self, item: Dict[str, Any], detail: Dict[str, Any]) -> str:
        """提取描述信息"""
        if detail and detail.get('detail_info', {}).get('comment'):
            return self.clean_text(detail['detail_info']['comment'])
        return self.clean_text(item.get('address', ''))
    
    def _extract_facilities(self, detail: Dict[str, Any]) -> List[str]:
        """提取设施信息"""
        if not detail:
            return []
        
        facilities = []
        detail_info = detail.get('detail_info', {})
        
        # 从标签中提取设施信息
        tag = detail_info.get('tag', '')
        if '停车' in tag:
            facilities.append('停车场')
        if 'WiFi' in tag or 'wifi' in tag:
            facilities.append('免费WiFi')
        
        return facilities
    
    def _extract_tags(self, item: Dict[str, Any], detail: Dict[str, Any]) -> List[str]:
        """提取标签"""
        tags = []
        
        # 从分类信息提取标签
        if item.get('detail_info', {}).get('tag'):
            tags.append(item['detail_info']['tag'])
        
        # 从详细信息提取标签
        if detail and detail.get('detail_info', {}).get('tag'):
            tags.append(detail['detail_info']['tag'])
        
        return list(set(tags))  # 去重
    
    def _extract_phone(self, detail: Dict[str, Any]) -> Optional[str]:
        """提取电话号码"""
        if not detail:
            return None
        return detail.get('detail_info', {}).get('telephone')
    
    def _extract_rating(self, detail: Dict[str, Any]) -> float:
        """提取评分"""
        if not detail:
            return 0.0
        
        rating = detail.get('detail_info', {}).get('overall_rating')
        try:
            return float(rating) if rating else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def _is_recommended(self, store: Dict[str, Any]) -> bool:
        """判断是否推荐"""
        name = store.get('name', '')
        return any(brand in name for brand in ['星巴克', '麦当劳', '肯德基', '海底捞', 'H&M', 'ZARA', 'UNIQLO'])
