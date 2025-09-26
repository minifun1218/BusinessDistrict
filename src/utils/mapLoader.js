// 地图API动态加载器 - 支持高德地图和百度地图
import { ENV_CONFIG } from '../config/env.js'

let loadPromise = null
let isLoading = false
let isLoaded = false

/**
 * 动态加载高德地图API - 使用AMapLoader方式
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
  const securityJsCode = ENV_CONFIG.AMAP_CONFIG.securityJsCode
  if (!apiKey || apiKey.trim() === '' || apiKey === 'YOUR_AMAP_API_KEY') {
    console.warn('高德地图API密钥未配置')
    return Promise.resolve(false)
  }
  
  if (!securityJsCode || securityJsCode.trim() === '') {
    console.warn('高德地图安全密钥未配置')
    return Promise.resolve(false)
  }
  
  isLoading = true
  
  loadPromise = new Promise((resolve) => {
    try {
      // 先加载 AMapLoader
      const loaderScript = document.createElement('script')
      loaderScript.type = 'text/javascript'
      loaderScript.src = 'https://webapi.amap.com/loader.js'
      
      loaderScript.onload = () => {
        // 设置安全密钥
        window._AMapSecurityConfig = {
          securityJsCode: securityJsCode
        }
        
        // 使用AMapLoader加载地图API
        window.AMapLoader.load({
          key: apiKey,
          version: ENV_CONFIG.AMAP_CONFIG.version || '2.0',
          plugins: ENV_CONFIG.AMAP_CONFIG.plugins || [
            'AMap.Scale', 
            'AMap.ToolBar', 
            'AMap.MapType', 
            'AMap.Geolocation',
            'AMap.PlaceSearch'
          ],
          AMapUI: ENV_CONFIG.AMAP_CONFIG.AMapUI || {
            version: '1.1',
            plugins: ['overlay/SimpleMarker']
          },
          Loca: ENV_CONFIG.AMAP_CONFIG.Loca || {
            version: '2.0'
          }
        }).then((AMap) => {
          console.log('高德地图API加载成功')
          window.AMap = AMap // 确保全局可访问
          isLoaded = true
          isLoading = false
          resolve(true)
        }).catch((error) => {
          console.error('高德地图API加载失败:', error)
          isLoading = false
          resolve(false)
        })
      }
      
      loaderScript.onerror = () => {
        console.error('AMapLoader脚本加载失败')
        isLoading = false
        resolve(false)
      }
      
      // 添加到页面
      document.head.appendChild(loaderScript)
      
      // 设置超时
      setTimeout(() => {
        if (isLoading) {
          console.error('高德地图API加载超时')
          isLoading = false
          resolve(false)
        }
      }, 15000) // 15秒超时
      
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

// 百度地图API加载器
let baiduLoadPromise = null
let baiduIsLoading = false
let baiduIsLoaded = false

/**
 * 动态加载百度地图API
 * @returns {Promise<boolean>} 加载是否成功
 */
export function loadBaiduMapAPI() {
  // 如果已经加载过，直接返回结果
  if (baiduIsLoaded) {
    return Promise.resolve(true)
  }
  
  // 如果正在加载，返回现有的Promise
  if (baiduIsLoading && baiduLoadPromise) {
    return baiduLoadPromise
  }
  
  // 检查API密钥
  const apiKey = ENV_CONFIG.BAIDU_MAP_CONFIG.ak
  if (!apiKey || apiKey.trim() === '' || apiKey === 'YOUR_BAIDU_API_KEY') {
    console.warn('百度地图API密钥未配置')
    return Promise.resolve(false)
  }
  
  baiduIsLoading = true
  
  baiduLoadPromise = new Promise((resolve) => {
    try {
      // 创建script标签加载百度地图API - 优化版
      const script = document.createElement('script')
      script.type = 'text/javascript'
      script.async = true // 异步加载，避免阻塞
      script.defer = true // 延迟执行
      // 使用更快的CDN节点和最小依赖
      script.src = `https://api.map.baidu.com/api?v=3.0&ak=${apiKey}&callback=initBMap&s=1&offline=false`
      
      // 设置全局回调函数
      window.initBMap = () => {
        console.log('百度地图API加载成功')
        baiduIsLoaded = true
        baiduIsLoading = false
        resolve(true)
        
        // 清理全局回调
        delete window.initBMap
      }
      
      // 处理加载失败
      script.onerror = () => {
        console.error('百度地图API加载失败')
        baiduIsLoading = false
        resolve(false)
        
        // 清理全局回调
        delete window.initBMap
      }
      
      // 添加到页面
      document.head.appendChild(script)
      
      // 设置超时
      setTimeout(() => {
        if (baiduIsLoading) {
          console.error('百度地图API加载超时')
          baiduIsLoading = false
          resolve(false)
          
          // 清理全局回调
          delete window.initBMap
        }
      }, 10000) // 10秒超时
      
    } catch (error) {
      console.error('加载百度地图API时出错:', error)
      baiduIsLoading = false
      resolve(false)
    }
  })
  
  return baiduLoadPromise
}

/**
 * 检查百度地图API是否可用
 * @returns {boolean}
 */
export function isBaiduMapAvailable() {
  return baiduIsLoaded && window.BMap && typeof window.BMap.Map === 'function'
}
