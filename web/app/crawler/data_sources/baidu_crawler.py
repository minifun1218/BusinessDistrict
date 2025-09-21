#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度地图API爬虫 - 获取商圈和POI数据
"""

import json
import logging
import hashlib
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode
from ..base_crawler import BaseCrawler

logger = logging.getLogger(__name__)

class BaiduMapCrawler(BaseCrawler):
    """百度地图API爬虫"""
    
    def __init__(self, api_key: str):
        super().__init__("百度地图API")
        self.api_key = api_key
        self.base_url = "https://api.map.baidu.com"
        
        # 商圈类型映射
        self.area_type_mapping = {
            '购物': 'shopping',
            '餐饮': 'dining', 
            '娱乐': 'entertainment',
            '综合': 'mixed'
        }
        
        # 店铺类型映射
        self.store_category_mapping = {
            '美食': 'restaurant',
            '购物': 'retail',
            '休闲娱乐': 'entertainment',
            '生活服务': 'service',
            '酒店': 'service',
            '景点': 'entertainment'
        }
    
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
            keywords = ['商圈', '商业区', '购物中心', '步行街']
            
            for keyword in keywords:
                areas = self._search_places(
                    query=keyword,
                    city_name=city_name,
                    center_lat=city_center['lat'],
                    center_lng=city_center['lng']
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
    
    def get_stores(self, area_id: str, area_name: str, area_lat: float = None, area_lng: float = None) -> List[Dict[str, Any]]:
        """获取商圈内的店铺数据"""
        try:
            logger.info(f"开始获取商圈 {area_name} 的店铺数据")
            
            if not area_lat or not area_lng:
                logger.error("商圈坐标信息缺失")
                return []
            
            stores = []
            # 搜索不同类型的店铺
            categories = ['美食', '购物', '休闲娱乐', '生活服务', '酒店']
            
            for category in categories:
                category_stores = self._search_places(
                    query=category,
                    center_lat=area_lat,
                    center_lng=area_lng,
                    radius=2000  # 2公里范围内
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
    
    def _search_places(self, query: str, city_name: str = None, center_lat: float = None, 
                      center_lng: float = None, radius: int = 10000) -> List[Dict[str, Any]]:
        """搜索地点"""
        try:
            url = f"{self.base_url}/place/v2/search"
            params = {
                'query': query,
                'output': 'json',
                'ak': self.api_key,
                'page_size': 20,
                'page_num': 0
            }
            
            if city_name:
                params['region'] = city_name
            elif center_lat and center_lng:
                params['location'] = f"{center_lat},{center_lng}"
                params['radius'] = radius
            
            response = self.make_request(url, params=params)
            data = response.json()
            
            if data.get('status') == 0 and data.get('results'):
                return data['results']
            return []
            
        except Exception as e:
            logger.error(f"搜索地点失败: {str(e)}")
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
            key = f"{area.get('name', '')}_{area.get('location', {}).get('lat', 0):.4f}_{area.get('location', {}).get('lng', 0):.4f}"
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
            key = f"{store.get('name', '')}_{store.get('location', {}).get('lat', 0):.4f}_{store.get('location', {}).get('lng', 0):.4f}"
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
            
            # 生成ID
            area_id = hashlib.md5(f"{city_id}_{name}_{location.get('lat')}_{location.get('lng')}".encode()).hexdigest()[:16]
            
            # 获取详细信息
            detail = None
            if area.get('uid'):
                detail = self._get_place_detail(area['uid'])
            
            return {
                'id': area_id,
                'name': name,
                'city_id': city_id,
                'type': self._determine_area_type(name, area.get('detail_info', {})),
                'level': self._determine_area_level(area.get('detail_info', {})),
                'longitude': float(location.get('lng', 0)),
                'latitude': float(location.get('lat', 0)),
                'address': area.get('address', ''),
                'hot_value': self._calculate_hot_value(area, detail),
                'description': self._extract_description(area, detail),
                'facilities': self._extract_facilities(detail) if detail else [],
                'tags': self._extract_tags(area, detail),
                'images': []  # 百度API通常不提供图片
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
            
            # 生成ID
            store_id = hashlib.md5(f"{area_id}_{name}_{location.get('lat')}_{location.get('lng')}".encode()).hexdigest()[:16]
            
            # 获取详细信息
            detail = None
            if store.get('uid'):
                detail = self._get_place_detail(store['uid'])
            
            return {
                'id': store_id,
                'name': name,
                'business_area_id': area_id,
                'category': self._determine_store_category(store.get('detail_info', {})),
                'longitude': float(location.get('lng', 0)),
                'latitude': float(location.get('lat', 0)),
                'address': store.get('address', ''),
                'phone': self._extract_phone(detail) if detail else None,
                'rating': self._extract_rating(detail) if detail else 0.0,
                'avg_price': self._extract_avg_price(detail) if detail else 0.0,
                'description': self._extract_description(store, detail),
                'tags': self._extract_tags(store, detail),
                'facilities': self._extract_facilities(detail) if detail else [],
                'images': []
            }
            
        except Exception as e:
            logger.error(f"格式化店铺数据失败: {str(e)}")
            return None
    
    def _determine_area_type(self, name: str, detail_info: Dict[str, Any]) -> str:
        """判断商圈类型"""
        if '购物' in name or '商场' in name or '百货' in name:
            return 'shopping'
        elif '美食' in name or '餐饮' in name:
            return 'dining'
        elif '娱乐' in name or '休闲' in name:
            return 'entertainment'
        else:
            return 'mixed'
    
    def _determine_area_level(self, detail_info: Dict[str, Any]) -> str:
        """判断商圈级别"""
        # 简单的级别判断逻辑，可以根据实际需要调整
        return 'B'  # 默认B级
    
    def _determine_store_category(self, detail_info: Dict[str, Any]) -> str:
        """判断店铺类别"""
        tag = detail_info.get('tag', '')
        for key, category in self.store_category_mapping.items():
            if key in tag:
                return category
        return 'service'  # 默认服务类
    
    def _calculate_hot_value(self, area: Dict[str, Any], detail: Dict[str, Any]) -> int:
        """计算热度值"""
        # 基于多个因素计算热度值
        base_score = 50
        
        # 根据名称知名度调整
        name = area.get('name', '')
        if any(keyword in name for keyword in ['万达', '银泰', '大悦城', '龙湖', '华润']):
            base_score += 30
        elif any(keyword in name for keyword in ['购物中心', '广场', '商场']):
            base_score += 20
        
        # 根据详细信息调整
        if detail:
            # 可以根据评论数、评分等调整热度
            pass
        
        return min(100, max(0, base_score))
    
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
    
    def _extract_avg_price(self, detail: Dict[str, Any]) -> float:
        """提取平均价格"""
        if not detail:
            return 0.0
        
        price = detail.get('detail_info', {}).get('price')
        try:
            return float(price) if price else 0.0
        except (ValueError, TypeError):
            return 0.0
