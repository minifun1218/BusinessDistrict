import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'

// 禁用Vue devtools
if (typeof window !== 'undefined') {
  try {
    // 尝试删除或重写devtools hook
    if (window.__VUE_DEVTOOLS_GLOBAL_HOOK__) {
      window.__VUE_DEVTOOLS_GLOBAL_HOOK__.Vue = undefined
    }
    // 定义一个空的hook对象来阻止devtools
    Object.defineProperty(window, '__VUE_DEVTOOLS_GLOBAL_HOOK__', {
      get() { return undefined },
      set() { /* 阻止设置 */ }
    })
  } catch (e) {
    // 如果设置失败，静默忽略
    console.debug('Vue devtools hook setting failed:', e.message)
  }
}

// 创建Vue应用
const app = createApp(App)

// 禁用Vue devtools和性能追踪
app.config.devtools = false
app.config.performance = false

// 全局错误处理
app.config.errorHandler = (err, vm, info) => {
  if (import.meta.env.PROD) {
    console.error('Production Error:', err)
  } else {
    console.error('Vue Error:', err)
    console.error('Component:', vm)
    console.error('Info:', info)
  }
}

// 生产环境优化
if (import.meta.env.PROD) {
  app.config.warnHandler = () => null
}

app.mount('#app')
