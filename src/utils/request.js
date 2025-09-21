import axios from 'axios'
import { API_CONFIG } from '../config/env.js'

// 创建axios实例
const request = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 在请求发送之前做一些处理
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 添加请求时间戳，防止缓存
    if (config.method === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now(),
      }
    }

    // 显示加载状态（可选）
    if (config.showLoading !== false) {
      // 这里可以触发全局loading状态
      console.log('Request started:', config.url)
    }

    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    // 隐藏加载状态
    console.log('Request completed:', response.config.url)

    const { data } = response

    // 统一处理响应格式
    if (data.code !== undefined) {
      // 后端返回的标准格式: { code: 200, data: {...}, message: 'success' }
      if (data.code === 200 || data.code === 0) {
        return data.data
      } else {
        // 业务错误
        const error = new Error(data.message || '请求失败')
        error.code = data.code
        error.data = data.data
        return Promise.reject(error)
      }
    }

    // 直接返回数据
    return data
  },
  (error) => {
    console.error('Response error:', error)

    // 隐藏加载状态
    if (error.config) {
      console.log('Request failed:', error.config.url)
    }

    // 处理HTTP错误状态码
    if (error.response) {
      const { status, data } = error.response
      let message = '请求失败'

      switch (status) {
        case 400:
          message = data?.message || '请求参数错误'
          break
        case 401:
          message = '未授权，请重新登录'
          // 清除token并跳转到登录页
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          // 这里可以触发全局登录状态重置
          window.location.href = '/login'
          break
        case 403:
          message = '拒绝访问'
          break
        case 404:
          message = '请求的资源不存在'
          break
        case 408:
          message = '请求超时'
          break
        case 429:
          message = '请求过于频繁，请稍后再试'
          break
        case 500:
          message = '服务器内部错误'
          break
        case 502:
          message = '网关错误'
          break
        case 503:
          message = '服务不可用'
          break
        case 504:
          message = '网关超时'
          break
        default:
          message = data?.message || `请求失败 (${status})`
      }

      const customError = new Error(message)
      customError.status = status
      customError.data = data
      return Promise.reject(customError)
    }

    // 网络错误
    if (error.code === 'ECONNABORTED') {
      return Promise.reject(new Error('请求超时，请检查网络连接'))
    }

    if (!window.navigator.onLine) {
      return Promise.reject(new Error('网络连接已断开'))
    }

    return Promise.reject(new Error(error.message || '网络错误'))
  }
)

// 封装常用的请求方法
export const http = {
  get(url, params, config = {}) {
    return request.get(url, { params, ...config })
  },

  post(url, data, config = {}) {
    return request.post(url, data, config)
  },

  put(url, data, config = {}) {
    return request.put(url, data, config)
  },

  patch(url, data, config = {}) {
    return request.patch(url, data, config)
  },

  delete(url, config = {}) {
    return request.delete(url, config)
  },

  // 上传文件
  upload(url, formData, config = {}) {
    return request.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      ...config,
    })
  },

  // 下载文件
  download(url, params, filename, config = {}) {
    return request.get(url, {
      params,
      responseType: 'blob',
      ...config,
    }).then(response => {
      const blob = new Blob([response])
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename || 'download'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
    })
  },
}

// 请求取消令牌
export const CancelToken = axios.CancelToken
export const isCancel = axios.isCancel

// 创建取消令牌
export function createCancelToken() {
  return CancelToken.source()
}

export default request
