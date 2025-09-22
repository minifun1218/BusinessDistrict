// 环境配置
export const ENV_CONFIG = {
  // API基础URL
  API_BASE_URL: 'http://localhost:3000/api',
  
  // WebSocket URL
  WEBSOCKET_URL: 'ws://localhost:3000/ws',
  
  // 地图API密钥 - 高德地图API密钥
  MAP_API_KEY: '97407716929403378fa9e42d20c9b051',
  
  // 高德地图配置
  AMAP_CONFIG: {
    key: '97407716929403378fa9e42d20c9b051', // 高德地图API密钥
    version: '2.0',
    defaultCenter: [116.4074, 39.9042], // 北京 [lng, lat]
    defaultZoom: 11,
    enableScrollWheelZoom: true,
    enableContinuousZoom: true,
    enableInertialDragging: true,
    plugins: ['AMap.Scale', 'AMap.ToolBar', 'AMap.MapType', 'AMap.Geolocation']
  },
  
  // 保留百度地图配置以防需要回退
  BAIDU_MAP_CONFIG: {
    ak: 'O7g5t8aZEqcNICpKttmBl7ZkcNVtsx3p', // 百度地图API密钥
    version: '3.0',
    defaultCenter: { lng: 116.4074, lat: 39.9042 }, // 北京
    defaultZoom: 11,
    enableScrollWheelZoom: true,
    enableContinuousZoom: true,
    enableInertialDragging: true
  },
  
  // 环境类型
  ENVIRONMENT: 'development',
  
  // 是否开启调试
  DEBUG: true,
  
  // 请求超时时间
  REQUEST_TIMEOUT: 15000,
  
  // 分页默认大小
  PAGE_SIZE: 20,
  
  // 图表刷新间隔（毫秒）
  CHART_REFRESH_INTERVAL: 30000,
  
  // 地图默认中心点
  DEFAULT_MAP_CENTER: {
    longitude: 116.4074,
    latitude: 39.9042,
    zoom: 10
  },
  
  // 支持的城市列表（用于开发环境模拟）
  MOCK_CITIES: [
    { id: 'beijing', name: '北京', code: '110000' },
    { id: 'shanghai', name: '上海', code: '310000' },
    { id: 'guangzhou', name: '广州', code: '440100' },
    { id: 'shenzhen', name: '深圳', code: '440300' },
    { id: 'hangzhou', name: '杭州', code: '330100' },
    { id: 'nanjing', name: '南京', code: '320100' },
    { id: 'wuhan', name: '武汉', code: '420100' },
    { id: 'chengdu', name: '成都', code: '510100' }
  ]
}

// API配置（用于request.js）
export const API_CONFIG = {
  BASE_URL: ENV_CONFIG.API_BASE_URL,
  TIMEOUT: ENV_CONFIG.REQUEST_TIMEOUT
}

// 根据环境获取配置
export const getConfig = (key) => {
  return ENV_CONFIG[key]
}

// 是否为开发环境
export const isDevelopment = () => {
  return ENV_CONFIG.ENVIRONMENT === 'development'
}

// 是否为生产环境
export const isProduction = () => {
  return ENV_CONFIG.ENVIRONMENT === 'production'
}

// 日志工具
export const logger = {
  info: (...args) => {
    if (ENV_CONFIG.DEBUG) {
      console.log('[INFO]', ...args)
    }
  },
  warn: (...args) => {
    if (ENV_CONFIG.DEBUG) {
      console.warn('[WARN]', ...args)
    }
  },
  error: (...args) => {
    if (ENV_CONFIG.DEBUG) {
      console.error('[ERROR]', ...args)
    }
  },
  debug: (...args) => {
    if (ENV_CONFIG.DEBUG) {
      console.debug('[DEBUG]', ...args)
    }
  }
}
