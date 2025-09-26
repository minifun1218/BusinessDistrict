-- 城市商圈消费热度可视化分析系统数据库结构
-- 创建时间: 2024-01-20
-- 数据库类型: SQLite/MySQL/PostgreSQL 通用

-- ==============================================
-- 1. 城市表 (cities)
-- ==============================================
CREATE TABLE IF NOT EXISTS cities (
    id VARCHAR(20) PRIMARY KEY,                    -- 城市代码 (如: beijing, shanghai)
    name VARCHAR(50) NOT NULL,                     -- 城市名称
    code VARCHAR(20) UNIQUE NOT NULL,              -- 行政区划代码
    level ENUM('province', 'city', 'district') NOT NULL, -- 行政级别
    parent_id VARCHAR(20),                         -- 父级城市ID
    
    -- 地理信息
    longitude FLOAT NOT NULL,                      -- 经度
    latitude FLOAT NOT NULL,                       -- 纬度
    
    -- 城市信息
    population INTEGER,                            -- 人口数量
    area FLOAT,                                    -- 面积（平方公里）
    economic_level ENUM('high', 'medium', 'low') DEFAULT 'medium', -- 经济水平
    is_hot BOOLEAN DEFAULT FALSE,                  -- 是否为热门城市
    
    -- 拼音信息（用于搜索）
    pinyin VARCHAR(100),                           -- 完整拼音
    pinyin_abbr VARCHAR(10),                       -- 拼音缩写
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 外键约束
    FOREIGN KEY (parent_id) REFERENCES cities(id) ON DELETE SET NULL,
    
    -- 索引
    INDEX idx_cities_name (name),
    INDEX idx_cities_code (code),
    INDEX idx_cities_level (level),
    INDEX idx_cities_pinyin (pinyin),
    INDEX idx_cities_pinyin_abbr (pinyin_abbr),
    INDEX idx_cities_parent (parent_id),
    INDEX idx_cities_location (longitude, latitude)
);

-- ==============================================
-- 2. 商圈表 (business_areas)
-- ==============================================
CREATE TABLE IF NOT EXISTS business_areas (
    id VARCHAR(50) PRIMARY KEY,                   -- 商圈唯一标识
    name VARCHAR(100) NOT NULL,                   -- 商圈名称
    city_id VARCHAR(20) NOT NULL,                 -- 所属城市ID
    
    -- 商圈分类
    type ENUM('shopping', 'dining', 'entertainment', 'mixed') DEFAULT 'mixed', -- 商圈类型
    level ENUM('A', 'B', 'C', 'D') DEFAULT 'C',   -- 商圈等级
    
    -- 地理信息
    longitude FLOAT NOT NULL,                      -- 经度
    latitude FLOAT NOT NULL,                       -- 纬度
    area FLOAT,                                    -- 面积（平方公里）
    
    -- 商圈数据
    hot_value INTEGER DEFAULT 0,                  -- 热度值 (0-100)
    avg_consumption FLOAT DEFAULT 0.0,            -- 平均消费
    customer_flow INTEGER DEFAULT 0,              -- 日均客流量
    store_count INTEGER DEFAULT 0,                -- 店铺数量
    rating FLOAT DEFAULT 0.0,                     -- 评分 (0-5)
    review_count INTEGER DEFAULT 0,               -- 评价数量
    
    -- 基本信息
    address TEXT,                                  -- 详细地址
    description TEXT,                              -- 商圈描述
    opening_hours VARCHAR(100),                    -- 营业时间
    
    -- JSON字段（存储复杂数据）
    facilities JSON,                               -- 配套设施 ["停车场", "WiFi", "ATM"]
    transportation JSON,                           -- 交通信息 [{"type": "地铁", "description": "附近有地铁站"}]
    images JSON,                                   -- 图片列表 ["url1", "url2"]
    tags JSON,                                     -- 标签 ["购物天堂", "美食聚集地"]
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 外键约束
    FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE CASCADE,
    
    -- 索引
    INDEX idx_business_areas_name (name),
    INDEX idx_business_areas_city (city_id),
    INDEX idx_business_areas_type (type),
    INDEX idx_business_areas_level (level),
    INDEX idx_business_areas_hot_value (hot_value),
    INDEX idx_business_areas_rating (rating),
    INDEX idx_business_areas_location (longitude, latitude),
    INDEX idx_business_areas_updated (updated_at),
    
    -- 复合索引
    INDEX idx_business_areas_city_hot (city_id, hot_value),
    INDEX idx_business_areas_city_type (city_id, type),
    INDEX idx_business_areas_location_hot (longitude, latitude, hot_value)
);

-- ==============================================
-- 3. 店铺表 (stores)
-- ==============================================
CREATE TABLE IF NOT EXISTS stores (
    id VARCHAR(50) PRIMARY KEY,                   -- 店铺唯一标识
    name VARCHAR(100) NOT NULL,                   -- 店铺名称
    business_area_id VARCHAR(50) NOT NULL,        -- 所属商圈ID
    
    -- 店铺分类
    category ENUM('restaurant', 'retail', 'entertainment', 'service') NOT NULL, -- 主要类别
    sub_category VARCHAR(50),                      -- 子分类
    
    -- 地理信息
    longitude FLOAT NOT NULL,                      -- 经度
    latitude FLOAT NOT NULL,                       -- 纬度
    
    -- 店铺数据
    rating FLOAT DEFAULT 0.0,                     -- 评分 (0-5)
    review_count INTEGER DEFAULT 0,               -- 评价数量
    avg_price FLOAT DEFAULT 0.0,                  -- 平均消费价格
    
    -- 基本信息
    phone VARCHAR(20),                             -- 联系电话
    address VARCHAR(255),                          -- 详细地址
    opening_hours VARCHAR(100),                    -- 营业时间
    description TEXT,                              -- 店铺描述
    
    -- JSON字段
    images JSON,                                   -- 图片列表
    tags JSON,                                     -- 标签
    facilities JSON,                               -- 设施信息
    
    -- 推荐状态
    is_recommended BOOLEAN DEFAULT FALSE,          -- 是否推荐
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 外键约束
    FOREIGN KEY (business_area_id) REFERENCES business_areas(id) ON DELETE CASCADE,
    
    -- 索引
    INDEX idx_stores_name (name),
    INDEX idx_stores_business_area (business_area_id),
    INDEX idx_stores_category (category),
    INDEX idx_stores_sub_category (sub_category),
    INDEX idx_stores_rating (rating),
    INDEX idx_stores_avg_price (avg_price),
    INDEX idx_stores_recommended (is_recommended),
    INDEX idx_stores_location (longitude, latitude),
    
    -- 复合索引
    INDEX idx_stores_area_category (business_area_id, category),
    INDEX idx_stores_area_rating (business_area_id, rating),
    INDEX idx_stores_category_rating (category, rating)
);

-- ==============================================
-- 4. 用户表 (users)
-- ==============================================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,        -- 用户ID
    username VARCHAR(50) UNIQUE NOT NULL,         -- 用户名
    email VARCHAR(100) UNIQUE NOT NULL,           -- 邮箱
    phone VARCHAR(20),                             -- 手机号
    password_hash VARCHAR(255) NOT NULL,          -- 密码哈希
    
    -- 用户信息
    nickname VARCHAR(50),                          -- 昵称
    avatar_url VARCHAR(255),                       -- 头像URL
    gender ENUM('male', 'female', 'other'),        -- 性别
    birth_date DATE,                               -- 出生日期
    city_id VARCHAR(20),                           -- 所在城市
    
    -- 用户状态
    is_active BOOLEAN DEFAULT TRUE,                -- 是否激活
    is_verified BOOLEAN DEFAULT FALSE,             -- 是否验证
    last_login_at DATETIME,                        -- 最后登录时间
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 外键约束
    FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE SET NULL,
    
    -- 索引
    INDEX idx_users_username (username),
    INDEX idx_users_email (email),
    INDEX idx_users_phone (phone),
    INDEX idx_users_city (city_id),
    INDEX idx_users_active (is_active),
    INDEX idx_users_last_login (last_login_at)
);

-- ==============================================
-- 5. 商圈评价表 (area_reviews)
-- ==============================================
CREATE TABLE IF NOT EXISTS area_reviews (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,        -- 评价ID
    business_area_id VARCHAR(50) NOT NULL,        -- 商圈ID
    user_id INTEGER,                               -- 用户ID（可为空，支持匿名评价）
    user_name VARCHAR(50),                         -- 用户昵称（匿名时使用）
    
    -- 评价内容
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5), -- 评分 1-5
    title VARCHAR(100),                            -- 评价标题
    content TEXT NOT NULL,                         -- 评价内容
    
    -- 评价统计
    helpful_count INTEGER DEFAULT 0,              -- 有用数
    images JSON,                                   -- 评价图片
    
    -- 评价来源
    source ENUM('dianping', 'meituan', 'manual', 'system') DEFAULT 'manual', -- 数据来源
    external_id VARCHAR(100),                      -- 外部评价ID
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 外键约束
    FOREIGN KEY (business_area_id) REFERENCES business_areas(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    
    -- 索引
    INDEX idx_area_reviews_business_area (business_area_id),
    INDEX idx_area_reviews_user (user_id),
    INDEX idx_area_reviews_rating (rating),
    INDEX idx_area_reviews_source (source),
    INDEX idx_area_reviews_created (created_at),
    
    -- 复合索引
    INDEX idx_area_reviews_area_rating (business_area_id, rating),
    INDEX idx_area_reviews_area_created (business_area_id, created_at)
);

-- ==============================================
-- 6. 店铺评价表 (store_reviews)
-- ==============================================
CREATE TABLE IF NOT EXISTS store_reviews (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,        -- 评价ID
    store_id VARCHAR(50) NOT NULL,                 -- 店铺ID
    user_id INTEGER,                               -- 用户ID
    user_name VARCHAR(50),                         -- 用户昵称
    
    -- 评价内容
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5), -- 评分 1-5
    title VARCHAR(100),                            -- 评价标题
    content TEXT NOT NULL,                         -- 评价内容
    
    -- 评价统计
    helpful_count INTEGER DEFAULT 0,              -- 有用数
    images JSON,                                   -- 评价图片
    
    -- 评价来源
    source ENUM('dianping', 'meituan', 'manual', 'system') DEFAULT 'manual',
    external_id VARCHAR(100),                      -- 外部评价ID
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 外键约束
    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    
    -- 索引
    INDEX idx_store_reviews_store (store_id),
    INDEX idx_store_reviews_user (user_id),
    INDEX idx_store_reviews_rating (rating),
    INDEX idx_store_reviews_source (source),
    INDEX idx_store_reviews_created (created_at),
    
    -- 复合索引
    INDEX idx_store_reviews_store_rating (store_id, rating),
    INDEX idx_store_reviews_store_created (store_id, created_at)
);

-- ==============================================
-- 7. 数据爬取记录表 (crawl_records)
-- ==============================================
CREATE TABLE IF NOT EXISTS crawl_records (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,        -- 记录ID
    target_type ENUM('business_area', 'store', 'city') NOT NULL, -- 爬取目标类型
    target_id VARCHAR(50) NOT NULL,                -- 目标ID
    source ENUM('dianping', 'meituan', 'amap', 'baidu') NOT NULL, -- 数据源
    
    -- 爬取状态
    status ENUM('pending', 'running', 'success', 'failed') DEFAULT 'pending', -- 爬取状态
    error_message TEXT,                            -- 错误信息
    
    -- 爬取统计
    items_crawled INTEGER DEFAULT 0,              -- 爬取条目数
    items_saved INTEGER DEFAULT 0,                -- 保存条目数
    start_time DATETIME,                           -- 开始时间
    end_time DATETIME,                             -- 结束时间
    duration INTEGER,                              -- 耗时（秒）
    
    -- 爬取配置
    config JSON,                                   -- 爬取配置
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX idx_crawl_records_target (target_type, target_id),
    INDEX idx_crawl_records_source (source),
    INDEX idx_crawl_records_status (status),
    INDEX idx_crawl_records_created (created_at),
    
    -- 复合索引
    INDEX idx_crawl_records_target_source (target_type, target_id, source),
    INDEX idx_crawl_records_status_created (status, created_at)
);

-- ==============================================
-- 8. 系统配置表 (system_config)
-- ==============================================
CREATE TABLE IF NOT EXISTS system_config (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,        -- 配置ID
    config_key VARCHAR(100) UNIQUE NOT NULL,      -- 配置键
    config_value TEXT,                             -- 配置值
    config_type ENUM('string', 'integer', 'float', 'boolean', 'json') DEFAULT 'string', -- 值类型
    description TEXT,                              -- 配置描述
    is_public BOOLEAN DEFAULT FALSE,               -- 是否公开（前端可访问）
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX idx_system_config_key (config_key),
    INDEX idx_system_config_public (is_public)
);

-- ==============================================
-- 9. 用户收藏表 (user_favorites)
-- ==============================================
CREATE TABLE IF NOT EXISTS user_favorites (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,        -- 收藏ID
    user_id INTEGER NOT NULL,                      -- 用户ID
    target_type ENUM('business_area', 'store') NOT NULL, -- 收藏类型
    target_id VARCHAR(50) NOT NULL,                -- 目标ID
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键约束
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- 唯一约束（用户不能重复收藏同一个对象）
    UNIQUE KEY uk_user_favorites (user_id, target_type, target_id),
    
    -- 索引
    INDEX idx_user_favorites_user (user_id),
    INDEX idx_user_favorites_target (target_type, target_id),
    INDEX idx_user_favorites_created (created_at)
);

-- ==============================================
-- 10. 搜索历史表 (search_history)
-- ==============================================
CREATE TABLE IF NOT EXISTS search_history (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,        -- 历史ID
    user_id INTEGER,                               -- 用户ID（可为空，支持匿名搜索）
    session_id VARCHAR(100),                       -- 会话ID
    
    -- 搜索信息
    search_type ENUM('keyword', 'location', 'area') NOT NULL, -- 搜索类型
    search_query TEXT NOT NULL,                    -- 搜索查询
    search_params JSON,                            -- 搜索参数
    
    -- 搜索结果
    result_count INTEGER DEFAULT 0,               -- 结果数量
    click_position INTEGER,                        -- 点击位置（用户点击了第几个结果）
    clicked_target_id VARCHAR(50),                 -- 点击的目标ID
    
    -- 位置信息
    longitude FLOAT,                               -- 搜索时的经度
    latitude FLOAT,                                -- 搜索时的纬度
    city_id VARCHAR(20),                           -- 搜索时的城市
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键约束
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE SET NULL,
    
    -- 索引
    INDEX idx_search_history_user (user_id),
    INDEX idx_search_history_session (session_id),
    INDEX idx_search_history_type (search_type),
    INDEX idx_search_history_city (city_id),
    INDEX idx_search_history_created (created_at),
    
    -- 复合索引
    INDEX idx_search_history_user_created (user_id, created_at),
    INDEX idx_search_history_city_created (city_id, created_at)
);

-- ==============================================
-- 初始化数据
-- ==============================================

-- 插入默认城市数据
INSERT INTO cities (id, name, code, level, longitude, latitude, pinyin, pinyin_abbr, is_hot) VALUES
('beijing', '北京', '110000', 'city', 116.4074, 39.9042, 'beijing', 'bj', TRUE),
('shanghai', '上海', '310000', 'city', 121.4737, 31.2304, 'shanghai', 'sh', TRUE),
('guangzhou', '广州', '440100', 'city', 113.2644, 23.1291, 'guangzhou', 'gz', TRUE),
('shenzhen', '深圳', '440300', 'city', 114.0579, 22.5431, 'shenzhen', 'sz', TRUE),
('hangzhou', '杭州', '330100', 'city', 120.1614, 30.2936, 'hangzhou', 'hz', TRUE),
('nanjing', '南京', '320100', 'city', 118.7969, 32.0603, 'nanjing', 'nj', TRUE),
('wuhan', '武汉', '420100', 'city', 114.2734, 30.5801, 'wuhan', 'wh', TRUE),
('chengdu', '成都', '510100', 'city', 104.0668, 30.5728, 'chengdu', 'cd', TRUE);

-- 插入系统配置
INSERT INTO system_config (config_key, config_value, config_type, description, is_public) VALUES
('crawl_delay_min', '2', 'integer', '爬虫最小延迟时间（秒）', FALSE),
('crawl_delay_max', '5', 'integer', '爬虫最大延迟时间（秒）', FALSE),
('cache_expire_days', '2', 'integer', '数据缓存过期天数', FALSE),
('max_search_results', '50', 'integer', '最大搜索结果数', TRUE),
('default_search_radius', '1000', 'integer', '默认搜索半径（米）', TRUE),
('site_name', '城市商圈消费热度分析系统', 'string', '网站名称', TRUE),
('enable_user_registration', 'true', 'boolean', '是否允许用户注册', TRUE);

-- ==============================================
-- 视图定义
-- ==============================================

-- 商圈统计视图
CREATE VIEW IF NOT EXISTS business_area_stats AS
SELECT 
    ba.id,
    ba.name,
    ba.city_id,
    c.name as city_name,
    ba.type,
    ba.level,
    ba.longitude,
    ba.latitude,
    ba.hot_value,
    ba.rating,
    ba.review_count,
    COUNT(DISTINCT s.id) as store_count_actual,
    AVG(s.rating) as avg_store_rating,
    SUM(s.review_count) as total_store_reviews,
    COUNT(DISTINCT ar.id) as area_review_count,
    AVG(ar.rating) as avg_area_rating,
    ba.updated_at
FROM business_areas ba
LEFT JOIN cities c ON ba.city_id = c.id
LEFT JOIN stores s ON ba.id = s.business_area_id
LEFT JOIN area_reviews ar ON ba.id = ar.business_area_id
GROUP BY ba.id;

-- 城市商圈统计视图
CREATE VIEW IF NOT EXISTS city_business_stats AS
SELECT 
    c.id as city_id,
    c.name as city_name,
    COUNT(DISTINCT ba.id) as business_area_count,
    COUNT(DISTINCT s.id) as store_count,
    AVG(ba.hot_value) as avg_hot_value,
    AVG(ba.rating) as avg_rating,
    SUM(ba.review_count) as total_reviews,
    MAX(ba.updated_at) as last_updated
FROM cities c
LEFT JOIN business_areas ba ON c.id = ba.city_id
LEFT JOIN stores s ON ba.id = s.business_area_id
GROUP BY c.id;

-- ==============================================
-- 触发器定义 (MySQL)
-- ==============================================

-- 更新商圈店铺数量触发器
DELIMITER $$
CREATE TRIGGER IF NOT EXISTS update_business_area_store_count_insert
AFTER INSERT ON stores
FOR EACH ROW
BEGIN
    UPDATE business_areas 
    SET store_count = (
        SELECT COUNT(*) 
        FROM stores 
        WHERE business_area_id = NEW.business_area_id
    ),
    updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.business_area_id;
END$$

CREATE TRIGGER IF NOT EXISTS update_business_area_store_count_delete
AFTER DELETE ON stores
FOR EACH ROW
BEGIN
    UPDATE business_areas 
    SET store_count = (
        SELECT COUNT(*) 
        FROM stores 
        WHERE business_area_id = OLD.business_area_id
    ),
    updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.business_area_id;
END$$

-- 更新商圈评价统计触发器
CREATE TRIGGER IF NOT EXISTS update_business_area_review_stats_insert
AFTER INSERT ON area_reviews
FOR EACH ROW
BEGIN
    UPDATE business_areas 
    SET review_count = (
        SELECT COUNT(*) 
        FROM area_reviews 
        WHERE business_area_id = NEW.business_area_id
    ),
    rating = (
        SELECT AVG(rating) 
        FROM area_reviews 
        WHERE business_area_id = NEW.business_area_id
    ),
    updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.business_area_id;
END$$

CREATE TRIGGER IF NOT EXISTS update_business_area_review_stats_delete
AFTER DELETE ON area_reviews
FOR EACH ROW
BEGIN
    UPDATE business_areas 
    SET review_count = (
        SELECT COUNT(*) 
        FROM area_reviews 
        WHERE business_area_id = OLD.business_area_id
    ),
    rating = COALESCE((
        SELECT AVG(rating) 
        FROM area_reviews 
        WHERE business_area_id = OLD.business_area_id
    ), 0),
    updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.business_area_id;
END$$

DELIMITER ;

-- ==============================================
-- 性能优化建议
-- ==============================================

-- 1. 定期清理过期数据
-- DELETE FROM search_history WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY);
-- DELETE FROM crawl_records WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY) AND status IN ('success', 'failed');

-- 2. 定期更新统计数据
-- 可以创建定时任务来更新商圈的统计信息

-- 3. 索引优化
-- 根据实际查询模式调整索引，删除不必要的索引

-- ==============================================
-- 备份和恢复建议
-- ==============================================

-- 备份命令示例 (MySQL):
-- mysqldump -u username -p database_name > backup.sql

-- 恢复命令示例 (MySQL):
-- mysql -u username -p database_name < backup.sql

-- ==============================================
-- 数据库创建完成
-- ==============================================
