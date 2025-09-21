#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
城市数据模型
"""

from datetime import datetime
from app.extensions import db

class City(db.Model):
    """城市模型"""
    __tablename__ = 'cities'
    
    id = db.Column(db.String(20), primary_key=True)  # 城市代码
    name = db.Column(db.String(50), nullable=False, index=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    level = db.Column(db.Enum('province', 'city', 'district', name='level_enum'), nullable=False, index=True)
    parent_id = db.Column(db.String(20), db.ForeignKey('cities.id'), nullable=True)
    
    # 地理信息
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    
    # 城市信息
    population = db.Column(db.Integer, nullable=True)  # 人口数量
    area = db.Column(db.Float, nullable=True)  # 面积（平方公里）
    economic_level = db.Column(db.Enum('high', 'medium', 'low', name='economic_enum'), default='medium')
    is_hot = db.Column(db.Boolean, default=False)  # 是否为热门城市
    
    # 拼音信息（用于搜索）
    pinyin = db.Column(db.String(100), nullable=True, index=True)
    pinyin_abbr = db.Column(db.String(10), nullable=True, index=True)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    children = db.relationship('City', backref=db.backref('parent', remote_side=[id]))
    business_areas = db.relationship('BusinessArea', backref='city', lazy='dynamic')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'level': self.level,
            'parent_id': self.parent_id,
            'parentName': self.parent.name if self.parent else None,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'population': self.population,
            'area': self.area,
            'economic_level': self.economic_level,
            'is_hot': self.is_hot,
            'pinyin': self.pinyin,
            'pinyin_abbr': self.pinyin_abbr,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<City {self.name}>'
