#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大众点评数据客户端 - 模拟数据源
注意：由于大众点评没有开放API，这里使用模拟数据来演示数据结构
实际项目中建议通过官方合作或第三方数据服务获取真实数据
"""

import json
import logging
import hashlib
import random
from typing import Dict, List, Optional, Any
from ..base_client import BaseDataClient

logger = logging.getLogger(__name__)

class DianpingClient(BaseDataClient):
    """大众点评数据客户端（模拟版本）"""
    
    def __init__(self):
        super().__init__("大众点评模拟数据源")
        
        # 店铺类型映射
        self.category_mapping = {
            '美食': 'restaurant',
            '购物': 'retail',
            '休闲娱乐': 'entertainment',
            '生活服务': 'service',
            '酒店': 'service',
            '景点': 'entertainment'
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """测试连接"""
        return {'status': 'ok', 'message': '大众点评模拟数据源连接正常'}
    
    def get_business_areas(self, city_id: str, city_name: str) -> List[Dict[str, Any]]:
        """获取城市商圈数据（模拟版本）"""
        try:
            logger.info(f"开始获取 {city_name} 的商圈数据（模拟）")
            
            # 生成模拟商圈数据
            mock_areas = self._generate_mock_areas(city_id, city_name)
            
            logger.info(f"成功获取 {city_name} 的 {len(mock_areas)} 个商圈（模拟）")
            return mock_areas
            
        except Exception as e:
            logger.error(f"获取 {city_name} 商圈数据失败: {str(e)}")
            return []
    
    def get_stores(self, area_id: str, area_name: str, area_lat: float, area_lng: float) -> List[Dict[str, Any]]:
        """获取商圈内的店铺数据（模拟版本）"""
        try:
            logger.info(f"开始获取商圈 {area_name} 的店铺数据（模拟）")
            
            # 生成模拟店铺数据
            mock_stores = self._generate_mock_stores(area_id, area_name, area_lat, area_lng)
            
            logger.info(f"成功获取商圈 {area_name} 的 {len(mock_stores)} 个店铺（模拟）")
            return mock_stores
            
        except Exception as e:
            logger.error(f"获取商圈 {area_name} 店铺数据失败: {str(e)}")
            return []
    
    def _generate_mock_areas(self, city_id: str, city_name: str) -> List[Dict[str, Any]]:
        """生成模拟商圈数据"""
        mock_areas = []
        
        # 预定义商圈名称模板
        area_templates = [
            f"{city_name}万达广场",
            f"{city_name}银泰城",
            f"{city_name}大悦城",
            f"{city_name}步行街",
            f"{city_name}老街",
            f"{city_name}CBD商圈",
            f"{city_name}购物中心",
            f"{city_name}商业街",
            f"{city_name}太古里",
            f"{city_name}IFS国际金融中心"
        ]
        
        # 根据城市设置基础坐标（这里使用一些主要城市的坐标）
        city_coords = {
            '北京': (39.9042, 116.4074),
            '上海': (31.2304, 121.4737),
            '广州': (23.1291, 113.2644),
            '深圳': (22.5431, 114.0579),
            '杭州': (30.2741, 120.1551),
            '成都': (30.6595, 104.0657),
            '西安': (34.3416, 108.9398),
            '南京': (32.0603, 118.7969),
            '武汉': (30.5928, 114.3055),
            '重庆': (29.5647, 106.5507)
        }
        
        base_lat, base_lng = city_coords.get(city_name, (39.9042, 116.4074))
        
        # 选择6-8个商圈
        selected_areas = random.sample(area_templates, random.randint(6, 8))
        
        for i, area_name in enumerate(selected_areas):
            area_id = hashlib.md5(f"{city_id}_{area_name}".encode()).hexdigest()[:16]
            
            # 生成随机坐标偏移
            lat_offset = random.uniform(-0.15, 0.15)
            lng_offset = random.uniform(-0.15, 0.15)
            
            mock_area = {
                'id': area_id,
                'name': area_name,
                'city_id': city_id,
                'type': self._random_area_type(),
                'level': self._determine_area_level_by_name(area_name),
                'longitude': base_lng + lng_offset,
                'latitude': base_lat + lat_offset,
                'address': f"{city_name}市{area_name}",
                'hot_value': random.randint(65, 95),
                'avg_consumption': round(random.uniform(90, 220), 2),
                'customer_flow': random.randint(8000, 25000),
                'store_count': random.randint(80, 400),
                'rating': round(random.uniform(4.1, 4.7), 1),
                'description': f"{area_name}是{city_name}的重要商圈，汇聚了众多知名品牌和特色店铺，是购物休闲的理想去处。",
                'facilities': self._random_facilities(),
                'transportation': self._random_transportation(),
                'tags': self._random_area_tags(area_name),
                'images': []
            }
            
            mock_areas.append(mock_area)
        
        return mock_areas
    
    def _generate_mock_stores(self, area_id: str, area_name: str, area_lat: float, area_lng: float) -> List[Dict[str, Any]]:
        """生成模拟店铺数据"""
        mock_stores = []
        
        # 知名品牌店铺模板
        store_templates = {
            'restaurant': [
                '海底捞火锅', '星巴克咖啡', '麦当劳', '肯德基', '必胜客',
                '外婆家', '绿茶餐厅', '西贝莜面村', '呷哺呷哺', '真功夫',
                '小南国', '鼎泰丰', '和府捞面', '喜茶', '奈雪的茶',
                '胖哥俩肉蟹煲', '江边城外', '巴奴毛肚火锅'
            ],
            'retail': [
                'H&M', 'ZARA', 'UNIQLO', '优衣库', '无印良品',
                '屈臣氏', '万宁', '苏宁易购', '国美电器', '小米之家',
                'Nike', 'Adidas', '李宁', '安踏', 'Converse',
                '周大福', '周生生', 'Pandora', 'Swarovski'
            ],
            'entertainment': [
                '万达影城', 'CGV影城', '大玩家', 'KTV', '健身房',
                '游戏厅', '密室逃脱', '桌游吧', '网咖', '台球厅',
                '溜冰场', '保龄球馆', '电玩城', 'VR体验馆'
            ],
            'service': [
                '中国银行', '工商银行', '建设银行', '招商银行',
                '美容美发', '洗衣店', '快递点', '中国移动', '中国联通',
                '药店', '眼镜店', '手机维修', '干洗店', '照相馆',
                '中国邮政', '顺丰速运', '圆通快递'
            ]
        }
        
        # 为每个类别生成店铺
        for category, names in store_templates.items():
            # 随机选择该类别的店铺数量
            num_stores = random.randint(3, 6)
            selected_names = random.sample(names, min(num_stores, len(names)))
            
            for name in selected_names:
                store_id = hashlib.md5(f"{area_id}_{name}".encode()).hexdigest()[:16]
                
                # 在商圈周围生成随机坐标
                lat_offset = random.uniform(-0.01, 0.01)
                lng_offset = random.uniform(-0.01, 0.01)
                
                mock_store = {
                    'id': store_id,
                    'name': name,
                    'business_area_id': area_id,
                    'category': category,
                    'sub_category': self._get_sub_category(category, name),
                    'longitude': area_lng + lng_offset,
                    'latitude': area_lat + lat_offset,
                    'rating': round(random.uniform(3.8, 4.9), 1),
                    'review_count': random.randint(150, 3000),
                    'avg_price': self._random_price_by_category(category, name),
                    'phone': self._generate_phone(),
                    'address': f"{area_name}内{name}",
                    'opening_hours': self._random_opening_hours(),
                    'description': self._generate_store_description(name, category),
                    'images': [],
                    'tags': self._random_store_tags(category, name),
                    'facilities': self._random_store_facilities(category),
                    'is_recommended': self._is_brand_recommended(name)
                }
                
                mock_stores.append(mock_store)
        
        return mock_stores
    
    def _determine_area_level_by_name(self, area_name: str) -> str:
        """根据商圈名称判断级别"""
        if any(keyword in area_name for keyword in ['万达', '银泰', '大悦城', '太古里', 'IFS']):
            return 'A'
        elif any(keyword in area_name for keyword in ['购物中心', '商业街', '步行街']):
            return 'B'
        else:
            return 'C'
    
    def _random_area_type(self) -> str:
        """随机商圈类型"""
        return random.choice(['shopping', 'dining', 'entertainment', 'mixed'])
    
    def _random_facilities(self) -> List[str]:
        """随机设施"""
        all_facilities = [
            '停车场', '免费WiFi', '母婴室', '无障碍通道', 'ATM', 
            '休息区', '充电站', '儿童游乐区', '美食广场', '电影院'
        ]
        return random.sample(all_facilities, random.randint(4, 7))
    
    def _random_transportation(self) -> List[Dict[str, Any]]:
        """随机交通信息"""
        transport_options = [
            {'type': '地铁', 'lines': ['1号线', '2号线', '3号线', '4号线', '5号线']},
            {'type': '公交', 'lines': ['快速公交', '普通公交']},
            {'type': '出租车', 'lines': ['打车便利']}
        ]
        
        transportation = []
        for transport in transport_options:
            if random.choice([True, False]):
                selected_lines = random.sample(transport['lines'], random.randint(1, 2))
                transportation.append({
                    'type': transport['type'],
                    'description': f"附近有{transport['type']}站点",
                    'lines': selected_lines,
                    'distance': f"{random.randint(100, 500)}米"
                })
        
        return transportation
    
    def _random_area_tags(self, area_name: str) -> List[str]:
        """随机商圈标签"""
        base_tags = ['购物天堂', '美食聚集地', '时尚潮流', '休闲娱乐', '交通便利', '品牌齐全']
        
        # 根据商圈名称添加特定标签
        if '万达' in area_name:
            base_tags.extend(['连锁品牌', '一站式购物'])
        elif '步行街' in area_name:
            base_tags.extend(['历史文化', '特色小吃'])
        elif 'CBD' in area_name:
            base_tags.extend(['商务区', '高端消费'])
        
        return random.sample(base_tags, random.randint(3, 5))
    
    def _get_sub_category(self, category: str, name: str) -> Optional[str]:
        """获取子分类"""
        sub_categories = {
            'restaurant': {
                '火锅': ['海底捞', '呷哺呷哺', '巴奴'],
                '咖啡': ['星巴克', '喜茶', '奈雪'],
                '快餐': ['麦当劳', '肯德基', '真功夫'],
                '中餐': ['外婆家', '绿茶餐厅', '小南国'],
                '西餐': ['必胜客']
            },
            'retail': {
                '服装': ['H&M', 'ZARA', 'UNIQLO', '优衣库'],
                '化妆品': ['屈臣氏', '万宁'],
                '电器': ['苏宁', '国美', '小米'],
                '运动': ['Nike', 'Adidas', '李宁', '安踏'],
                '珠宝': ['周大福', '周生生', 'Pandora']
            },
            'entertainment': {
                '电影': ['万达影城', 'CGV影城'],
                '游戏': ['大玩家', '游戏厅', 'VR体验馆'],
                '运动': ['健身房', '保龄球馆', '溜冰场']
            },
            'service': {
                '银行': ['中国银行', '工商银行', '建设银行', '招商银行'],
                '通讯': ['中国移动', '中国联通'],
                '快递': ['顺丰', '圆通', '中国邮政']
            }
        }
        
        if category in sub_categories:
            for sub_cat, store_names in sub_categories[category].items():
                if any(store_name in name for store_name in store_names):
                    return sub_cat
        
        return None
    
    def _random_price_by_category(self, category: str, name: str) -> float:
        """根据类别和品牌生成价格"""
        # 知名品牌的价格区间
        brand_prices = {
            '星巴克': (35, 55),
            '海底捞': (80, 120),
            '麦当劳': (25, 45),
            'H&M': (50, 200),
            'ZARA': (100, 500),
            'UNIQLO': (80, 300),
            '万达影城': (40, 60)
        }
        
        # 检查是否是知名品牌
        for brand, price_range in brand_prices.items():
            if brand in name:
                return round(random.uniform(*price_range), 2)
        
        # 按类别设置默认价格范围
        price_ranges = {
            'restaurant': (35, 180),
            'retail': (60, 600),
            'entertainment': (50, 250),
            'service': (25, 120)
        }
        
        min_price, max_price = price_ranges.get(category, (40, 150))
        return round(random.uniform(min_price, max_price), 2)
    
    def _generate_phone(self) -> str:
        """生成随机电话号码"""
        prefixes = ['010', '021', '020', '0755', '0571', '028', '029', '025', '027', '023']
        prefix = random.choice(prefixes)
        number = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        return f"{prefix}-{number[:4]}-{number[4:]}"
    
    def _random_opening_hours(self) -> str:
        """随机营业时间"""
        start_hour = random.randint(8, 10)
        end_hour = random.randint(20, 22)
        return f"{start_hour:02d}:00-{end_hour:02d}:00"
    
    def _generate_store_description(self, name: str, category: str) -> str:
        """生成店铺描述"""
        descriptions = {
            'restaurant': f"{name}提供优质的餐饮服务，环境舒适，口味正宗，是聚餐的好选择。",
            'retail': f"{name}汇集时尚潮流商品，品质保证，价格合理，购物体验佳。",
            'entertainment': f"{name}设施齐全，环境优雅，是休闲娱乐的理想场所。",
            'service': f"{name}提供专业的服务，工作人员态度友好，服务效率高。"
        }
        
        return descriptions.get(category, f"{name}是一家优质的商户，欢迎您的光临。")
    
    def _random_store_tags(self, category: str, name: str) -> List[str]:
        """随机店铺标签"""
        tag_pools = {
            'restaurant': ['美味', '环境好', '服务佳', '性价比高', '网红店', '排队火爆', '特色菜'],
            'retail': ['品质好', '款式新', '价格实惠', '品牌正品', '服务好', '潮流时尚', '性价比高'],
            'entertainment': ['好玩', '设施新', '环境好', '性价比高', '适合聚会', '体验佳', '人气旺'],
            'service': ['专业', '便民', '服务好', '价格合理', '位置便利', '效率高', '态度好']
        }
        
        base_tags = tag_pools.get(category, ['服务好', '位置便利'])
        
        # 为知名品牌添加特殊标签
        if any(brand in name for brand in ['星巴克', '麦当劳', '肯德基']):
            base_tags.extend(['连锁品牌', '品质保证'])
        
        return random.sample(base_tags, random.randint(2, 4))
    
    def _random_store_facilities(self, category: str) -> List[str]:
        """随机店铺设施"""
        facility_pools = {
            'restaurant': ['WiFi', '停车位', '包厢', '外卖', '刷卡', '空调', '儿童座椅'],
            'retail': ['WiFi', '停车位', '试衣间', '刷卡', '会员卡', '空调', '无障碍通道'],
            'entertainment': ['WiFi', '停车位', '包厢', '会员卡', '预约', '空调', '储物柜'],
            'service': ['WiFi', '停车位', '刷卡', '预约', '会员卡', '排队系统', '空调']
        }
        
        facilities = facility_pools.get(category, ['WiFi', '刷卡'])
        return random.sample(facilities, random.randint(2, 4))
    
    def _is_brand_recommended(self, name: str) -> bool:
        """判断是否为推荐品牌"""
        recommended_brands = [
            '星巴克', '海底捞', '麦当劳', '肯德基', 'H&M', 'ZARA', 'UNIQLO', 
            '优衣库', '无印良品', '万达影城', 'CGV', '屈臣氏', '万宁'
        ]
        return any(brand in name for brand in recommended_brands)
