#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证相关API接口
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User
from app.utils.auth import hash_password, check_password, validate_email, validate_phone
from app.utils.response import success_response, error_response

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 400)
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        remember = data.get('remember', False)
        
        if not username or not password:
            return error_response('用户名和密码不能为空', 400)
        
        # 查找用户（支持用户名、邮箱、手机号登录）
        user = User.query.filter(
            (User.username == username) | 
            (User.email == username) | 
            (User.phone == username)
        ).first()
        
        if not user:
            return error_response('用户不存在', 404)
        
        if not user.is_active:
            return error_response('账户已被禁用', 403)
        
        # 验证密码
        if not check_password(password, user.password_hash):
            return error_response('密码错误', 401)
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # 生成JWT令牌
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return success_response({
            'accessToken': access_token,
            'refreshToken': refresh_token,
            'tokenType': 'Bearer',
            'expiresIn': 86400,  # 24小时
            'user': user.to_dict()
        }, '登录成功')
        
    except Exception as e:
        return error_response(f'登录失败: {str(e)}', 500)

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 400)
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirmPassword', '')
        
        # 验证必填字段
        if not all([username, email, password]):
            return error_response('用户名、邮箱和密码不能为空', 400)
        
        # 验证密码一致性
        if password != confirm_password:
            return error_response('两次输入的密码不一致', 400)
        
        # 验证密码长度
        if len(password) < 6:
            return error_response('密码长度至少为6位', 400)
        
        # 验证邮箱格式
        if not validate_email(email):
            return error_response('邮箱格式不正确', 400)
        
        # 验证手机号格式（如果提供）
        if phone and not validate_phone(phone):
            return error_response('手机号格式不正确', 400)
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return error_response('用户名已存在', 409)
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            return error_response('邮箱已被注册', 409)
        
        # 检查手机号是否已存在（如果提供）
        if phone and User.query.filter_by(phone=phone).first():
            return error_response('手机号已被注册', 409)
        
        # 创建新用户
        user = User(
            username=username,
            email=email,
            phone=phone if phone else None,
            password_hash=hash_password(password),
            nickname=username,
            is_active=True
        )
        
        db.session.add(user)
        db.session.commit()
        
        return success_response({
            'user': user.to_dict()
        }, '注册成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'注册失败: {str(e)}', 500)

@auth_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_info():
    """获取用户信息"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return error_response('用户不存在', 404)
        
        return success_response(user.to_dict(), '获取用户信息成功')
        
    except Exception as e:
        return error_response(f'获取用户信息失败: {str(e)}', 500)

@auth_bp.route('/user', methods=['PUT'])
@jwt_required()
def update_user_info():
    """更新用户信息"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return error_response('用户不存在', 404)
        
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 400)
        
        # 可更新的字段
        updatable_fields = ['nickname', 'avatar', 'gender', 'age', 'city']
        
        for field in updatable_fields:
            if field in data:
                setattr(user, field, data[field])
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return success_response(user.to_dict(), '用户信息更新成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新用户信息失败: {str(e)}', 500)

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """刷新访问令牌"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            return error_response('用户不存在或已被禁用', 404)
        
        # 生成新的访问令牌
        access_token = create_access_token(identity=str(user.id))
        
        return success_response({
            'accessToken': access_token,
            'tokenType': 'Bearer',
            'expiresIn': 86400
        }, '令牌刷新成功')
        
    except Exception as e:
        return error_response(f'令牌刷新失败: {str(e)}', 500)

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户退出登录"""
    try:
        # 在实际应用中，这里可以将令牌加入黑名单
        # 目前只是返回成功响应
        return success_response(None, '退出登录成功')
        
    except Exception as e:
        return error_response(f'退出登录失败: {str(e)}', 500)

@auth_bp.route('/password', methods=['PUT'])
@jwt_required()
def change_password():
    """修改密码"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return error_response('用户不存在', 404)
        
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 400)
        
        old_password = data.get('oldPassword', '')
        new_password = data.get('newPassword', '')
        confirm_password = data.get('confirmPassword', '')
        
        if not all([old_password, new_password, confirm_password]):
            return error_response('所有密码字段都不能为空', 400)
        
        # 验证旧密码
        if not check_password(old_password, user.password_hash):
            return error_response('原密码错误', 401)
        
        # 验证新密码一致性
        if new_password != confirm_password:
            return error_response('两次输入的新密码不一致', 400)
        
        # 验证新密码长度
        if len(new_password) < 6:
            return error_response('新密码长度至少为6位', 400)
        
        # 更新密码
        user.password_hash = hash_password(new_password)
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return success_response(None, '密码修改成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'密码修改失败: {str(e)}', 500)