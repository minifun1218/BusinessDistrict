// 百度地图API动态加载器
import { ENV_CONFIG } from '../config/env.js'

let loadPromise = null
let isLoading = false
let isLoaded = false

/**
 * 动态加载百度地图API
 * @returns {Promise<boolean>} 加载是否成功
 */
export function loadBaiduMapAPI() {
  // 如果已经加载过，直接返回结果
  if (isLoaded) {
    return Promise.resolve(true)
  }
  
  // 如果正在加载，返回现有的Promise
  if (isLoading && loadPromise) {
    return loadPromise
  }
  
  // 检查API密钥
  const apiKey = ENV_CONFIG.BAIDU_MAP_CONFIG.ak
  if (!apiKey || apiKey.trim() === '' || apiKey === 'YOUR_BAIDU_MAP_API_KEY') {
    console.warn('百度地图API密钥未配置')
    return Promise.resolve(false)
  }
  
  isLoading = true
  
  loadPromise = new Promise((resolve) => {
    try {
      // 创建script标签
      const script = document.createElement('script')
      script.type = 'text/javascript'
      script.src = `https://api.map.baidu.com/api?v=3.0&ak=${apiKey}&callback=initBaiduMap`
      
      // 设置全局回调函数
      window.initBaiduMap = () => {
        console.log('百度地图API加载成功')
        isLoaded = true
        isLoading = false
        resolve(true)
        
        // 清理全局回调
        delete window.initBaiduMap
      }
      
      // 处理加载失败
      script.onerror = () => {
        console.error('百度地图API加载失败')
        isLoading = false
        resolve(false)
        
        // 清理全局回调
        delete window.initBaiduMap
      }
      
      // 添加到页面
      document.head.appendChild(script)
      
      // 设置超时
      setTimeout(() => {
        if (isLoading) {
          console.error('百度地图API加载超时')
          isLoading = false
          resolve(false)
          
          // 清理全局回调
          delete window.initBaiduMap
        }
      }, 10000) // 10秒超时
      
    } catch (error) {
      console.error('加载百度地图API时出错:', error)
      isLoading = false
      resolve(false)
    }
  })
  
  return loadPromise
}

/**
 * 检查百度地图API是否可用
 * @returns {boolean}
 */
export function isBaiduMapAvailable() {
  return isLoaded && window.BMap && typeof window.BMap.Map === 'function'
}

/**
 * 重置加载状态（用于测试或重新加载）
 */
export function resetLoadState() {
  loadPromise = null
  isLoading = false
  isLoaded = false
}
