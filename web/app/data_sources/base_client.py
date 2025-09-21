#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据源客户端基类 - 定义通用的API客户端接口
"""

import time
import random
import logging
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class BaseDataClient(ABC):
    """数据源客户端基类"""
    
    def __init__(self, name: str, api_key: str = None, delay_range: tuple = (0.5, 1.5)):
        self.name = name
        self.api_key = api_key
        self.delay_range = delay_range
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'BusinessDistrict/1.0.0',
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        self.session.headers.update(self.headers)
        
    def random_delay(self):
        """随机延时，避免请求过于频繁"""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
        
    def make_request(self, url: str, method: str = 'GET', **kwargs) -> requests.Response:
        """发送HTTP请求，包含重试机制"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.request(method, url, timeout=30, **kwargs)
                response.raise_for_status()
                self.random_delay()
                return response
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"API请求失败 {url} (尝试 {max_retries} 次): {str(e)}")
                    raise
                else:
                    logger.warning(f"API请求失败 {url} (第 {attempt + 1} 次尝试): {str(e)}")
                    time.sleep(1)  # 重试前等待1秒
            
    @abstractmethod
    def get_business_areas(self, city_id: str, city_name: str) -> List[Dict[str, Any]]:
        """获取商圈数据"""
        pass
        
    @abstractmethod
    def get_stores(self, area_id: str, area_name: str, area_lat: float, area_lng: float) -> List[Dict[str, Any]]:
        """获取店铺数据"""
        pass
        
    def validate_data(self, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """验证数据完整性"""
        for field in required_fields:
            if field not in data or data[field] is None:
                logger.warning(f"数据缺失字段: {field}")
                return False
        return True
        
    def clean_text(self, text: str) -> str:
        """清理文本数据"""
        if not text:
            return ""
        return text.strip().replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        
    def parse_coordinate(self, coord_str: str) -> Optional[float]:
        """解析坐标字符串"""
        try:
            return float(coord_str)
        except (ValueError, TypeError):
            return None
            
    def test_connection(self) -> Dict[str, Any]:
        """测试API连接"""
        try:
            # 子类应该重写此方法实现具体的连接测试
            return {'status': 'ok', 'message': 'API客户端连接正常'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
            
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
