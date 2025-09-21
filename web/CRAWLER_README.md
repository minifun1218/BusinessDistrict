# 爬虫系统使用说明

## 概述

本系统集成了多个数据源的爬虫，用于获取真实的商圈和店铺数据，包括：

- **百度地图API爬虫**：获取POI数据和商圈信息
- **高德地图API爬虫**：获取地点数据和周边信息  
- **大众点评爬虫**：获取评价和热度数据（演示版本）

## 系统架构

```
app/crawler/
├── __init__.py                 # 模块初始化
├── base_crawler.py            # 爬虫基类
├── crawler_manager.py         # 爬虫管理器
├── scheduler.py              # 任务调度器
├── commands.py               # CLI命令
└── data_sources/             # 数据源爬虫
    ├── __init__.py
    ├── baidu_crawler.py      # 百度地图爬虫
    ├── amap_crawler.py       # 高德地图爬虫
    └── dianping_crawler.py   # 大众点评爬虫
```

## 配置

在 `config/config.py` 中添加API密钥：

```python
# 第三方API配置
BAIDU_MAP_AK = os.environ.get('BAIDU_MAP_AK') or 'your-baidu-map-api-key'
AMAP_KEY = os.environ.get('AMAP_KEY') or 'your-amap-api-key'
```

或设置环境变量：

```bash
export BAIDU_MAP_AK="your-baidu-map-api-key"
export AMAP_KEY="your-amap-api-key"
```

## API接口

### 1. 获取爬虫状态

```http
GET /api/crawler/status
```

返回可用的爬虫列表和统计信息。

### 2. 测试爬虫连通性

```http
GET /api/crawler/test
```

测试所有爬虫的连接状态。

### 3. 爬取城市数据

```http
POST /api/crawler/crawl-city
Content-Type: application/json

{
  "cityId": "110000",
  "cityName": "北京",
  "crawlers": ["baidu", "amap", "dianping"],  // 可选
  "updateExisting": false                      // 可选
}
```

### 4. 批量爬取城市数据

```http
POST /api/crawler/batch-crawl
Content-Type: application/json

{
  "cityIds": ["110000", "310000", "440100"],
  "crawlers": ["baidu", "amap"],
  "updateExisting": true
}
```

### 5. 爬取商圈店铺数据

```http
POST /api/crawler/crawl-area-stores
Content-Type: application/json

{
  "areaId": "area_123456",
  "crawlers": ["baidu", "amap"],
  "updateExisting": false
}
```

### 6. 检查数据质量

```http
GET /api/crawler/data-quality
```

返回数据完整性和质量报告。

## CLI命令

### 安装依赖

```bash
cd web
pip install -r requirements.txt
```

### 可用命令

1. **测试爬虫**：
   ```bash
   flask crawler test-crawlers
   ```

2. **爬取单个城市**：
   ```bash
   flask crawler crawl-city --city-name "北京" --crawlers "dianping" --update
   ```

3. **爬取热门城市**：
   ```bash
   flask crawler crawl-hot-cities --limit 5 --update
   ```

4. **爬取商圈店铺**：
   ```bash
   flask crawler crawl-area --area-name "王府井商圈" --update
   ```

5. **查看统计信息**：
   ```bash
   flask crawler show-stats
   ```

6. **检查数据质量**：
   ```bash
   flask crawler check-data-quality
   ```

## 定时任务

系统支持定时爬取任务：

- **每日数据更新**：凌晨2点自动更新热门城市数据
- **每周全量同步**：周日凌晨3点同步所有城市数据
- **自定义任务**：通过API调度特定时间的爬取任务

### 调度任务示例

```http
POST /api/crawler/schedule-task
Content-Type: application/json

{
  "taskType": "city",
  "targetIds": ["110000", "310000"],
  "scheduleTime": "2024-01-01T02:00:00",
  "crawlers": ["baidu", "amap"],
  "updateExisting": true
}
```

## 数据流程

1. **城市数据爬取**：
   - 根据城市名称搜索商圈
   - 提取商圈基本信息（名称、坐标、类型等）
   - 计算热度值和其他指标
   - 保存到数据库

2. **店铺数据爬取**：
   - 基于商圈坐标搜索周边店铺
   - 提取店铺详细信息（评分、价格、标签等）
   - 分类处理不同类型的店铺
   - 更新商圈的店铺统计

3. **数据合并**：
   - 多个数据源的信息自动合并
   - 去重和数据清洗
   - 优先保留更完整的数据

## 监控和维护

### 日志查看

系统会记录详细的爬取日志：

```bash
tail -f app.log | grep crawler
```

### 错误处理

- 自动重试机制（最多3次）
- 反爬虫检测和延时
- 数据验证和清洗
- 异常情况记录

### 性能优化

- 并发爬取多个数据源
- 智能去重算法
- 增量更新机制
- 缓存热门数据

## 扩展新的数据源

1. 创建新的爬虫类继承 `BaseCrawler`：

```python
from app.crawler.base_crawler import BaseCrawler

class NewCrawler(BaseCrawler):
    def __init__(self, api_key):
        super().__init__("新数据源")
        self.api_key = api_key
    
    def get_business_areas(self, city_id, city_name):
        # 实现商圈数据获取逻辑
        pass
    
    def get_stores(self, area_id, area_name, area_lat, area_lng):
        # 实现店铺数据获取逻辑
        pass
```

2. 在 `CrawlerManager` 中注册新爬虫：

```python
def _init_crawlers(self):
    # ... 现有代码 ...
    self.crawlers['new_source'] = NewCrawler(api_key)
```

## 注意事项

1. **API限制**：
   - 百度地图API有调用频率限制
   - 高德地图API有每日配额限制
   - 建议设置合理的延时和重试策略

2. **反爬虫**：
   - 使用随机User-Agent
   - 设置随机延时
   - 避免过于频繁的请求

3. **数据质量**：
   - 定期检查数据完整性
   - 验证坐标准确性
   - 清理重复和无效数据

4. **法律合规**：
   - 遵守网站的robots.txt
   - 尊重数据提供方的使用条款
   - 不要过度爬取影响服务

## 故障排除

### 常见问题

1. **API密钥无效**：
   - 检查配置文件中的API密钥
   - 确认密钥权限和配额

2. **网络连接问题**：
   - 检查网络连接
   - 确认防火墙设置

3. **数据库错误**：
   - 检查数据库连接
   - 确认表结构正确

### 调试方法

1. 启用详细日志：
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. 使用测试脚本：
   ```bash
   python test_crawler.py
   ```

3. 单独测试爬虫：
   ```bash
   flask crawler test-crawlers
   ```

## 更新日志

- **v1.0.0** (2024-01-01): 初始版本，支持百度地图、高德地图、大众点评数据源
- 后续版本将添加更多数据源和功能优化
