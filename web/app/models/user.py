#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户数据模型
"""

from datetime import datetime
from app.extensions import db

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # 用户信息
    nickname = db.Column(db.String(80), nullable=True)
    avatar = db.Column(db.String(255), nullable=True)
    gender = db.Column(db.Enum('male', 'female', 'unknown', name='gender_enum'), default='unknown')
    age = db.Column(db.Integer, nullable=True)
    city = db.Column(db.String(50), nullable=True)
    
    # 用户状态
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    vip_level = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'nickname': self.nickname,
            'avatar': self.avatar,
            'gender': self.gender,
            'age': self.age,
            'city': self.city,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'vip_level': self.vip_level,
            'points': self.points,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'
