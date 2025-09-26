#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商圈数据模型
"""

from datetime import datetime
from app.extensions import db
import json

class BusinessArea(db.Model):
    """商圈模型"""
    __tablename__ = 'business_areas'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    city_id = db.Column(db.String(20), db.ForeignKey('cities.id'), nullable=False, index=True)
    
    # 商圈分类
    type = db.Column(db.Enum('shopping', 'dining', 'entertainment', 'mixed', name='area_type_enum'), 
                    default='mixed', index=True)
    level = db.Column(db.Enum('A', 'B', 'C', 'D', name='area_level_enum'), default='C', index=True)
    
    # 地理信息
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    area = db.Column(db.Float, nullable=True)  # 面积（平方公里）
    
    # 商圈数据
    hot_value = db.Column(db.Integer, default=0, index=True)  # 热度值
    avg_consumption = db.Column(db.Float, default=0.0)  # 平均消费
    customer_flow = db.Column(db.Integer, default=0)  # 日均客流量
    store_count = db.Column(db.Integer, default=0)  # 店铺数量
    rating = db.Column(db.Float, default=0.0)  # 评分
    review_count = db.Column(db.Integer, default=0)  # 评价数量
    
    # 基本信息
    address = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    opening_hours = db.Column(db.String(100), nullable=True)
    
    # JSON字段（SQLite兼容）
    facilities = db.Column(db.Text, nullable=True)  # 配套设施JSON
    transportation = db.Column(db.Text, nullable=True)  # 交通信息JSON
    images = db.Column(db.Text, nullable=True)  # 图片列表JSON
    tags = db.Column(db.Text, nullable=True)  # 标签JSON
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    stores = db.relationship('Store', backref='business_area', lazy='dynamic', cascade='all, delete-orphan')
    area_reviews = db.relationship('AreaReview', backref='business_area', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        """初始化方法，处理JSON字段"""
        # 处理JSON字段
        json_fields = ['facilities', 'transportation', 'images', 'tags']
        json_values = {}
        
        # 提取JSON字段的值，包括空列表
        for field in json_fields:
            if field in kwargs:
                value = kwargs[field]
                if isinstance(value, (list, dict)) or value is None:
                    json_values[field] = kwargs.pop(field)
        
        # 调用父类初始化
        super().__init__(**kwargs)
        
        # 设置JSON字段
        for field, value in json_values.items():
            getattr(self, f'set_{field}')(value)
    
    def get_facilities(self):
        """获取设施信息"""
        if self.facilities:
            try:
                return json.loads(self.facilities)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    def set_facilities(self, facilities_list):
        """设置设施信息"""
        if facilities_list is not None:
            self.facilities = json.dumps(facilities_list)
        else:
            self.facilities = None
    
    def get_transportation(self):
        """获取交通信息"""
        if self.transportation:
            try:
                return json.loads(self.transportation)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    def set_transportation(self, transportation_list):
        """设置交通信息"""
        if transportation_list is not None:
            self.transportation = json.dumps(transportation_list)
        else:
            self.transportation = None
    
    def get_images(self):
        """获取图片列表"""
        if self.images:
            try:
                return json.loads(self.images)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    def set_images(self, images_list):
        """设置图片列表"""
        if images_list is not None:
            self.images = json.dumps(images_list)
        else:
            self.images = None
    
    def get_tags(self):
        """获取标签列表"""
        if self.tags:
            try:
                return json.loads(self.tags)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    def set_tags(self, tags_list):
        """设置标签列表"""
        if tags_list is not None:
            self.tags = json.dumps(tags_list)
        else:
            self.tags = None
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'city_id': self.city_id,
            'cityName': self.city.name if self.city else None,
            'type': self.type,
            'level': self.level,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'area': self.area,
            'hot_value': self.hot_value,
            'hotValue': self.hot_value,  # 前端兼容
            'avg_consumption': self.avg_consumption,
            'customer_flow': self.customer_flow,
            'store_count': self.store_count,
            'rating': self.rating,
            'review_count': self.review_count,
            'address': self.address,
            'description': self.description,
            'opening_hours': self.opening_hours,
            'facilities': self.get_facilities(),
            'transportation': self.get_transportation(),
            'images': self.get_images(),
            'tags': self.get_tags(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<BusinessArea {self.name}>'
