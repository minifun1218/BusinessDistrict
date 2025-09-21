#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商圈数据模型
"""

from datetime import datetime
from app.extensions import db

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
    
    # 基本信息
    address = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    opening_hours = db.Column(db.String(100), nullable=True)
    
    # JSON字段
    facilities = db.Column(db.JSON, nullable=True)  # 配套设施
    transportation = db.Column(db.JSON, nullable=True)  # 交通信息
    images = db.Column(db.JSON, nullable=True)  # 图片列表
    tags = db.Column(db.JSON, nullable=True)  # 标签
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    stores = db.relationship('Store', backref='business_area', lazy='dynamic')
    
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
            'address': self.address,
            'description': self.description,
            'opening_hours': self.opening_hours,
            'facilities': self.facilities or [],
            'transportation': self.transportation or [],
            'images': self.images or [],
            'tags': self.tags or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<BusinessArea {self.name}>'

class Store(db.Model):
    """店铺模型"""
    __tablename__ = 'stores'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    business_area_id = db.Column(db.String(50), db.ForeignKey('business_areas.id'), 
                                nullable=False, index=True)
    
    # 店铺分类
    category = db.Column(db.Enum('restaurant', 'retail', 'entertainment', 'service', 
                                name='store_category_enum'), nullable=False, index=True)
    sub_category = db.Column(db.String(50), nullable=True, index=True)
    
    # 地理信息
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    
    # 店铺数据
    rating = db.Column(db.Float, default=0.0, index=True)
    review_count = db.Column(db.Integer, default=0)
    avg_price = db.Column(db.Float, default=0.0)
    
    # 基本信息
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    opening_hours = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    # JSON字段
    images = db.Column(db.JSON, nullable=True)
    tags = db.Column(db.JSON, nullable=True)
    facilities = db.Column(db.JSON, nullable=True)
    
    # 推荐状态
    is_recommended = db.Column(db.Boolean, default=False, index=True)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'business_area_id': self.business_area_id,
            'businessAreaName': self.business_area.name if self.business_area else None,
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
            'images': self.images or [],
            'tags': self.tags or [],
            'facilities': self.facilities or [],
            'is_recommended': self.is_recommended,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Store {self.name}>'
