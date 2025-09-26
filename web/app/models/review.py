#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评价数据模型
"""

from datetime import datetime
from app.extensions import db
import json

class AreaReview(db.Model):
    """商圈评价模型"""
    __tablename__ = 'area_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    business_area_id = db.Column(db.String(50), db.ForeignKey('business_areas.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    user_name = db.Column(db.String(50), nullable=True)  # 用户昵称（匿名时使用）
    
    # 评价内容
    rating = db.Column(db.Integer, nullable=False, index=True)  # 评分 1-5
    title = db.Column(db.String(100), nullable=True)  # 评价标题
    content = db.Column(db.Text, nullable=False)  # 评价内容
    
    # 评价统计
    helpful_count = db.Column(db.Integer, default=0)  # 有用数
    images = db.Column(db.Text, nullable=True)  # 评价图片JSON
    
    # 评价来源
    source = db.Column(db.Enum('dianping', 'meituan', 'manual', 'system', name='review_source_enum'), default='manual', index=True)
    external_id = db.Column(db.String(100), nullable=True)  # 外部评价ID
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 检查约束
    __table_args__ = (
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )
    
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
        if images_list:
            self.images = json.dumps(images_list)
        else:
            self.images = None
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'business_area_id': self.business_area_id,
            'business_area_name': self.business_area.name if hasattr(self, 'business_area') and self.business_area else None,
            'user_id': self.user_id,
            'user_name': self.user_name or (self.user.nickname if self.user else None),
            'rating': self.rating,
            'title': self.title,
            'content': self.content,
            'helpful_count': self.helpful_count,
            'images': self.get_images(),
            'source': self.source,
            'external_id': self.external_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<AreaReview {self.id}>'


class StoreReview(db.Model):
    """店铺评价模型"""
    __tablename__ = 'store_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.String(50), db.ForeignKey('stores.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    user_name = db.Column(db.String(50), nullable=True)  # 用户昵称
    
    # 评价内容
    rating = db.Column(db.Integer, nullable=False, index=True)  # 评分 1-5
    title = db.Column(db.String(100), nullable=True)  # 评价标题
    content = db.Column(db.Text, nullable=False)  # 评价内容
    
    # 评价统计
    helpful_count = db.Column(db.Integer, default=0)  # 有用数
    images = db.Column(db.Text, nullable=True)  # 评价图片JSON
    
    # 评价来源
    source = db.Column(db.Enum('dianping', 'meituan', 'manual', 'system', name='store_review_source_enum'), default='manual', index=True)
    external_id = db.Column(db.String(100), nullable=True)  # 外部评价ID
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 检查约束
    __table_args__ = (
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='check_store_rating_range'),
    )
    
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
        if images_list:
            self.images = json.dumps(images_list)
        else:
            self.images = None
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'store_id': self.store_id,
            'store_name': self.store.name if hasattr(self, 'store') and self.store else None,
            'user_id': self.user_id,
            'user_name': self.user_name or (self.user.nickname if self.user else None),
            'rating': self.rating,
            'title': self.title,
            'content': self.content,
            'helpful_count': self.helpful_count,
            'images': self.get_images(),
            'source': self.source,
            'external_id': self.external_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<StoreReview {self.id}>'
