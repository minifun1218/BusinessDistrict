# 城市商圈消费热度可视化分析系统 - Flask API

基于Flask构建的城市商圈消费热度分析系统后端API服务。

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip 包管理器
- SQLite（默认）或 MySQL（可选）
- Redis（可选，用于缓存）

### 安装依赖

```bash
cd web
pip install -r requirements.txt
```

### 初始化数据库

```bash
python data/init_data.py
```

### 启动服务

```bash
# 方式1: 使用启动脚本
python run.py

# 方式2: 使用Flask命令
python app.py

# 方式3: 使用gunicorn（生产环境）
gunicorn -w 4 -b 127.0.0.1:3000 app:app
```

服务启动后访问：
- API服务：http://127.0.0.1:3000
- API文档：http://127.0.0.1:3000/api/docs
- 健康检查：http://127.0.0.1:3000/api/health

## 📁 项目结构

```
web/
├── app/                    # Flask应用主目录
│   ├── __init__.py        # 应用工厂函数
│   ├── extensions.py      # Flask扩展初始化
│   ├── api/               # API蓝图
│   │   ├── auth.py       # 认证接口
│   │   ├── cities.py     # 城市接口
│   │   ├── business.py   # 商圈接口
│   │   └── analytics.py  # 数据分析接口
│   ├── models/           # 数据模型
│   │   ├── user.py       # 用户模型
│   │   ├── city.py       # 城市模型
│   │   └── business_area.py # 商圈模型
│   └── utils/            # 工具函数
│       ├── response.py   # 响应格式化
│       └── auth.py       # 认证工具
├── config/               # 配置文件
│   └── config.py        # 应用配置
├── data/                # 数据文件
│   └── init_data.py     # 数据初始化脚本
├── static/              # 静态文件
├── templates/           # 模板文件
├── tests/               # 测试文件
├── app.py              # 应用入口
├── run.py              # 启动脚本
└── requirements.txt    # 依赖列表
```

## 🔌 API接口

### 认证接口 (/api/auth)

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/login` | 用户登录 |
| POST | `/register` | 用户注册 |
| GET | `/user` | 获取用户信息 |
| PUT | `/user` | 更新用户信息 |
| POST | `/refresh` | 刷新令牌 |
| POST | `/logout` | 退出登录 |
| PUT | `/password` | 修改密码 |

### 城市接口 (/api/cities)

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/` | 获取城市列表 |
| GET | `/hot` | 获取热门城市 |
| GET | `/{city_id}` | 获取城市详情 |
| GET | `/search` | 搜索城市 |
| GET | `/location` | 根据坐标获取城市 |
| GET | `/provinces` | 获取省份列表 |
| GET | `/{city_id}/stats` | 获取城市统计 |

### 商圈接口 (/api/business-areas)

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/` | 获取商圈列表 |
| GET | `/{area_id}` | 获取商圈详情 |
| GET | `/search` | 搜索商圈 |
| GET | `/hot-ranking` | 获取热度排行 |
| GET | `/{area_id}/stats` | 获取商圈统计 |
| GET | `/{area_id}/stores` | 获取商圈店铺 |
| POST | `/compare` | 商圈对比 |
| GET | `/nearby` | 获取附近商圈 |

### 数据分析接口 (/api/analytics)

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/city/{city_id}` | 获取城市分析数据 |
| GET | `/hot-ranking` | 获取热度排行数据 |
| GET | `/hourly-flow` | 获取24小时客流数据 |
| GET | `/category-distribution` | 获取消费类型分布 |
| GET | `/sentiment-analysis` | 获取情感分析数据 |
| GET | `/consumption-trend` | 获取消费趋势数据 |
| POST | `/radar-comparison` | 获取雷达图对比数据 |
| GET | `/heatmap` | 获取热力图数据 |
| GET | `/realtime/{city_id}` | 获取实时数据 |

## 📊 数据模型

### 用户模型 (User)
- 基本信息：用户名、邮箱、手机号
- 个人资料：昵称、头像、性别、年龄、城市
- 状态信息：激活状态、VIP等级、积分

### 城市模型 (City)
- 基本信息：名称、代码、级别（省/市/区）
- 地理信息：经纬度坐标
- 统计信息：人口、面积、经济水平

### 商圈模型 (BusinessArea)
- 基本信息：名称、类型、级别
- 地理信息：经纬度、面积
- 业务数据：热度值、平均消费、客流量、评分
- 扩展信息：配套设施、交通信息、标签

### 店铺模型 (Store)
- 基本信息：名称、分类、子分类
- 地理信息：经纬度
- 业务数据：评分、评价数、平均价格
- 联系信息：电话、地址、营业时间

## 🔧 配置说明

### 数据库配置

默认使用SQLite数据库，生产环境建议使用MySQL：

```python
# SQLite（默认）
DATABASE_URL = 'sqlite:///business_district.db'

# MySQL
DATABASE_URL = 'mysql+pymysql://username:password@localhost/business_district'
```

### JWT配置

```python
JWT_SECRET_KEY = 'your-jwt-secret-key'
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
```

### CORS配置

已配置允许前端跨域访问：

```python
CORS(app, 
     origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
     supports_credentials=True)
```

## 🧪 测试

### 测试账号

系统预置了以下测试账号：

- **管理员**: `admin` / `admin123`
- **演示用户**: `demo` / `demo123`

### API测试

使用curl测试API：

```bash
# 健康检查
curl http://127.0.0.1:3000/api/health

# 用户登录
curl -X POST http://127.0.0.1:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}'

# 获取城市列表
curl http://127.0.0.1:3000/api/cities

# 获取商圈热度排行
curl "http://127.0.0.1:3000/api/analytics/hot-ranking?cityId=beijing"
```

## 🚀 部署

### 开发环境

```bash
python run.py
```

### 生产环境

使用gunicorn部署：

```bash
# 安装gunicorn
pip install gunicorn

# 启动服务
gunicorn -w 4 -b 0.0.0.0:3000 app:app

# 使用配置文件
gunicorn -c gunicorn.conf.py app:app
```

### Docker部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 3000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:3000", "app:app"]
```

## 📝 开发指南

### 添加新的API接口

1. 在对应的蓝图文件中添加路由函数
2. 使用统一的响应格式（`success_response`, `error_response`）
3. 添加适当的错误处理和参数验证
4. 更新API文档

### 数据库迁移

```bash
# 初始化迁移
flask db init

# 生成迁移文件
flask db migrate -m "Add new table"

# 应用迁移
flask db upgrade
```

### 添加新的数据模型

1. 在`app/models/`目录下创建模型文件
2. 在`app/__init__.py`中导入模型
3. 运行数据库迁移

## 🤝 贡献

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

MIT License

## 📞 联系方式

如有问题或建议，请联系项目维护者。
