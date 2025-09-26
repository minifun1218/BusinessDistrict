#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型模块
"""

# 导入所有模型，确保Flask-Migrate能够发现它们
from .city import City
from .business_area import BusinessArea
from .store import Store
from .user import User
from .review import AreaReview, StoreReview
from .system import SystemConfig, CrawlRecord, UserFavorite, SearchHistory

# 导出所有模型
__all__ = [
    'City',
    'BusinessArea', 
    'Store',
    'User',
    'AreaReview',
    'StoreReview',
    'SystemConfig',
    'CrawlRecord',
    'UserFavorite',
    'SearchHistory'
]
