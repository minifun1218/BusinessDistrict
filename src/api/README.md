# API接口文档

本项目的API接口已经完整封装，支持城市商圈消费热度可视化分析系统的所有功能需求。

## 目录结构

```
src/
├── api/                    # API接口目录
│   ├── index.js           # 统一导出
│   ├── auth.js            # 认证相关接口
│   ├── city.js            # 城市相关接口
│   ├── business.js        # 商圈和店铺相关接口
│   └── analytics.js       # 数据分析相关接口
├── utils/
│   └── request.js         # HTTP请求工具类
├── types/
│   └── api.js             # API数据类型定义
└── config/
    └── env.js             # 环境配置
```

## 使用方式

### 1. 导入API

```javascript
// 方式1: 导入具体的API模块
import { authApi, cityApi, businessApi, analyticsApi } from '@/api'

// 方式2: 导入统一的API对象
import { api } from '@/api'
```

### 2. 调用示例

```javascript
// 用户登录
const loginResponse = await authApi.login({
  username: 'user@example.com',
  password: 'password123'
})

// 获取城市列表
const cities = await cityApi.getCityList()

// 获取商圈热度排行
const hotRanking = await analyticsApi.getHotRankingData('beijing')
```

## API接口分类

### 认证接口 (authApi)

| 方法 | 描述 | 参数 |
|------|------|------|
| `login(params)` | 用户登录 | username, password, remember |
| `register(params)` | 用户注册 | username, email, phone, password |
| `logout()` | 退出登录 | - |
| `getUserInfo()` | 获取用户信息 | - |
| `refreshToken(token)` | 刷新访问令牌 | refreshToken |

### 城市接口 (cityApi)

| 方法 | 描述 | 参数 |
|------|------|------|
| `getCityList(params)` | 获取城市列表 | level, page, pageSize |
| `getHotCities()` | 获取热门城市 | - |
| `getCityById(id)` | 获取城市详情 | cityId |
| `searchCities(keyword)` | 搜索城市 | keyword |
| `getCityByLocation(lng, lat)` | 根据坐标获取城市 | longitude, latitude |

### 商圈接口 (businessApi)

| 方法 | 描述 | 参数 |
|------|------|------|
| `getBusinessAreas(params)` | 获取商圈列表 | cityId, type, page, pageSize |
| `getBusinessAreaById(id)` | 获取商圈详情 | areaId |
| `searchBusinessAreas(params)` | 搜索商圈 | keyword, cityId, type |
| `getHotRanking(cityId)` | 获取商圈热度排行 | cityId, limit |

### 数据分析接口 (analyticsApi)

| 方法 | 描述 | 参数 |
|------|------|------|
| `getCityAnalytics(cityId)` | 获取城市整体数据 | cityId, dateRange |
| `getHotRankingData(cityId)` | 获取热度排行数据 | cityId, limit |
| `getHourlyFlowData(cityId)` | 获取24小时客流数据 | cityId, date |
| `getCategoryDistribution(cityId)` | 获取消费类型分布 | cityId, dateRange |
| `getSentimentAnalysis(cityId)` | 获取情感分析数据 | cityId, dateRange |
| `getConsumptionTrend(cityId)` | 获取消费趋势数据 | cityId, dateRange |
| `getHeatmapData(cityId)` | 获取热力图数据 | cityId, zoom |

## 请求配置

### 基础配置

- **基础URL**: `http://localhost:3000/api` (可通过环境变量配置)
- **请求超时**: 15秒
- **请求格式**: JSON
- **认证方式**: Bearer Token

### 请求拦截器

自动添加以下功能：
- 自动添加Authorization头部
- 防缓存时间戳
- 全局loading状态管理
- 请求日志记录

### 响应拦截器

自动处理以下情况：
- 统一响应格式解析
- HTTP状态码错误处理
- 401未授权自动跳转
- 网络错误提示
- 业务错误统一处理

## 错误处理

### HTTP状态码处理

| 状态码 | 说明 | 处理方式 |
|--------|------|----------|
| 400 | 请求参数错误 | 显示错误信息 |
| 401 | 未授权 | 清除token，跳转登录 |
| 403 | 拒绝访问 | 显示权限不足提示 |
| 404 | 资源不存在 | 显示资源不存在提示 |
| 429 | 请求过频 | 显示限流提示 |
| 500+ | 服务器错误 | 显示服务器错误提示 |

### 业务错误处理

```javascript
try {
  const data = await authApi.login(loginForm)
  // 处理成功逻辑
} catch (error) {
  // error.message: 错误信息
  // error.code: 业务错误码
  // error.status: HTTP状态码
  console.error('登录失败:', error.message)
}
```

## 数据格式

### 标准响应格式

```javascript
{
  "code": 200,           // 业务状态码
  "message": "success",  // 响应消息
  "data": {...},         // 响应数据
  "timestamp": 1234567890 // 时间戳
}
```

### 分页响应格式

```javascript
{
  "list": [...],         // 数据列表
  "total": 100,          // 总数量
  "page": 1,             // 当前页
  "pageSize": 20,        // 每页大小
  "totalPages": 5,       // 总页数
  "hasNext": true,       // 是否有下一页
  "hasPrev": false       // 是否有上一页
}
```

## 环境配置

在 `src/config/env.js` 中配置不同环境的参数：

```javascript
export const ENV_CONFIG = {
  API_BASE_URL: 'http://localhost:3000/api',
  REQUEST_TIMEOUT: 15000,
  DEBUG: true,
  // ... 其他配置
}
```

## 开发建议

1. **API调用位置**: 建议在组件的方法中调用API，避免在计算属性中调用
2. **错误处理**: 每个API调用都应该有适当的错误处理
3. **加载状态**: 对于耗时的API调用，应该显示加载状态
4. **数据缓存**: 对于不经常变化的数据，可以考虑缓存策略
5. **请求取消**: 对于可能被中断的请求，使用CancelToken进行取消

## 扩展API

如需添加新的API接口：

1. 在对应的API文件中添加方法
2. 在 `src/api/index.js` 中导出
3. 在类型定义文件中添加相应的类型
4. 更新本文档

## 测试

建议使用以下工具进行API测试：
- Postman
- Insomnia
- 浏览器开发者工具
- Jest单元测试
