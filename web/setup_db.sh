#!/bin/bash
echo "正在设置数据库..."
echo

# 设置环境变量
export FLASK_APP=app.py
export FLASK_ENV=development

echo "1. 初始化Flask-Migrate..."
flask db init

echo
echo "2. 生成迁移脚本..."
flask db migrate -m "Initial migration - 创建所有表"

echo
echo "3. 执行数据库迁移..."
flask db upgrade

echo
echo "4. 运行初始化脚本插入初始数据..."
python init_db.py

echo
echo "数据库设置完成！"
