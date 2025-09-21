#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速修复脚本 - 解决当前的启动问题
"""

import os
import sys
import subprocess

def fix_backend_issues():
    """修复后端问题"""
    print("🔧 修复后端问题...")
    
    # 1. 初始化数据库和基础数据
    print("1. 初始化数据库...")
    try:
        os.chdir('web')
        result = subprocess.run([sys.executable, 'init_data.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ 数据库初始化成功")
        else:
            print(f"   ❌ 数据库初始化失败: {result.stderr}")
    except Exception as e:
        print(f"   ❌ 初始化过程出错: {str(e)}")
    
    # 2. 测试后端启动
    print("2. 测试后端启动...")
    try:
        result = subprocess.run([sys.executable, '-c', 
                               "from app import create_app; app = create_app(); print('后端启动测试成功')"], 
                              capture_output=True, text=True, cwd='web')
        if result.returncode == 0:
            print("   ✅ 后端启动测试成功")
        else:
            print(f"   ❌ 后端启动测试失败: {result.stderr}")
    except Exception as e:
        print(f"   ❌ 测试过程出错: {str(e)}")
    
    os.chdir('..')

def check_frontend_config():
    """检查前端配置"""
    print("\n🔧 检查前端配置...")
    
    # 检查API配置
    try:
        with open('src/config/env.js', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'localhost:3000' in content:
                print("   ✅ API地址配置正确")
            else:
                print("   ⚠️  请检查API地址配置")
    except Exception as e:
        print(f"   ❌ 读取配置文件失败: {str(e)}")

def provide_solutions():
    """提供解决方案"""
    print("\n📋 解决方案:")
    print("1. 启动后端服务:")
    print("   cd web")
    print("   python start_server.py")
    print()
    print("2. 或者直接运行:")
    print("   cd web")
    print("   python app.py")
    print()
    print("3. 启动前端服务:")
    print("   npm run dev")
    print()
    print("4. 检查服务状态:")
    print("   后端: http://localhost:3000/api/health")
    print("   前端: http://localhost:5173")
    print()
    print("5. 如果仍有问题，请检查:")
    print("   - 端口3000是否被占用")
    print("   - 防火墙设置")
    print("   - 网络连接")

def main():
    """主函数"""
    print("🚀 开始修复项目问题...")
    
    # 修复后端问题
    fix_backend_issues()
    
    # 检查前端配置
    check_frontend_config()
    
    # 提供解决方案
    provide_solutions()
    
    print("\n✨ 修复完成！请按照上述步骤启动服务。")

if __name__ == '__main__':
    main()
