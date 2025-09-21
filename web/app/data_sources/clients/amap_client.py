#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高德地图开放API客户端 - 使用官方Web API获取POI和商圈数据
官方文档：https://lbs.amap.com/api/webservice/summary
"""

import json
import logging
import hashlib
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode
from ..base_client import BaseDataClient

logger = logging.getLogger(__name__)

class AmapClient(BaseDataClient):
    """高德地图开放API客户端"""
    
    def __init__(self, api_key: str):
        super().__init__("高德地图开放API", api_key)
        self.base_url = "https://restapi.amap.com/v3"
        
        # 商圈相关的POI分类代码
        self.business_area_types = [
            '060000',  # 购物服务
            '061000',  # 购物相关场所
            '061100',  # 商场
            '061200',  # 便民商店/便利店
            '061300',  # 家电电子
        ]
        
        # 店铺类型映射 - 基于高德POI分类
        self.store_category_mapping = {
            '050000': 'restaurant',    # 餐饮服务
            '060000': 'retail',        # 购物服务
            '080000': 'entertainment', # 休闲娱乐
            '070000': 'service',       # 生活服务
            '100000': 'service',       # 住宿服务
            '110000': 'entertainment', # 风景名胜
            '090000': 'service',       # 医疗保健服务
            '120000': 'service',       # 商务住宅
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """测试API连接"""
        try:
            # 使用地理编码API测试连接
            result = self._geocode('北京市')
            if result:
                return {'status': 'ok', 'message': '高德地图API连接正常'}
            else:
                return {'status': 'failed', 'message': '高德地图API响应异常'}
        except Exception as e:
            return {'status': 'error', 'message': f'高德地图API连接失败: {str(e)}'}
    
    def get_business_areas(self, city_id: str, city_name: str) -> List[Dict[str, Any]]:
        """获取城市商圈数据"""
        try:
            logger.info(f"开始获取 {city_name} 的商圈数据")
            
            business_areas = []
            
            # 1. 搜索购物中心和商场
            shopping_centers = self._search_pois(
                keywords='购物中心|商场|百货|商业广场',
                city=city_name,
                types='061100',  # 商场分类
                page_size=50
            )
            business_areas.extend(shopping_centers)
            
            # 2. 搜索商圈和商业区
            business_districts = self._search_pois(
                keywords='商圈|商业区|步行街|商业街',
                city=city_name,
                types='060000',  # 购物服务大类
                page_size=30
            )
            business_areas.extend(business_districts)
            
            # 3. 搜索知名商业地标
            landmarks = self._search_pois(
                keywords='万达|银泰|大悦城|龙湖|华润|恒隆|太古里|IFS',
                city=city_name,
                types='061100',
                page_size=20
            )
            business_areas.extend(landmarks)
            
            # 数据去重和处理
            unique_areas = self._deduplicate_areas(business_areas)
            
            # 转换为标准格式
            result = []
            for area in unique_areas:
                area_data = self._format_business_area(area, city_id, city_name)
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
                {'types': '050000', 'keywords': '餐厅|美食|咖啡|火锅', 'radius': 1500},
                {'types': '060000', 'keywords': '服装|化妆品|超市|专卖店', 'radius': 1500},
                {'types': '080000', 'keywords': '电影院|KTV|健身|游戏', 'radius': 1500},
                {'types': '070000', 'keywords': '银行|药店|美容|维修', 'radius': 1000},
                {'types': '100000', 'keywords': '酒店|宾馆', 'radius': 2000},
            ]
            
            for config in search_configs:
                category_stores = self._search_around(
                    location=f"{area_lng},{area_lat}",
                    types=config['types'],
                    keywords=config.get('keywords', ''),
                    radius=config['radius'],
                    page_size=50
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
    
    def _geocode(self, address: str) -> Optional[Dict[str, Any]]:
        """地理编码 - 将地址转换为坐标"""
        try:
            url = f"{self.base_url}/geocode/geo"
            params = {
                'key': self.api_key,
                'address': address,
                'output': 'JSON'
            }
            
            response = self.make_request(url, params=params)
            data = response.json()
            
            if data.get('status') == '1' and data.get('geocodes'):
                return data['geocodes'][0]
            return None
            
        except Exception as e:
            logger.error(f"地理编码失败: {str(e)}")
            return None
    
    def _search_pois(self, keywords: str, city: str, types: str = None, 
                     page_size: int = 20, page: int = 1) -> List[Dict[str, Any]]:
        """搜索POI - 文本搜索"""
        try:
            url = f"{self.base_url}/place/text"
            params = {
                'key': self.api_key,
                'keywords': keywords,
                'city': city,
                'output': 'JSON',
                'offset': page_size,
                'page': page,
                'extensions': 'all'  # 返回详细信息
            }
            
            if types:
                params['types'] = types
            
            response = self.make_request(url, params=params)
            data = response.json()
            
            if data.get('status') == '1' and data.get('pois'):
                return data['pois']
            return []
            
        except Exception as e:
            logger.error(f"搜索POI失败: {str(e)}")
            return []
    
    def _search_around(self, location: str, types: str, keywords: str = '', 
                      radius: int = 1000, page_size: int = 20) -> List[Dict[str, Any]]:
        """周边搜索 - 基于坐标搜索周边POI"""
        try:
            url = f"{self.base_url}/place/around"
            params = {
                'key': self.api_key,
                'location': location,
                'types': types,
                'radius': radius,
                'output': 'JSON',
                'offset': page_size,
                'page': 1,
                'extensions': 'all'
            }
            
            if keywords:
                params['keywords'] = keywords
            
            response = self.make_request(url, params=params)
            data = response.json()
            
            if data.get('status') == '1' and data.get('pois'):
                return data['pois']
            return []
            
        except Exception as e:
            logger.error(f"周边搜索失败: {str(e)}")
            return []
    
    def _get_poi_detail(self, poi_id: str) -> Optional[Dict[str, Any]]:
        """获取POI详情"""
        try:
            url = f"{self.base_url}/place/detail"
            params = {
                'key': self.api_key,
                'id': poi_id,
                'output': 'JSON',
                'extensions': 'all'
            }
            
            response = self.make_request(url, params=params)
            data = response.json()
            
            if data.get('status') == '1' and data.get('pois'):
                return data['pois'][0]
            return None
            
        except Exception as e:
            logger.error(f"获取POI详情失败: {str(e)}")
            return None
    
    def _deduplicate_areas(self, areas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """商圈数据去重"""
        seen = set()
        unique_areas = []
        
        for area in areas:
            # 使用名称和坐标作为去重标识
            location = area.get('location', '').split(',')
            if len(location) == 2:
                key = f"{area.get('name', '')}_{location[1][:6]}_{location[0][:6]}"
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
            location = store.get('location', '').split(',')
            if len(location) == 2:
                key = f"{store.get('name', '')}_{location[1][:6]}_{location[0][:6]}"
                if key not in seen:
                    seen.add(key)
                    unique_stores.append(store)
        
        return unique_stores
    
    def _format_business_area(self, area: Dict[str, Any], city_id: str, city_name: str) -> Optional[Dict[str, Any]]:
        """格式化商圈数据"""
        try:
            name = area.get('name', '')
            location = area.get('location', '').split(',')
            
            if not name or len(location) != 2:
                return None
            
            lng, lat = float(location[0]), float(location[1])
            
            # 生成ID
            area_id = hashlib.md5(f"{city_id}_{name}_{lat}_{lng}".encode()).hexdigest()[:16]
            
            return {
                'id': area_id,
                'name': name,
                'city_id': city_id,
                'type': self._determine_area_type(name, area.get('type', '')),
                'level': self._determine_area_level(area),
                'longitude': lng,
                'latitude': lat,
                'address': area.get('address', ''),
                'hot_value': self._calculate_hot_value(area),
                'avg_consumption': self._estimate_consumption(area),
                'customer_flow': self._estimate_customer_flow(area),
                'store_count': 0,  # 需要后续统计
                'rating': 0.0,  # 高德API通常不直接提供商圈评分
                'description': self._extract_description(area),
                'facilities': self._extract_facilities(area),
                'transportation': [],  # 可以后续调用公交API获取
                'tags': self._extract_tags(area),
                'images': []
            }
            
        except Exception as e:
            logger.error(f"格式化商圈数据失败: {str(e)}")
            return None
    
    def _format_store(self, store: Dict[str, Any], area_id: str) -> Optional[Dict[str, Any]]:
        """格式化店铺数据"""
        try:
            name = store.get('name', '')
            location = store.get('location', '').split(',')
            
            if not name or len(location) != 2:
                return None
            
            lng, lat = float(location[0]), float(location[1])
            
            # 生成ID
            store_id = hashlib.md5(f"{area_id}_{name}_{lat}_{lng}".encode()).hexdigest()[:16]
            
            return {
                'id': store_id,
                'name': name,
                'business_area_id': area_id,
                'category': self._determine_store_category(store.get('type', '')),
                'sub_category': self._get_sub_category(store.get('type', '')),
                'longitude': lng,
                'latitude': lat,
                'rating': 4.0,  # 默认评分，高德API不直接提供
                'review_count': 0,
                'avg_price': self._estimate_price(store),
                'phone': store.get('tel', ''),
                'address': store.get('address', ''),
                'opening_hours': self._extract_opening_hours(store),
                'description': self._extract_description(store),
                'images': [],
                'tags': self._extract_tags(store),
                'facilities': self._extract_facilities(store),
                'is_recommended': self._is_recommended(store)
            }
            
        except Exception as e:
            logger.error(f"格式化店铺数据失败: {str(e)}")
            return None
    
    def _determine_area_type(self, name: str, poi_type: str) -> str:
        """判断商圈类型"""
        name_lower = name.lower()
        if any(keyword in name for keyword in ['购物', '商场', '百货', 'mall']):
            return 'shopping'
        elif any(keyword in name for keyword in ['美食', '餐饮', '小吃']):
            return 'dining'
        elif any(keyword in name for keyword in ['娱乐', '休闲', '酒吧']):
            return 'entertainment'
        else:
            return 'mixed'
    
    def _determine_area_level(self, area: Dict[str, Any]) -> str:
        """判断商圈级别"""
        name = area.get('name', '')
        
        # 根据知名度和规模判断级别
        if any(keyword in name for keyword in ['万达', '银泰', '大悦城', '龙湖', '华润', '恒隆', '太古里', 'IFS']):
            return 'A'
        elif any(keyword in name for keyword in ['购物中心', '广场', '商城', '百货']):
            return 'B'
        else:
            return 'C'
    
    def _determine_store_category(self, poi_type: str) -> str:
        """判断店铺类别"""
        if not poi_type:
            return 'service'
        
        type_code = poi_type.split('|')[0] if '|' in poi_type else poi_type[:6]
        return self.store_category_mapping.get(type_code, 'service')
    
    def _get_sub_category(self, poi_type: str) -> Optional[str]:
        """获取子分类"""
        if '|' in poi_type:
            parts = poi_type.split('|')
            return parts[-1] if len(parts) > 1 else None
        return None
    
    def _calculate_hot_value(self, area: Dict[str, Any]) -> int:
        """计算热度值"""
        base_score = 50
        name = area.get('name', '')
        
        # 根据名称知名度调整
        if any(keyword in name for keyword in ['万达', '银泰', '大悦城', '龙湖', '华润']):
            base_score += 35
        elif any(keyword in name for keyword in ['购物中心', '广场', '商场']):
            base_score += 25
        elif '步行街' in name:
            base_score += 20
        
        # 根据地址判断位置重要性
        address = area.get('address', '')
        if any(keyword in address for keyword in ['市中心', 'CBD', '核心区', '中央商务']):
            base_score += 15
        
        return min(100, max(0, base_score))
    
    def _estimate_consumption(self, area: Dict[str, Any]) -> float:
        """估算平均消费"""
        name = area.get('name', '')
        if any(keyword in name for keyword in ['万达', '银泰', '大悦城', '太古里', 'IFS']):
            return 180.0
        elif '购物中心' in name:
            return 140.0
        elif '步行街' in name:
            return 90.0
        else:
            return 110.0
    
    def _estimate_customer_flow(self, area: Dict[str, Any]) -> int:
        """估算客流量"""
        hot_value = self._calculate_hot_value(area)
        return int(hot_value * 800)  # 基于热度估算日均客流
    
    def _estimate_price(self, store: Dict[str, Any]) -> float:
        """估算价格"""
        poi_type = store.get('type', '')
        
        if '050000' in poi_type:  # 餐饮
            if '中餐厅' in poi_type or '火锅店' in poi_type:
                return 85.0
            elif '快餐厅' in poi_type:
                return 35.0
            elif '咖啡厅' in poi_type:
                return 45.0
            else:
                return 65.0
        elif '060000' in poi_type:  # 购物
            return 220.0
        elif '080000' in poi_type:  # 娱乐
            return 120.0
        else:
            return 60.0
    
    def _extract_opening_hours(self, item: Dict[str, Any]) -> Optional[str]:
        """提取营业时间"""
        # 高德API的扩展信息中可能包含营业时间
        return None  # 需要根据实际API响应调整
    
    def _extract_description(self, item: Dict[str, Any]) -> str:
        """提取描述信息"""
        parts = []
        
        if item.get('address'):
            parts.append(f"地址：{item['address']}")
        
        if item.get('type'):
            type_name = item['type'].split('|')[-1] if '|' in item['type'] else item['type']
            parts.append(f"类型：{type_name}")
        
        return self.clean_text(' | '.join(parts))
    
    def _extract_facilities(self, item: Dict[str, Any]) -> List[str]:
        """提取设施信息"""
        facilities = []
        
        # 从类型信息推断设施
        poi_type = item.get('type', '')
        if '停车' in poi_type:
            facilities.append('停车场')
        
        # 可以根据实际API响应添加更多设施信息
        return facilities
    
    def _extract_tags(self, item: Dict[str, Any]) -> List[str]:
        """提取标签"""
        tags = []
        
        # 从类型信息提取标签
        if item.get('type'):
            type_parts = item['type'].split('|')
            tags.extend([part.strip() for part in type_parts if part.strip()])
        
        return list(set(tags))  # 去重
    
    def _is_recommended(self, store: Dict[str, Any]) -> bool:
        """判断是否推荐"""
        # 简单的推荐逻辑，可以根据实际需求调整
        name = store.get('name', '')
        return any(brand in name for brand in ['星巴克', '麦当劳', '肯德基', '海底捞', 'H&M', 'ZARA', 'UNIQLO'])
