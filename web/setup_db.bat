@echo off
echo 正在设置数据库...
echo.

REM 设置环境变量
set FLASK_APP=app.py
set FLASK_ENV=development

echo 1. 初始化Flask-Migrate...
flask db init

echo.
echo 2. 生成迁移脚本...
flask db migrate -m "Initial migration - 创建所有表"

echo.
echo 3. 执行数据库迁移...
flask db upgrade

echo.
echo 4. 运行初始化脚本插入初始数据...
python init_db.py

echo.
echo 数据库设置完成！
pause
