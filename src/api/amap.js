#!/usr/bin/env javascript
/**
 * 高德地图API服务 - 前端直接调用高德地图API
 */

import { ENV_CONFIG } from '../config/env.js'

const AMAP_API_BASE = 'https://restapi.amap.com/v3'

/**
 * 高德地图API服务类
 */
class AmapApiService {
  constructor() {
    this.apiKey = ENV_CONFIG.AMAP_CONFIG.key
  }

  /**
   * 周边搜索 - 搜索指定位置周围的POI
   * @param {Object} params 搜索参数
   * @param {string} params.location 经纬度 "lng,lat"
   * @param {string} params.keywords 关键词
   * @param {string} params.types POI类型代码
   * @param {number} params.radius 搜索半径（米）
   * @param {number} params.offset 每页记录数
   * @param {number} params.page 页码
   * @returns {Promise<Object>} API响应
   */
  async searchAround(params) {
    const {
      location,
      keywords = '',
      types = '',
      radius = 2000,
      offset = 20,
      page = 1
    } = params

    try {
      const queryParams = new URLSearchParams({
        key: this.apiKey,
        location,
        output: 'JSON',
        radius,
        offset,
        page,
        extensions: 'all'
      })

      if (keywords) queryParams.append('keywords', keywords)
      if (types) queryParams.append('types', types)

      const url = `${AMAP_API_BASE}/place/around?${queryParams}`
      
      // 使用JSONP方式调用，避免跨域问题
      const response = await this.makeJsonpRequest(url)
      
      return this.processSearchResult(response)
    } catch (error) {
      console.error('高德周边搜索失败:', error)
      throw new Error('搜索附近POI失败')
    }
  }

  /**
   * 关键词搜索 - 在指定城市搜索POI
   * @param {Object} params 搜索参数
   * @param {string} params.keywords 关键词
   * @param {string} params.city 城市名称或城市代码
   * @param {string} params.types POI类型代码
   * @param {number} params.offset 每页记录数
   * @param {number} params.page 页码
   * @returns {Promise<Object>} API响应
   */
  async searchText(params) {
    const {
      keywords,
      city = '全国',
      types = '',
      offset = 20,
      page = 1
    } = params

    try {
      const queryParams = new URLSearchParams({
        key: this.apiKey,
        keywords,
        city,
        output: 'JSON',
        offset,
        page,
        extensions: 'all'
      })

      if (types) queryParams.append('types', types)

      const url = `${AMAP_API_BASE}/place/text?${queryParams}`
      
      const response = await this.makeJsonpRequest(url)
      
      return this.processSearchResult(response)
    } catch (error) {
      console.error('高德关键词搜索失败:', error)
      throw new Error('搜索POI失败')
    }
  }

  /**
   * 搜索商圈 - 专门搜索商圈类型的POI
   * @param {Object} params 搜索参数
   * @param {string} params.location 经纬度 "lng,lat"
   * @param {number} params.radius 搜索半径（米）
   * @returns {Promise<Array>} 商圈列表
   */
  async searchBusinessAreas(params) {
    const { location, radius = 3000 } = params

    try {
      // 商圈相关的关键词和类型
      const businessKeywords = ['商圈', '商业区', '购物中心', '步行街', '商业广场', '商业街']
      const businessTypes = [
        '060000', // 购物服务
        '061000', // 购物中心
        '061200'  // 专业市场
      ]

      const allResults = []

      // 搜索商圈关键词
      for (const keyword of businessKeywords.slice(0, 3)) { // 限制搜索次数
        try {
          const result = await this.searchAround({
            location,
            keywords: keyword,
            radius,
            offset: 10
          })
          
          if (result.pois && result.pois.length > 0) {
            allResults.push(...result.pois)
          }
        } catch (error) {
          console.warn(`搜索关键词 "${keyword}" 失败:`, error)
        }
      }

      // 搜索商圈类型
      for (const type of businessTypes) {
        try {
          const result = await this.searchAround({
            location,
            types: type,
            radius,
            offset: 10
          })
          
          if (result.pois && result.pois.length > 0) {
            allResults.push(...result.pois)
          }
        } catch (error) {
          console.warn(`搜索类型 "${type}" 失败:`, error)
        }
      }

      // 数据去重和格式化
      const uniqueAreas = this.deduplicatePois(allResults)
      return this.formatBusinessAreas(uniqueAreas)

    } catch (error) {
      console.error('搜索商圈失败:', error)
      return []
    }
  }

  /**
   * 搜索附近POI - 搜索指定位置周围的各类POI
   * @param {Object} params 搜索参数
   * @param {string} params.location 经纬度 "lng,lat"
   * @param {number} params.radius 搜索半径（米）
   * @returns {Promise<Array>} POI列表
   */
  async searchNearbyPois(params) {
    const { location, radius = 1000 } = params

    try {
      // 常用POI类型
      const poiTypes = [
        '050000', // 餐饮服务
        '060000', // 购物服务
        '070000', // 生活服务
        '080000', // 休闲娱乐
        '100000'  // 住宿服务
      ]

      const allResults = []

      // 搜索不同类型的POI
      for (const type of poiTypes) {
        try {
          const result = await this.searchAround({
            location,
            types: type,
            radius,
            offset: 15
          })
          
          if (result.pois && result.pois.length > 0) {
            allResults.push(...result.pois)
          }
        } catch (error) {
          console.warn(`搜索POI类型 "${type}" 失败:`, error)
        }
      }

      // 数据去重和格式化
      const uniquePois = this.deduplicatePois(allResults)
      return this.formatPois(uniquePois)

    } catch (error) {
      console.error('搜索附近POI失败:', error)
      return []
    }
  }

  /**
   * 使用JSONP方式请求API（避免跨域）
   * @param {string} url API URL
   * @returns {Promise<Object>} API响应
   */
  makeJsonpRequest(url) {
    return new Promise((resolve, reject) => {
      const callbackName = `amap_callback_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      const script = document.createElement('script')
      
      // 设置全局回调函数
      window[callbackName] = (data) => {
        document.body.removeChild(script)
        delete window[callbackName]
        resolve(data)
      }
      
      // 添加callback参数
      const separator = url.includes('?') ? '&' : '?'
      script.src = `${url}${separator}callback=${callbackName}`
      script.onerror = () => {
        document.body.removeChild(script)
        delete window[callbackName]
        reject(new Error('JSONP请求失败'))
      }
      
      document.body.appendChild(script)
      
      // 设置超时
      setTimeout(() => {
        if (window[callbackName]) {
          document.body.removeChild(script)
          delete window[callbackName]
          reject(new Error('请求超时'))
        }
      }, 10000)
    })
  }

  /**
   * 处理搜索结果
   * @param {Object} response API响应
   * @returns {Object} 处理后的结果
   */
  processSearchResult(response) {
    if (!response || response.status !== '1') {
      throw new Error(response?.info || '搜索失败')
    }

    return {
      pois: response.pois || [],
      count: parseInt(response.count || 0),
      suggestion: response.suggestion || {},
      info: response.info
    }
  }

  /**
   * POI数据去重
   * @param {Array} pois POI列表
   * @returns {Array} 去重后的POI列表
   */
  deduplicatePois(pois) {
    const seen = new Set()
    const unique = []

    for (const poi of pois) {
      const key = `${poi.name}_${poi.location}`
      if (!seen.has(key)) {
        seen.add(key)
        unique.push(poi)
      }
    }

    return unique
  }

  /**
   * 格式化商圈数据
   * @param {Array} pois 原始POI数据
   * @returns {Array} 格式化后的商圈数据
   */
  formatBusinessAreas(pois) {
    return pois.map((poi, index) => {
      const [lng, lat] = poi.location.split(',').map(Number)
      
      return {
        id: poi.id || `area_${index}`,
        name: poi.name,
        longitude: lng,
        latitude: lat,
        address: poi.address || poi.pname + poi.cityname + poi.adname,
        category: this.determineAreaCategory(poi),
        hotValue: this.calculateHotValue(poi),
        distance: poi.distance ? Math.round(poi.distance) : 0,
        type: poi.type || '',
        tel: poi.tel || '',
        photos: poi.photos || [],
        rating: this.extractRating(poi),
        tags: this.extractTags(poi)
      }
    })
  }

  /**
   * 格式化POI数据
   * @param {Array} pois 原始POI数据
   * @returns {Array} 格式化后的POI数据
   */
  formatPois(pois) {
    return pois.map((poi, index) => {
      const [lng, lat] = poi.location.split(',').map(Number)
      
      return {
        id: poi.id || `poi_${index}`,
        name: poi.name,
        longitude: lng,
        latitude: lat,
        address: poi.address || poi.pname + poi.cityname + poi.adname,
        category: this.determinePoiCategory(poi.type),
        type: poi.type || '',
        tel: poi.tel || '',
        distance: poi.distance ? Math.round(poi.distance) : 0,
        rating: this.extractRating(poi),
        photos: poi.photos || [],
        business_area: poi.business_area || '',
        tags: this.extractTags(poi)
      }
    })
  }

  /**
   * 确定商圈类别
   * @param {Object} poi POI数据
   * @returns {string} 商圈类别
   */
  determineAreaCategory(poi) {
    const name = poi.name || ''
    const type = poi.type || ''

    if (name.includes('购物') || name.includes('商场') || name.includes('百货') || type.includes('购物')) {
      return '购物中心'
    } else if (name.includes('美食') || name.includes('餐饮') || type.includes('餐饮')) {
      return '美食街区'
    } else if (name.includes('娱乐') || name.includes('休闲') || type.includes('娱乐')) {
      return '休闲娱乐'
    } else {
      return '综合商圈'
    }
  }

  /**
   * 确定POI类别
   * @param {string} type POI类型
   * @returns {string} POI类别
   */
  determinePoiCategory(type) {
    if (!type) return '其他'

    const typeCode = type.split('|')[0] || type.substring(0, 6)
    
    const categoryMap = {
      '050000': '餐饮美食',
      '060000': '购物零售',
      '070000': '生活服务',
      '080000': '休闲娱乐',
      '100000': '酒店住宿',
      '110000': '旅游景点',
      '120000': '交通设施',
      '130000': '金融保险',
      '140000': '教育文化',
      '150000': '医疗保健'
    }

    return categoryMap[typeCode] || '其他'
  }

  /**
   * 计算热度值
   * @param {Object} poi POI数据
   * @returns {number} 热度值
   */
  calculateHotValue(poi) {
    let hotValue = 50 // 基础热度

    const name = poi.name || ''
    
    // 根据知名度调整
    if (['万达', '银泰', '大悦城', '龙湖', '华润'].some(brand => name.includes(brand))) {
      hotValue += 35
    } else if (['购物中心', '广场', '商场'].some(keyword => name.includes(keyword))) {
      hotValue += 25
    } else if (name.includes('步行街')) {
      hotValue += 20
    }

    // 根据地址重要性调整
    const address = poi.address || ''
    if (['市中心', 'CBD', '核心区'].some(keyword => address.includes(keyword))) {
      hotValue += 15
    }

    return Math.min(100, Math.max(0, hotValue))
  }

  /**
   * 提取评分
   * @param {Object} poi POI数据
   * @returns {number} 评分
   */
  extractRating(poi) {
    // 高德API通常不直接提供评分，可以从扩展信息中提取
    if (poi.biz_ext && poi.biz_ext.rating) {
      return parseFloat(poi.biz_ext.rating)
    }
    return 0
  }

  /**
   * 提取标签
   * @param {Object} poi POI数据
   * @returns {Array} 标签列表
   */
  extractTags(poi) {
    const tags = []
    
    if (poi.type) {
      const typeParts = poi.type.split('|')
      tags.push(...typeParts.filter(part => part.trim()))
    }
    
    if (poi.tag) {
      tags.push(poi.tag)
    }
    
    return [...new Set(tags)] // 去重
  }
}

// 创建服务实例
const amapApiService = new AmapApiService()

export default amapApiService
