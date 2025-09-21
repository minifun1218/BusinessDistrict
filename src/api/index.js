// 统一导出所有API
export { authApi } from './auth'
export { cityApi } from './city'
export { businessApi, storeApi } from './business'
export { analyticsApi } from './analytics'

// 创建统一的API对象
export const api = {
  // 认证相关
  auth: {
    login: (params) => import('./auth').then(m => m.authApi.login(params)),
    register: (params) => import('./auth').then(m => m.authApi.register(params)),
    logout: () => import('./auth').then(m => m.authApi.logout()),
    getUserInfo: () => import('./auth').then(m => m.authApi.getUserInfo()),
    refreshToken: (token) => import('./auth').then(m => m.authApi.refreshToken(token))
  },

  // 城市相关
  city: {
    getList: (params) => import('./city').then(m => m.cityApi.getCityList(params)),
    getHotCities: () => import('./city').then(m => m.cityApi.getHotCities()),
    getById: (id) => import('./city').then(m => m.cityApi.getCityById(id)),
    search: (keyword) => import('./city').then(m => m.cityApi.searchCities(keyword))
  },

  // 商圈相关
  business: {
    getList: (params) => import('./business').then(m => m.businessApi.getBusinessAreas(params)),
    getById: (id) => import('./business').then(m => m.businessApi.getBusinessAreaById(id)),
    search: (params) => import('./business').then(m => m.businessApi.searchBusinessAreas(params)),
    getHotRanking: (cityId, params) => import('./business').then(m => m.businessApi.getHotRanking(cityId, params))
  },

  // 数据分析相关
  analytics: {
    getCityData: (cityId, params) => import('./analytics').then(m => m.analyticsApi.getCityAnalytics(cityId, params)),
    getHotRanking: (cityId, params) => import('./analytics').then(m => m.analyticsApi.getHotRankingData(cityId, params)),
    getHourlyFlow: (cityId, params) => import('./analytics').then(m => m.analyticsApi.getHourlyFlowData(cityId, params)),
    getCategoryDistribution: (cityId, params) => import('./analytics').then(m => m.analyticsApi.getCategoryDistribution(cityId, params)),
    getSentimentAnalysis: (cityId, params) => import('./analytics').then(m => m.analyticsApi.getSentimentAnalysis(cityId, params)),
    getConsumptionTrend: (cityId, params) => import('./analytics').then(m => m.analyticsApi.getConsumptionTrend(cityId, params)),
    getRadarComparison: (areaIds, params) => import('./analytics').then(m => m.analyticsApi.getRadarComparisonData(areaIds, params)),
    getHeatmapData: (cityId, params) => import('./analytics').then(m => m.analyticsApi.getHeatmapData(cityId, params)),
    getRealTimeData: (cityId) => import('./analytics').then(m => m.analyticsApi.getRealTimeData(cityId))
  }
}
