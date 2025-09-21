# 数据源集成系统使用说明

## 概述

本系统集成了多个开放API数据源，用于获取真实的商圈和店铺数据：

- **百度地图开放API**：获取POI数据和地理信息
- **高德地图开放API**：获取地点数据和周边信息  
- **大众点评模拟数据**：演示评价和热度数据结构

## 系统特点

✅ **使用官方开放API** - 合规获取数据，无反爬风险  
✅ **多数据源融合** - 自动合并去重，提高数据完整性  
✅ **并发处理** - 多线程并行获取，提升效率  
✅ **智能缓存** - 避免重复请求，节省API配额  
✅ **错误重试** - 自动重试机制，提高稳定性  

## 快速开始

### 1. 配置API密钥

在环境变量或配置文件中设置：

```bash
# 百度地图API密钥
export BAIDU_MAP_AK="your-baidu-map-api-key"

# 高德地图API密钥  
export AMAP_KEY="your-amap-api-key"
```

### 2. 测试连接

```bash
curl http://localhost:3000/api/crawler/test
```

### 3. 获取城市数据

```bash
curl -X POST http://localhost:3000/api/crawler/crawl-city \
  -H "Content-Type: application/json" \
  -d '{
    "cityId": "110000",
    "cityName": "北京",
    "crawlers": ["baidu", "amap", "dianping"]
  }'
```

## API接口

### 获取数据源状态
```http
GET /api/crawler/status
```

### 测试数据源连接
```http
GET /api/crawler/test
```

### 获取城市商圈数据
```http
POST /api/crawler/crawl-city
Content-Type: application/json

{
  "cityId": "110000",
  "cityName": "北京",
  "crawlers": ["baidu", "amap"],  // 可选，默认使用所有数据源
  "updateExisting": false         // 是否更新已存在的数据
}
```

### 批量获取多城市数据
```http
POST /api/crawler/batch-crawl
Content-Type: application/json

{
  "cityIds": ["110000", "310000", "440100"],
  "crawlers": ["baidu", "amap"],
  "updateExisting": true
}
```

### 数据质量检查
```http
GET /api/crawler/data-quality
```

## 数据源详情

### 百度地图API
- **数据类型**: POI、商圈、地理编码
- **优势**: 数据覆盖全面，位置准确
- **限制**: 有调用频率和配额限制
- **官方文档**: https://lbsyun.baidu.com/

### 高德地图API  
- **数据类型**: POI、周边搜索、地点详情
- **优势**: 数据更新及时，分类详细
- **限制**: 有每日调用配额
- **官方文档**: https://lbs.amap.com/

### 大众点评（模拟）
- **数据类型**: 商圈评价、热度数据
- **说明**: 当前为模拟数据，演示数据结构
- **建议**: 实际使用时通过官方合作获取

## 数据处理流程

1. **多源并发获取** - 同时调用多个API获取数据
2. **智能去重合并** - 基于名称和坐标去重，合并相同实体
3. **数据标准化** - 统一数据格式和字段命名
4. **质量验证** - 检查必需字段，过滤无效数据
5. **入库保存** - 保存到数据库，更新统计信息

## 性能优化

- **并发控制**: 使用线程池控制并发数量
- **请求限流**: 自动延时，避免超出API限制
- **缓存机制**: 缓存热门查询结果
- **增量更新**: 支持仅更新变化的数据

## 错误处理

- **自动重试**: 网络错误自动重试3次
- **降级策略**: 单个数据源失败不影响整体流程
- **错误记录**: 详细记录错误信息用于调试
- **监控告警**: 可集成监控系统进行告警

## 成本控制

- **API配额监控**: 实时监控API调用量
- **智能缓存**: 减少重复请求
- **分时调度**: 在低峰期执行大批量任务
- **数据去重**: 避免重复存储相同数据

## 扩展指南

### 添加新数据源

1. 继承 `BaseDataClient` 类：

```python
from app.data_sources.base_client import BaseDataClient

class NewAPIClient(BaseDataClient):
    def __init__(self, api_key):
        super().__init__("新API数据源", api_key)
    
    def get_business_areas(self, city_id, city_name):
        # 实现获取商圈数据的逻辑
        pass
    
    def get_stores(self, area_id, area_name, area_lat, area_lng):
        # 实现获取店铺数据的逻辑
        pass
```

2. 在 `DataSourceManager` 中注册：

```python
def _init_clients(self):
    # 现有代码...
    self.clients['new_api'] = NewAPIClient(api_key)
```

## 监控和维护

### 日志监控
```bash
# 查看数据获取日志
tail -f app.log | grep "data_sources"

# 查看错误日志
tail -f app.log | grep "ERROR"
```

### 性能监控
- API调用次数和响应时间
- 数据获取成功率
- 数据库写入性能
- 内存和CPU使用情况

### 定期维护
- 清理过期缓存
- 检查API配额使用情况
- 更新API密钥
- 优化数据去重算法

## 注意事项

1. **API配额管理**: 合理规划API调用，避免超出限制
2. **数据合规**: 遵守各平台的使用条款和数据使用规范
3. **错误处理**: 做好异常处理，避免单点故障
4. **数据质量**: 定期检查数据准确性和完整性
5. **成本控制**: 监控API调用成本，优化调用策略

## 常见问题

**Q: API密钥无效怎么办？**
A: 检查密钥是否正确，是否有相应权限，是否已过期。

**Q: 数据获取失败怎么处理？**
A: 系统会自动重试，如果多次失败会记录错误日志，可以手动重新执行。

**Q: 如何提高数据获取速度？**
A: 可以增加并发数量，使用缓存，或者分批次处理数据。

**Q: 数据重复怎么办？**
A: 系统有自动去重机制，基于名称和坐标判断是否为同一实体。

## 技术支持

如有问题或建议，请提交Issue或联系开发团队。
