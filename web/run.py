#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask应用启动脚本
"""

import os
import sys

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from app import create_app
    
    # 创建Flask应用
    app = create_app()
    
    if __name__ == '__main__':
        # 环境变量配置
        debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
        port = int(os.environ.get('PORT', 3000))
        host = os.environ.get('HOST', '127.0.0.1')
        
        print("=" * 60)
        print("🚀 城市商圈消费热度分析API服务")
        print("=" * 60)
        print(f"📍 服务地址: http://{host}:{port}")
        print(f"🔧 调试模式: {'开启' if debug_mode else '关闭'}")
        print(f"🌐 CORS支持: 已启用")
        print(f"📚 API文档: http://{host}:{port}/api/docs")
        print(f"💚 健康检查: http://{host}:{port}/api/health")
        print("=" * 60)
        
        try:
            app.run(
                host=host,
                port=port,
                debug=debug_mode,
                threaded=True
            )
        except KeyboardInterrupt:
            print("\n👋 服务已停止")
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            sys.exit(1)

except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保已安装所有依赖: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ 应用创建失败: {e}")
    sys.exit(1)
