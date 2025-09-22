// 地图API动态加载器 - 支持高德地图
import { ENV_CONFIG } from '../config/env.js'

let loadPromise = null
let isLoading = false
let isLoaded = false

/**
 * 动态加载高德地图API
 * @returns {Promise<boolean>} 加载是否成功
 */
export function loadAmapAPI() {
  // 如果已经加载过，直接返回结果
  if (isLoaded) {
    return Promise.resolve(true)
  }
  
  // 如果正在加载，返回现有的Promise
  if (isLoading && loadPromise) {
    return loadPromise
  }
  
  // 检查API密钥
  const apiKey = ENV_CONFIG.AMAP_CONFIG.key
  if (!apiKey || apiKey.trim() === '' || apiKey === 'YOUR_AMAP_API_KEY') {
    console.warn('高德地图API密钥未配置')
    return Promise.resolve(false)
  }
  
  isLoading = true
  
  loadPromise = new Promise((resolve) => {
    try {
      // 创建script标签加载高德地图API
      const script = document.createElement('script')
      script.type = 'text/javascript'
      script.src = `https://webapi.amap.com/maps?v=2.0&key=${apiKey}&callback=initAmap`
      
      // 设置全局回调函数
      window.initAmap = () => {
        console.log('高德地图API加载成功')
        isLoaded = true
        isLoading = false
        resolve(true)
        
        // 清理全局回调
        delete window.initAmap
      }
      
      // 处理加载失败
      script.onerror = () => {
        console.error('高德地图API加载失败')
        isLoading = false
        resolve(false)
        
        // 清理全局回调
        delete window.initAmap
      }
      
      // 添加到页面
      document.head.appendChild(script)
      
      // 设置超时
      setTimeout(() => {
        if (isLoading) {
          console.error('高德地图API加载超时')
          isLoading = false
          resolve(false)
          
          // 清理全局回调
          delete window.initAmap
        }
      }, 10000) // 10秒超时
      
    } catch (error) {
      console.error('加载高德地图API时出错:', error)
      isLoading = false
      resolve(false)
    }
  })
  
  return loadPromise
}

/**
 * 检查高德地图API是否可用
 * @returns {boolean}
 */
export function isAmapAvailable() {
  return isLoaded && window.AMap && typeof window.AMap.Map === 'function'
}

/**
 * 重置加载状态（用于测试或重新加载）
 */
export function resetLoadState() {
  loadPromise = null
  isLoading = false
  isLoaded = false
}

// 保留百度地图API加载器的兼容性函数
export function loadBaiduMapAPI() {
  console.warn('已切换到高德地图，百度地图API加载器已弃用')
  return loadAmapAPI()
}

export function isBaiduMapAvailable() {
  console.warn('已切换到高德地图，百度地图API检查已弃用')
  return isAmapAvailable()
}
