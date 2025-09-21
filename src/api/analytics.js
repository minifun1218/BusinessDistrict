import { http } from '../utils/request'

// 数据分析相关API
export const analyticsApi = {
  // 获取城市整体统计数据
  getCityAnalytics(cityId, params = {}) {
    return http.get(`/analytics/city/${cityId}`, params)
  },

  // 获取商圈热度排行数据
  getHotRankingData(cityId, params = {}) {
    return http.get(`/analytics/hot-ranking`, { cityId, ...params })
  },

  // 获取24小时客流分析数据
  getHourlyFlowData(cityId, params = {}) {
    return http.get(`/analytics/hourly-flow`, { cityId, ...params })
  },

  // 获取消费类型分布数据
  getCategoryDistribution(cityId, params = {}) {
    return http.get(`/analytics/category-distribution`, { cityId, ...params })
  },

  // 获取情感分析数据
  getSentimentAnalysis(cityId, params = {}) {
    return http.get(`/analytics/sentiment-analysis`, { cityId, ...params })
  },

  // 获取消费趋势数据
  getConsumptionTrend(cityId, params = {}) {
    return http.get(`/analytics/consumption-trend`, { cityId, ...params })
  },

  // 获取商圈对比雷达图数据
  getRadarComparisonData(areaIds, params = {}) {
    return http.post(`/analytics/radar-comparison`, { areaIds, ...params })
  },

  // 获取地图热力图数据
  getHeatmapData(cityId, params = {}) {
    return http.get(`/analytics/heatmap`, { cityId, ...params })
  },

  // 获取实时数据
  getRealTimeData(cityId) {
    return http.get(`/analytics/realtime/${cityId}`)
  },

  // 获取时间段对比数据
  getTimeComparisonData(cityId, params = {}) {
    return http.get(`/analytics/time-comparison`, { cityId, ...params })
  },

  // 获取用户画像数据
  getUserProfileData(cityId, params = {}) {
    return http.get(`/analytics/user-profile`, { cityId, ...params })
  },

  // 获取商圈客流预测
  getCustomerFlowForecast(areaId, params = {}) {
    return http.get(`/analytics/forecast/customer-flow/${areaId}`, params)
  },

  // 获取消费预测
  getConsumptionForecast(areaId, params = {}) {
    return http.get(`/analytics/forecast/consumption/${areaId}`, params)
  },

  // 获取节假日影响分析
  getHolidayImpactAnalysis(cityId, params = {}) {
    return http.get(`/analytics/holiday-impact`, { cityId, ...params })
  },

  // 获取天气影响分析
  getWeatherImpactAnalysis(cityId, params = {}) {
    return http.get(`/analytics/weather-impact`, { cityId, ...params })
  },

  // 获取竞争分析数据
  getCompetitiveAnalysis(areaId, params = {}) {
    return http.get(`/analytics/competitive/${areaId}`, params)
  },

  // 导出分析报告
  exportAnalyticsReport(params) {
    return http.download('/analytics/export', params, `analytics-report-${Date.now()}.xlsx`)
  },

  // 获取特定商圈的热度排行数据
  getAreaHotRankingData(areaId) {
    return http.get('/analytics/area-hot-ranking', { area_id: areaId })
  },

  // 获取特定商圈的客流数据
  getAreaHourlyFlowData(areaId) {
    return http.get('/analytics/area-hourly-flow', { area_id: areaId })
  },

  // 获取特定商圈的类型分布数据
  getAreaCategoryDistribution(areaId) {
    return http.get('/analytics/area-category-distribution', { area_id: areaId })
  },

  // 获取特定商圈的情感分析数据
  getAreaSentimentAnalysis(areaId) {
    return http.get('/analytics/area-sentiment-analysis', { area_id: areaId })
  },

  // 获取特定商圈的消费趋势数据
  getAreaConsumptionTrend(areaId) {
    return http.get('/analytics/area-consumption-trend', { area_id: areaId })
  },

  // 获取特定商圈的雷达对比数据
  getAreaRadarComparisonData(areaIds) {
    return http.post('/analytics/area-radar-comparison', { area_ids: areaIds })
  }
}
