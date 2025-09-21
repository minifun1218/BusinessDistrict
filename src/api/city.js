import { http } from '../utils/request'

// 城市相关API
export const cityApi = {
  // 获取城市列表
  getCityList(params = {}) {
    return http.get('/cities', params)
  },

  // 获取热门城市
  getHotCities() {
    return http.get('/cities/hot')
  },

  // 根据城市ID获取城市信息
  getCityById(cityId) {
    return http.get(`/cities/${cityId}`)
  },

  // 根据坐标获取城市信息
  getCityByLocation(longitude, latitude) {
    return http.get('/cities/location', { longitude, latitude })
  },

  // 搜索城市
  searchCities(keyword) {
    return http.get('/cities/search', { keyword })
  },

  // 获取省份列表
  getProvinces() {
    return http.get('/cities/provinces')
  },

  // 根据省份ID获取城市列表
  getCitiesByProvince(provinceId) {
    return http.get(`/cities/province/${provinceId}`)
  },

  // 根据城市ID获取区县列表
  getDistrictsByCity(cityId) {
    return http.get(`/cities/${cityId}/districts`)
  },

  // 获取城市统计信息
  getCityStats(cityId) {
    return http.get(`/cities/${cityId}/stats`)
  },

  // 获取城市商圈概览
  getCityBusinessAreas(cityId, params = {}) {
    return http.get(`/cities/${cityId}/business-areas`, params)
  }
}
