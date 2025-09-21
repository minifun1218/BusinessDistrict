#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速启动服务脚本
"""

import os
import sys
import subprocess
import time
import requests

def check_port(port):
    """检查端口是否被占用"""
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('localhost', port))
            return result == 0
    except:
        return False

def start_backend():
    """启动后端服务"""
    print("🚀 启动后端服务...")
    
    # 检查端口3000是否被占用
    if check_port(3000):
        print("⚠️  端口3000已被占用，尝试访问现有服务...")
        try:
            response = requests.get('http://localhost:3000/api/health', timeout=5)
            if response.status_code == 200:
                print("✅ 后端服务已在运行")
                return True
            else:
                print("❌ 端口被其他程序占用")
                return False
        except:
            print("❌ 端口被其他程序占用")
            return False
    
    # 启动后端服务
    try:
        os.chdir('web')
        
        # 首先尝试运行开发脚本
        if os.path.exists('run_dev.py'):
            print("使用开发启动脚本...")
            subprocess.Popen([sys.executable, 'run_dev.py'])
        elif os.path.exists('app.py'):
            print("使用标准启动脚本...")
            subprocess.Popen([sys.executable, 'app.py'])
        else:
            print("❌ 找不到启动脚本")
            return False
        
        # 等待服务启动
        print("⏳ 等待后端服务启动...")
        for i in range(30):  # 等待30秒
            try:
                response = requests.get('http://localhost:3000/api/health', timeout=2)
                if response.status_code == 200:
                    print("✅ 后端服务启动成功")
                    return True
            except:
                pass
            time.sleep(1)
            print(f"   等待中... ({i+1}/30)")
        
        print("❌ 后端服务启动超时")
        return False
        
    except Exception as e:
        print(f"❌ 启动后端服务失败: {str(e)}")
        return False
    finally:
        os.chdir('..')

def main():
    """主函数"""
    print("🎯 快速启动服务脚本")
    print("=" * 50)
    
    # 启动后端
    backend_ok = start_backend()
    
    if backend_ok:
        print("\n✨ 启动完成！")
        print("📍 后端服务: http://localhost:3000")
        print("🏥 健康检查: http://localhost:3000/api/health")
        print("📚 API文档: http://localhost:3000/api/docs")
        print("\n📝 下一步:")
        print("1. 在另一个终端运行: npm run dev")
        print("2. 访问前端: http://localhost:5173")
        print("3. 如果地图有问题，这是正常的，其他功能不受影响")
    else:
        print("\n❌ 后端启动失败")
        print("请手动启动:")
        print("1. cd web")
        print("2. python run_dev.py")

if __name__ == '__main__':
    main()
