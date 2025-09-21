import { http } from '../utils/request'

// 商圈相关API
export const businessApi = {
  // 获取商圈列表
  getBusinessAreas(params = {}) {
    return http.get('/business-areas', params)
  },

  // 根据ID获取商圈详情
  getBusinessAreaById(areaId) {
    return http.get(`/business-areas/${areaId}`)
  },

  // 搜索商圈
  searchBusinessAreas(params) {
    return http.get('/business-areas/search', params)
  },

  // 获取商圈热度排行
  getHotRanking(cityId, params = {}) {
    return http.get('/business-areas/hot-ranking', { cityId, ...params })
  },

  // 获取商圈统计数据
  getBusinessAreaStats(areaId, params = {}) {
    return http.get(`/business-areas/${areaId}/stats`, params)
  },

  // 获取商圈内店铺列表
  getStoresByArea(areaId, params = {}) {
    return http.get(`/business-areas/${areaId}/stores`, params)
  },

  // 获取商圈客流分析
  getCustomerFlowAnalysis(areaId, params = {}) {
    return http.get(`/business-areas/${areaId}/customer-flow`, params)
  },

  // 获取商圈消费分析
  getConsumptionAnalysis(areaId, params = {}) {
    return http.get(`/business-areas/${areaId}/consumption`, params)
  },

  // 获取商圈评价分析
  getReviewAnalysis(areaId, params = {}) {
    return http.get(`/business-areas/${areaId}/reviews`, params)
  },

  // 获取商圈对比数据
  compareBusinessAreas(areaIds) {
    return http.post('/business-areas/compare', { areaIds })
  },

  // 获取附近商圈
  getNearbyBusinessAreas(longitude, latitude, radius = 5000) {
    return http.get('/business-areas/nearby', { longitude, latitude, radius })
  },

  // 搜索附近商圈（地图专用）
  searchNearbyBusinessAreas(params) {
    return http.get('/business/areas/nearby', params)
  },

  // 获取商圈列表（按城市）
  getBusinessAreaList(cityId) {
    return http.get('/business/areas', { city_id: cityId })
  },

  // 获取商圈分析数据
  getAreaAnalytics(areaId) {
    return http.get(`/business/areas/${areaId}/analytics`)
  }
}

// 店铺相关API
export const storeApi = {
  // 获取店铺列表
  getStores(params = {}) {
    return http.get('/stores', params)
  },

  // 根据ID获取店铺详情
  getStoreById(storeId) {
    return http.get(`/stores/${storeId}`)
  },

  // 搜索店铺
  searchStores(params) {
    return http.get('/stores/search', params)
  },

  // 获取推荐店铺
  getRecommendedStores(params = {}) {
    return http.get('/stores/recommended', params)
  },

  // 获取店铺评价
  getStoreReviews(storeId, params = {}) {
    return http.get(`/stores/${storeId}/reviews`, params)
  },

  // 添加店铺评价
  addStoreReview(storeId, review) {
    return http.post(`/stores/${storeId}/reviews`, review)
  },

  // 收藏店铺
  favoriteStore(storeId) {
    return http.post(`/stores/${storeId}/favorite`)
  },

  // 取消收藏
  unfavoriteStore(storeId) {
    return http.delete(`/stores/${storeId}/favorite`)
  },

  // 获取用户收藏的店铺
  getFavoriteStores(params = {}) {
    return http.get('/stores/favorites', params)
  },

  // 获取附近店铺
  getNearbyStores(longitude, latitude, radius = 2000, params = {}) {
    return http.get('/stores/nearby', { longitude, latitude, radius, ...params })
  }
}
