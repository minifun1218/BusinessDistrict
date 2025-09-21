#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫基类 - 定义通用的爬虫接口和功能
"""

import time
import random
import logging
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from fake_useragent import UserAgent
from retrying import retry

logger = logging.getLogger(__name__)

class BaseCrawler(ABC):
    """爬虫基类"""
    
    def __init__(self, name: str, delay_range: tuple = (1, 3)):
        self.name = name
        self.delay_range = delay_range
        self.ua = UserAgent()
        self.session = requests.Session()
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        self.session.headers.update(self.headers)
        
    def random_delay(self):
        """随机延时，避免被反爬"""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
        
    def update_user_agent(self):
        """更新User-Agent"""
        self.session.headers.update({'User-Agent': self.ua.random})
        
    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def make_request(self, url: str, method: str = 'GET', **kwargs) -> requests.Response:
        """发送HTTP请求，包含重试机制"""
        try:
            self.update_user_agent()
            response = self.session.request(method, url, timeout=30, **kwargs)
            response.raise_for_status()
            self.random_delay()
            return response
        except Exception as e:
            logger.error(f"请求失败 {url}: {str(e)}")
            raise
            
    @abstractmethod
    def get_business_areas(self, city_id: str, city_name: str) -> List[Dict[str, Any]]:
        """获取商圈数据"""
        pass
        
    @abstractmethod
    def get_stores(self, area_id: str, area_name: str) -> List[Dict[str, Any]]:
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
            
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
