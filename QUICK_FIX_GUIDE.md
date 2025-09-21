# 快速修复指南

## 问题总结

刚刚修复了以下问题：
1. ✅ 后端Python依赖问题（移除了retrying依赖）
2. ✅ CORS跨域问题（配置了开发环境CORS）
3. ✅ 百度地图API密钥问题（添加了占位符处理）

## 快速启动步骤

### 1. 启动后端服务

```bash
# 进入后端目录
cd web

# 使用新的开发启动脚本（推荐）
python run_dev.py

# 或者使用原始启动方式
python app.py
```

### 2. 启动前端服务

```bash
# 在项目根目录
npm run dev
```

### 3. 验证服务状态

- 后端健康检查: http://localhost:3000/api/health
- 前端访问: http://localhost:5173
- API文档: http://localhost:3000/api/docs

## 已修复的具体问题

### 1. Python依赖问题
- **问题**: `ModuleNotFoundError: No module named 'retrying'`
- **解决**: 移除了retrying依赖，使用内置重试机制
- **文件**: `web/app/data_sources/base_client.py`

### 2. CORS跨域问题
- **问题**: `Access-Control-Allow-Origin header is not present`
- **解决**: 创建了新的开发启动脚本，配置了完整的CORS支持
- **文件**: `web/run_dev.py`

### 3. 百度地图API问题
- **问题**: API密钥配置错误导致地图初始化失败
- **解决**: 添加了API密钥检查和占位符显示
- **文件**: `src/components/BaiduMap.vue`, `src/config/env.js`

## 配置百度地图API（可选）

如果你有百度地图API密钥，可以按以下步骤配置：

1. 打开 `src/config/env.js`
2. 找到 `BAIDU_MAP_CONFIG.ak` 字段
3. 替换为你的API密钥：

```javascript
BAIDU_MAP_CONFIG: {
  ak: '你的百度地图API密钥',
  // ... 其他配置
}
```

如果没有API密钥，系统会显示占位符，不影响其他功能的使用。

## 测试数据

后端启动时会自动初始化以下城市数据：
- 北京
- 上海  
- 广州
- 深圳
- 杭州

## 故障排除

### 如果后端仍然无法启动：

1. 检查Python版本（建议Python 3.8+）
2. 安装依赖：
   ```bash
   cd web
   pip install -r requirements.txt
   ```
3. 检查端口3000是否被占用

### 如果前端无法连接后端：

1. 确认后端服务已启动（访问 http://localhost:3000/api/health）
2. 检查浏览器控制台是否有CORS错误
3. 确认前端配置中的API地址正确（http://localhost:3000/api）

### 如果地图不显示：

1. 这是正常的，因为没有配置百度地图API密钥
2. 地图会显示占位符，其他功能不受影响
3. 如需使用地图功能，请配置有效的百度地图API密钥

## 下一步

现在系统应该能够正常启动了。你可以：

1. 访问前端界面测试城市选择功能
2. 使用数据源API获取商圈数据
3. 根据需要配置百度地图API密钥

如果还有问题，请检查浏览器控制台和后端日志输出。
