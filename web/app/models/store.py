#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
店铺数据模型
"""

from datetime import datetime
from app.extensions import db
import json

class Store(db.Model):
    """店铺模型"""
    __tablename__ = 'stores'
    
    id = db.Column(db.String(50), primary_key=True)  # 店铺唯一标识
    name = db.Column(db.String(100), nullable=False, index=True)  # 店铺名称
    business_area_id = db.Column(db.String(50), db.ForeignKey('business_areas.id'), nullable=False, index=True)
    
    # 店铺分类
    category = db.Column(db.Enum('restaurant', 'retail', 'entertainment', 'service', name='store_category_enum'), nullable=False, index=True)
    sub_category = db.Column(db.String(50), nullable=True, index=True)  # 子分类
    
    # 地理信息
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    
    # 店铺数据
    rating = db.Column(db.Float, default=0.0, index=True)  # 评分 (0-5)
    review_count = db.Column(db.Integer, default=0)  # 评价数量
    avg_price = db.Column(db.Float, default=0.0, index=True)  # 平均消费价格
    
    # 基本信息
    phone = db.Column(db.String(20), nullable=True)  # 联系电话
    address = db.Column(db.String(255), nullable=True)  # 详细地址
    opening_hours = db.Column(db.String(100), nullable=True)  # 营业时间
    description = db.Column(db.Text, nullable=True)  # 店铺描述
    
    # JSON字段（SQLite兼容）
    images = db.Column(db.Text, nullable=True)  # 图片列表JSON
    tags = db.Column(db.Text, nullable=True)  # 标签JSON
    facilities = db.Column(db.Text, nullable=True)  # 设施信息JSON
    
    # 推荐状态
    is_recommended = db.Column(db.Boolean, default=False, index=True)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    reviews = db.relationship('StoreReview', backref='store', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        """初始化方法，处理JSON字段"""
        # 处理JSON字段
        json_fields = ['images', 'tags', 'facilities']
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
    
    def get_facilities(self):
        """获取设施信息"""
        if self.facilities:
            try:
                return json.loads(self.facilities)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    def set_facilities(self, facilities_dict):
        """设置设施信息"""
        if facilities_dict is not None:
            self.facilities = json.dumps(facilities_dict)
        else:
            self.facilities = None
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'business_area_id': self.business_area_id,
            'business_area_name': self.business_area.name if hasattr(self, 'business_area') and self.business_area else None,
            'category': self.category,
            'sub_category': self.sub_category,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'rating': self.rating,
            'review_count': self.review_count,
            'avg_price': self.avg_price,
            'phone': self.phone,
            'address': self.address,
            'opening_hours': self.opening_hours,
            'description': self.description,
            'images': self.get_images(),
            'tags': self.get_tags(),
            'facilities': self.get_facilities(),
            'is_recommended': self.is_recommended,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Store {self.name}>'
