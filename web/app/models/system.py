#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统相关数据模型
"""

from datetime import datetime
from app.extensions import db
import json

class SystemConfig(db.Model):
    """系统配置模型"""
    __tablename__ = 'system_config'
    
    id = db.Column(db.Integer, primary_key=True)
    config_key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    config_value = db.Column(db.Text, nullable=True)
    config_type = db.Column(db.Enum('string', 'integer', 'float', 'boolean', 'json', name='config_type_enum'), default='string')
    description = db.Column(db.Text, nullable=True)
    is_public = db.Column(db.Boolean, default=False, index=True)  # 是否公开（前端可访问）
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_value(self):
        """根据类型获取配置值"""
        if not self.config_value:
            return None
        
        try:
            if self.config_type == 'integer':
                return int(self.config_value)
            elif self.config_type == 'float':
                return float(self.config_value)
            elif self.config_type == 'boolean':
                return self.config_value.lower() in ('true', '1', 'yes', 'on')
            elif self.config_type == 'json':
                return json.loads(self.config_value)
            else:  # string
                return self.config_value
        except (ValueError, json.JSONDecodeError):
            return self.config_value
    
    def set_value(self, value):
        """设置配置值"""
        if self.config_type == 'json':
            self.config_value = json.dumps(value) if value is not None else None
        else:
            self.config_value = str(value) if value is not None else None
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'config_key': self.config_key,
            'config_value': self.get_value(),
            'config_type': self.config_type,
            'description': self.description,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<SystemConfig {self.config_key}>'


class CrawlRecord(db.Model):
    """数据爬取记录模型"""
    __tablename__ = 'crawl_records'
    
    id = db.Column(db.Integer, primary_key=True)
    target_type = db.Column(db.Enum('business_area', 'store', 'city', name='crawl_target_enum'), nullable=False, index=True)
    target_id = db.Column(db.String(50), nullable=False, index=True)
    source = db.Column(db.Enum('dianping', 'meituan', 'amap', 'baidu', name='crawl_source_enum'), nullable=False, index=True)
    
    # 爬取状态
    status = db.Column(db.Enum('pending', 'running', 'success', 'failed', name='crawl_status_enum'), default='pending', index=True)
    error_message = db.Column(db.Text, nullable=True)
    
    # 爬取统计
    items_crawled = db.Column(db.Integer, default=0)  # 爬取条目数
    items_saved = db.Column(db.Integer, default=0)  # 保存条目数
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    duration = db.Column(db.Integer, nullable=True)  # 耗时（秒）
    
    # 爬取配置
    config = db.Column(db.Text, nullable=True)  # JSON配置
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_config(self):
        """获取爬取配置"""
        if self.config:
            try:
                return json.loads(self.config)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    def set_config(self, config_dict):
        """设置爬取配置"""
        if config_dict:
            self.config = json.dumps(config_dict)
        else:
            self.config = None
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'source': self.source,
            'status': self.status,
            'error_message': self.error_message,
            'items_crawled': self.items_crawled,
            'items_saved': self.items_saved,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'config': self.get_config(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<CrawlRecord {self.target_type}:{self.target_id}>'


class UserFavorite(db.Model):
    """用户收藏模型"""
    __tablename__ = 'user_favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    target_type = db.Column(db.Enum('business_area', 'store', name='favorite_target_enum'), nullable=False, index=True)
    target_id = db.Column(db.String(50), nullable=False, index=True)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # 唯一约束（用户不能重复收藏同一个对象）
    __table_args__ = (
        db.UniqueConstraint('user_id', 'target_type', 'target_id', name='uk_user_favorites'),
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<UserFavorite {self.user_id}:{self.target_type}:{self.target_id}>'


class SearchHistory(db.Model):
    """搜索历史模型"""
    __tablename__ = 'search_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    session_id = db.Column(db.String(100), nullable=True, index=True)
    
    # 搜索信息
    search_type = db.Column(db.Enum('keyword', 'location', 'area', name='search_type_enum'), nullable=False, index=True)
    search_query = db.Column(db.Text, nullable=False)
    search_params = db.Column(db.Text, nullable=True)  # JSON搜索参数
    
    # 搜索结果
    result_count = db.Column(db.Integer, default=0)
    click_position = db.Column(db.Integer, nullable=True)  # 点击位置
    clicked_target_id = db.Column(db.String(50), nullable=True)  # 点击的目标ID
    
    # 位置信息
    longitude = db.Column(db.Float, nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    city_id = db.Column(db.String(20), db.ForeignKey('cities.id'), nullable=True, index=True)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def get_search_params(self):
        """获取搜索参数"""
        if self.search_params:
            try:
                return json.loads(self.search_params)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    def set_search_params(self, params_dict):
        """设置搜索参数"""
        if params_dict:
            self.search_params = json.dumps(params_dict)
        else:
            self.search_params = None
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'search_type': self.search_type,
            'search_query': self.search_query,
            'search_params': self.get_search_params(),
            'result_count': self.result_count,
            'click_position': self.click_position,
            'clicked_target_id': self.clicked_target_id,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'city_id': self.city_id,
            'city_name': self.city.name if hasattr(self, 'city') and self.city else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<SearchHistory {self.search_type}:{self.search_query}>'
