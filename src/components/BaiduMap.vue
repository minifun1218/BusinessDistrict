<template>
  <div class="baidu-map-container">
    <!-- 加载状态 -->
    <div v-if="isLoading" class="map-loading">
      <div class="loading-spinner"></div>
      <div class="loading-text">地图加载中...</div>
    </div>

    <!-- 地图控制面板 -->
    <div class="map-controls" v-show="!isLoading">
      <!-- 城市选择器 -->
      <div class="city-selector">
        <label>当前城市：</label>
        <CitySelector v-model="selectedCity" @change="handleCityChange" />
      </div>

      <!-- 搜索框 -->
      <div class="search-box">
        <input
          v-model="searchKeyword"
          @keyup.enter="searchLocation"
          placeholder="搜索地点、商圈..."
          class="modern-input"
        />
        <button @click="searchLocation" class="search-btn modern-btn primary">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
            <path d="m21 21-4.35-4.35" stroke="currentColor" stroke-width="2"/>
          </svg>
          搜索
        </button>
      </div>

      <!-- 搜索半径 -->
      <div class="radius-selector">
        <label>搜索半径：</label>
        <select v-model="searchRadius" @change="onRadiusChange" class="modern-select">
          <option value="500">500米</option>
          <option value="1000">1公里</option>
          <option value="2000">2公里</option>
          <option value="5000">5公里</option>
          <option value="10000">10公里</option>
        </select>
      </div>

      <!-- 工具按钮 -->
      <div class="map-tools">
        <button @click="getCurrentLocation" class="tool-btn modern-btn outline" title="定位当前位置">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
            <path d="M12 1V3" stroke="currentColor" stroke-width="2"/>
            <path d="M12 21V23" stroke="currentColor" stroke-width="2"/>
            <path d="M4.22 4.22L5.64 5.64" stroke="currentColor" stroke-width="2"/>
            <path d="M18.36 18.36L19.78 19.78" stroke="currentColor" stroke-width="2"/>
            <path d="M1 12H3" stroke="currentColor" stroke-width="2"/>
            <path d="M21 12H23" stroke="currentColor" stroke-width="2"/>
            <path d="M4.22 19.78L5.64 18.36" stroke="currentColor" stroke-width="2"/>
            <path d="M18.36 5.64L19.78 4.22" stroke="currentColor" stroke-width="2"/>
          </svg>
        </button>
        <button @click="clearMarkers" class="tool-btn modern-btn outline" title="清除标记">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 6H5H21" stroke="currentColor" stroke-width="2"/>
            <path d="M8 6V4A2 2 0 0110 2H14A2 2 0 0116 4V6M19 6V20A2 2 0 0117 22H7A2 2 0 015 20V6H19Z" stroke="currentColor" stroke-width="2"/>
          </svg>
        </button>
        <button @click="refreshMap" class="tool-btn modern-btn outline" title="刷新地图">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 12A9 9 0 019 3 9.75 9.75 0 0118 6.41V4" stroke="currentColor" stroke-width="2"/>
            <path d="M21 12A9 9 0 0115 21 9.75 9.75 0 016 17.59V20" stroke="currentColor" stroke-width="2"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- 百度地图容器 -->
    <div ref="baiduMapContainer" class="baidu-map" :style="{ height: mapHeight }"></div>

    <!-- 坐标显示 -->
    <div v-if="!isLoading && currentCoords" class="coords-display">
      <span>经度: {{ currentCoords.lng.toFixed(6) }}</span>
      <span>纬度: {{ currentCoords.lat.toFixed(6) }}</span>
    </div>

    <!-- 附近商圈列表 -->
    <div v-if="nearbyBusinessAreas.length > 0" class="nearby-areas-panel">
      <h4>附近商圈 ({{ nearbyBusinessAreas.length }}个)</h4>
      <div class="areas-list">
        <div 
          v-for="area in nearbyBusinessAreas" 
          :key="area.id"
          @click="selectBusinessArea(area)"
          class="area-item"
          :class="{ active: selectedArea?.id === area.id }"
        >
          <div class="area-name">{{ area.name }}</div>
          <div class="area-info">
            <span class="area-distance">{{ area.distance }}米</span>
            <span class="area-type">{{ area.category }}</span>
            <span class="area-hot" :class="getHotClass(area.hotValue)">
              热度{{ area.hotValue }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 选中商圈详情 -->
    <div v-if="selectedArea" class="selected-area-panel modern-card">
      <h4>{{ selectedArea.name }}</h4>
      <div class="area-details">
        <div class="detail-item">
          <span class="label">热度值：</span>
          <span class="value" :class="getHotClass(selectedArea.hotValue)">{{ selectedArea.hotValue }}</span>
        </div>
        <div class="detail-item">
          <span class="label">商家数量：</span>
          <span class="value">{{ selectedArea.storeCount || 'N/A' }}</span>
        </div>
        <div class="detail-item">
          <span class="label">平均消费：</span>
          <span class="value">¥{{ selectedArea.avgConsumption || 'N/A' }}</span>
        </div>
        <div class="detail-item">
          <span class="label">类型：</span>
          <span class="value">{{ selectedArea.category }}</span>
        </div>
        <div class="detail-item" v-if="selectedArea.distance">
          <span class="label">距离：</span>
          <span class="value">{{ selectedArea.distance }}米</span>
        </div>
      </div>
      <button @click="viewAreaDetails" class="modern-btn primary">查看详情</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ENV_CONFIG } from '../config/env.js'
import { loadBaiduMapAPI, isBaiduMapAvailable } from '../utils/mapLoader.js'
import CitySelector from './CitySelector.vue'

// Props
const props = defineProps({
  modelValue: { type: Object, default: () => ({ lng: 116.4074, lat: 39.9042 }) },
  height: { type: String, default: '500px' },
  businessAreas: { type: Array, default: () => [] },
  currentCity: { type: Object, default: () => ({ id: 'beijing', name: '北京' }) }
})

// Emits
const emit = defineEmits(['update:modelValue', 'area-selected', 'location-changed', 'city-changed'])

// 响应式数据
const baiduMapContainer = ref(null)
const map = ref(null)
const markers = ref([])
const searchKeyword = ref('')
const searchRadius = ref(1000)
const selectedArea = ref(null)
const mapHeight = ref(props.height)
const selectedCity = ref(props.currentCity)
const isLoading = ref(true)
const hasInitialized = ref(false)
const currentCoords = ref(props.modelValue)
const nearbyBusinessAreas = ref([])

let resizeHandler = null
let localSearchInstance = null

// 节流函数
const throttle = (fn, wait = 200) => {
  let last = 0, timer = null
  return (...args) => {
    const now = Date.now()
    if (now - last >= wait) {
      last = now
      fn(...args)
    } else {
      clearTimeout(timer)
      timer = setTimeout(() => {
        last = Date.now()
        fn(...args)
      }, wait - (now - last))
    }
  }
}

// 快速初始化
const quickInit = async () => {
  if (hasInitialized.value) return
  
  try {
    // 检查API是否已加载
    if (window.BMap && isBaiduMapAvailable()) {
      initBaiduMap()
      return
    }
    
    // 加载百度地图API
    const loadSuccess = await loadBaiduMapAPI()
    if (loadSuccess && isBaiduMapAvailable()) {
      requestAnimationFrame(() => initBaiduMap())
    } else {
      showMapPlaceholder('API加载失败')
    }
  } catch (e) {
    console.error('地图API加载错误:', e)
    showMapPlaceholder('API加载出错')
  }
}

// 地图初始化
const initBaiduMap = () => {
  if (!baiduMapContainer.value) return
  if (!ENV_CONFIG.BAIDU_MAP_CONFIG.ak) {
    showMapPlaceholder('API密钥未配置')
    return
  }
  if (!window.BMap?.Map) {
    showMapPlaceholder('API未就绪')
    return
  }

  try {
    const container = baiduMapContainer.value
    container.innerHTML = ''
    
    // 创建地图实例
    map.value = new window.BMap.Map(container, {
      enableMapClick: true,
      minZoom: 4,
      maxZoom: 18
    })

    const center = new window.BMap.Point(props.modelValue.lng, props.modelValue.lat)
    map.value.centerAndZoom(center, ENV_CONFIG.BAIDU_MAP_CONFIG.defaultZoom || 11)

    // 启用地图功能
    map.value.enableScrollWheelZoom(true)
    map.value.enableContinuousZoom(true)
    map.value.enableInertialDragging(true)

    // 添加控件
    map.value.addControl(new window.BMap.NavigationControl())
    map.value.addControl(new window.BMap.ScaleControl())
    map.value.addControl(new window.BMap.OverviewMapControl())
    map.value.addControl(new window.BMap.MapTypeControl())

    // 地图事件监听
    map.value.addEventListener('click', handleMapClick)
    map.value.addEventListener('moveend', handleMapMoveEnd)

    // 加载初始商圈数据
    if (props.businessAreas.length > 0) {
      loadBusinessAreaMarkers()
    }

    // 窗口大小调整监听
    const onResize = throttle(() => map.value?.checkResize(), 300)
    resizeHandler = onResize
    window.addEventListener('resize', onResize, { passive: true })

    hasInitialized.value = true
    isLoading.value = false

    console.log('百度地图初始化成功')

  } catch (error) {
    console.error('地图初始化失败:', error)
    showMapPlaceholder('地图初始化失败')
  }
}

// 显示占位符
const showMapPlaceholder = (reason = '地图加载失败') => {
  isLoading.value = false
  if (!baiduMapContainer.value) return
  baiduMapContainer.value.innerHTML = `
    <div style="
      width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
      background: #f5f5f5; border: 1px dashed #d9d9d9; color: #666; font-size: 14px;
      text-align: center; flex-direction: column; padding: 20px; box-sizing: border-box;
    ">
      <div style="margin-bottom: 10px; font-size: 24px;">🗺️</div>
      <div style="font-weight: bold; margin-bottom: 8px;">${reason}</div>
      <div style="font-size: 12px; color: #999;">请检查网络连接或联系管理员</div>
    </div>
  `
}

// 地图点击事件
const handleMapClick = (e) => {
  const point = e.point
  const coords = { lng: point.lng, lat: point.lat }
  
  currentCoords.value = coords
  emit('update:modelValue', coords)
  emit('location-changed', coords)
  
  // 添加点击标记
  addClickMarker(point)
  
  // 搜索附近商圈
  searchNearbyBusinessAreas(point)
}

// 地图移动结束事件
const handleMapMoveEnd = throttle(() => {
  if (!map.value) return
  const center = map.value.getCenter()
  const coords = { lng: center.lng, lat: center.lat }
  currentCoords.value = coords
  emit('update:modelValue', coords)
}, 200)

// 添加点击标记
const addClickMarker = (point) => {
  if (!map.value) return
  
  // 清除之前的点击标记
  markers.value = markers.value.filter(marker => {
    if (marker.isClickMarker) {
      map.value.removeOverlay(marker)
      return false
    }
    return true
  })
  
  // 创建新标记
  const marker = new window.BMap.Marker(point)
  marker.isClickMarker = true
  map.value.addOverlay(marker)
  markers.value.push(marker)
  
  // 添加信息窗口
  const infoWindow = new window.BMap.InfoWindow(`
    <div style="padding: 10px; min-width: 200px;">
      <h4 style="margin: 0 0 10px 0;">选中位置</h4>
      <p style="margin: 5px 0;">经度: ${point.lng.toFixed(6)}</p>
      <p style="margin: 5px 0;">纬度: ${point.lat.toFixed(6)}</p>
      <button onclick="searchNearby()" style="margin-top: 10px; padding: 5px 10px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer;">搜索附近商圈</button>
    </div>
  `)
  
  marker.addEventListener('click', () => {
    map.value.openInfoWindow(infoWindow, point)
  })
}

// 加载商圈标记
const loadBusinessAreaMarkers = () => {
  if (!map.value || !props.businessAreas.length) return

  // 清除旧的商圈标记
  markers.value = markers.value.filter(m => {
    if (!m.isClickMarker) {
      map.value.removeOverlay(m)
      return false
    }
    return true
  })

  // 根据缩放级别限制显示数量
  const currentZoom = map.value.getZoom()
  const maxMarkers = currentZoom < 12 ? 20 : 50
  
  let filteredAreas = props.businessAreas
  if (currentZoom < 12) {
    // 低缩放时只显示热门商圈
    filteredAreas = props.businessAreas
      .filter(a => a.hotValue > 60)
      .slice(0, maxMarkers)
  } else {
    filteredAreas = props.businessAreas.slice(0, maxMarkers)
  }

  // 图标缓存
  const iconCache = {
    hot: new window.BMap.Icon('/icons/marker-hot.png', new window.BMap.Size(25, 35), {
      imageOffset: new window.BMap.Size(0, 0)
    }),
    warm: new window.BMap.Icon('/icons/marker-warm.png', new window.BMap.Size(25, 35), {
      imageOffset: new window.BMap.Size(0, 0)
    }),
    cool: new window.BMap.Icon('/icons/marker-cool.png', new window.BMap.Size(25, 35), {
      imageOffset: new window.BMap.Size(0, 0)
    })
  }

  // 创建标记
  filteredAreas.forEach(area => {
    const point = new window.BMap.Point(area.longitude, area.latitude)
    let iconKey = 'cool'
    if (area.hotValue > 80) iconKey = 'hot'
    else if (area.hotValue > 50) iconKey = 'warm'
    
    const marker = new window.BMap.Marker(point, { icon: iconCache[iconKey] })
    
    marker.addEventListener('click', () => {
      selectBusinessArea(area)
      
      const infoWindow = new window.BMap.InfoWindow(`
        <div style="padding: 15px; min-width: 200px;">
          <h4 style="margin: 0 0 10px 0; color: #333;">${area.name}</h4>
          <p style="margin: 5px 0;"><strong>热度值:</strong> ${area.hotValue}</p>
          <p style="margin: 5px 0;"><strong>类型:</strong> ${area.category}</p>
          <p style="margin: 5px 0;"><strong>商家数量:</strong> ${area.storeCount || 'N/A'}</p>
          <button onclick="viewDetails('${area.id}')" style="margin-top: 10px; padding: 8px 16px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer;">查看详情</button>
        </div>
      `)
      
      map.value.openInfoWindow(infoWindow, point)
    })
    
    map.value.addOverlay(marker)
    markers.value.push(marker)
  })
}

// 搜索位置
const searchLocation = async () => {
  if (!searchKeyword.value.trim() || !map.value) return

  try {
    if (!localSearchInstance) {
      localSearchInstance = new window.BMap.LocalSearch(map.value, {
        onSearchComplete: (results) => {
          if (localSearchInstance.getStatus() === window.BMAP_STATUS_SUCCESS) {
            const poi = results.getPoi(0)
            if (poi) {
              const point = poi.point
              map.value.centerAndZoom(point, 15)
              
              // 添加搜索结果标记
              const marker = new window.BMap.Marker(point)
              map.value.addOverlay(marker)
              markers.value.push(marker)
              
              const coords = { lng: point.lng, lat: point.lat }
              currentCoords.value = coords
              emit('update:modelValue', coords)
              emit('location-changed', coords)
              
              // 搜索附近商圈
              searchNearbyBusinessAreas(point)
            }
          }
        }
      })
    }
    
    localSearchInstance.search(searchKeyword.value)
  } catch (error) {
    console.error('搜索失败:', error)
  }
}

// 搜索附近商圈
const searchNearbyBusinessAreas = async (point) => {
  try {
    // 模拟API调用 - 这里你需要替换为实际的API调用
    const mockNearbyAreas = generateMockNearbyAreas(point)
    nearbyBusinessAreas.value = mockNearbyAreas
    
    // 通知父组件
    emit('location-changed', {
      lng: point.lng,
      lat: point.lat,
      nearbyAreas: mockNearbyAreas
    })
    
    console.log(`搜索到 ${mockNearbyAreas.length} 个附近商圈`)
  } catch (error) {
    console.error('搜索附近商圈失败:', error)
  }
}

// 生成模拟附近商圈数据
const generateMockNearbyAreas = (centerPoint) => {
  const mockAreas = [
    { id: '1', name: '王府井商业街', category: '购物中心', hotValue: 95 },
    { id: '2', name: '西单大悦城', category: '购物中心', hotValue: 88 },
    { id: '3', name: '三里屯太古里', category: '时尚街区', hotValue: 92 },
    { id: '4', name: '国贸商城', category: '高端商场', hotValue: 90 },
    { id: '5', name: '朝阳大悦城', category: '购物中心', hotValue: 82 },
    { id: '6', name: '蓝色港湾', category: '休闲商区', hotValue: 75 },
    { id: '7', name: '五道口购物中心', category: '学院商圈', hotValue: 70 },
    { id: '8', name: '中关村广场', category: '科技商圈', hotValue: 78 }
  ]
  
  return mockAreas.map(area => {
    // 计算随机距离
    const distance = Math.floor(Math.random() * parseInt(searchRadius.value)) + 100
    
    return {
      ...area,
      longitude: centerPoint.lng + (Math.random() - 0.5) * 0.02,
      latitude: centerPoint.lat + (Math.random() - 0.5) * 0.02,
      distance,
      storeCount: Math.floor(Math.random() * 200) + 50,
      avgConsumption: Math.floor(Math.random() * 300) + 100
    }
  }).filter(area => area.distance <= parseInt(searchRadius.value))
    .sort((a, b) => a.distance - b.distance)
}

// 选择商圈
const selectBusinessArea = (area) => {
  selectedArea.value = area
  emit('area-selected', area)
  
  if (map.value) {
    const point = new window.BMap.Point(area.longitude, area.latitude)
    map.value.panTo(point)
  }
}

// 获取当前位置
const getCurrentLocation = () => {
  if (!map.value) return
  
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const point = new window.BMap.Point(position.coords.longitude, position.coords.latitude)
        map.value.centerAndZoom(point, 15)
        
        const marker = new window.BMap.Marker(point)
        map.value.addOverlay(marker)
        markers.value.push(marker)
        
        const coords = { lng: point.lng, lat: point.lat }
        currentCoords.value = coords
        emit('update:modelValue', coords)
        
        // 搜索附近商圈
        searchNearbyBusinessAreas(point)
      },
      (error) => {
        console.error('定位失败:', error)
        alert('定位失败，请检查浏览器定位权限')
      }
    )
  } else {
    alert('浏览器不支持地理定位')
  }
}

// 清除标记
const clearMarkers = () => {
  if (!map.value) return
  
  markers.value.forEach(marker => map.value.removeOverlay(marker))
  markers.value = []
  selectedArea.value = null
  nearbyBusinessAreas.value = []
}

// 刷新地图
const refreshMap = throttle(() => {
  if (map.value) {
    map.value.checkResize()
    const center = map.value.getCenter()
    map.value.panTo(center)
  }
}, 300)

// 城市变化处理
const handleCityChange = (city) => {
  selectedCity.value = city
  emit('city-changed', city)
  updateMapCenterForCity(city)
}

// 根据城市更新地图中心点
const updateMapCenterForCity = (city) => {
  if (!map.value) return
  
  const cityCoords = {
    'beijing': { lng: 116.4074, lat: 39.9042 },
    'shanghai': { lng: 121.4737, lat: 31.2304 },
    'guangzhou': { lng: 113.2644, lat: 23.1291 },
    'shenzhen': { lng: 114.0579, lat: 22.5431 },
    'hangzhou': { lng: 120.1614, lat: 30.2936 },
    'nanjing': { lng: 118.7969, lat: 32.0603 },
    'wuhan': { lng: 114.2734, lat: 30.5801 },
    'chengdu': { lng: 104.0668, lat: 30.5728 }
  }
  
  const coords = cityCoords[city.id] || cityCoords['beijing']
  const point = new window.BMap.Point(coords.lng, coords.lat)
  
  map.value.centerAndZoom(point, ENV_CONFIG.BAIDU_MAP_CONFIG.defaultZoom || 11)
  currentCoords.value = coords
  emit('update:modelValue', coords)
  
  // 清除之前的搜索结果
  nearbyBusinessAreas.value = []
  selectedArea.value = null
}

// 搜索半径变化
const onRadiusChange = throttle(() => {
  if (currentCoords.value) {
    const point = new window.BMap.Point(currentCoords.value.lng, currentCoords.value.lat)
    searchNearbyBusinessAreas(point)
  }
}, 500)

// 查看区域详情
const viewAreaDetails = () => {
  if (selectedArea.value) {
    emit('area-selected', selectedArea.value)
  }
}

// 获取热度等级样式类
const getHotClass = (hotValue) => {
  if (hotValue > 80) return 'hot'
  if (hotValue > 50) return 'warm'
  return 'cool'
}

// 监听商圈数据变化
watch(() => props.businessAreas, () => {
  if (map.value) {
    loadBusinessAreaMarkers()
  }
}, { deep: true })

// 监听中心点变化
watch(() => props.modelValue, (newCenter) => {
  if (map.value && newCenter) {
    const point = new window.BMap.Point(newCenter.lng, newCenter.lat)
    map.value.panTo(point)
    currentCoords.value = newCenter
  }
}, { deep: true })

// 生命周期
onMounted(() => {
  mapHeight.value = props.height
  currentCoords.value = props.modelValue
  
  // 立即初始化
  nextTick(() => {
    quickInit()
  })
  
  // 暴露全局函数（供InfoWindow使用）
  window.searchNearby = () => {
    if (currentCoords.value) {
      const point = new window.BMap.Point(currentCoords.value.lng, currentCoords.value.lat)
      searchNearbyBusinessAreas(point)
    }
  }
  
  window.viewDetails = (areaId) => {
    const area = nearbyBusinessAreas.value.find(a => a.id === areaId) || 
                  props.businessAreas.find(a => a.id === areaId)
    if (area) {
      selectBusinessArea(area)
    }
  }
})

onUnmounted(() => {
  try {
    if (map.value) {
      map.value.removeEventListener('click', handleMapClick)
      map.value.removeEventListener('moveend', handleMapMoveEnd)
    }
  } catch {}
  
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler)
    resizeHandler = null
  }
  
  // 清理全局函数
  delete window.searchNearby
  delete window.viewDetails
})
</script>

<style scoped>
.baidu-map-container {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 16px;
  overflow: hidden;
  background: #f5f5f5;
}

/* 加载状态 */
.map-loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  z-index: 1000;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

.loading-text {
  color: #64748b;
  font-size: 14px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 控制面板 */
.map-controls {
  position: absolute;
  top: 15px;
  left: 15px;
  right: 15px;
  display: flex;
  gap: 12px;
  align-items: center;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 12px 16px;
  border-radius: 12px;
  z-index: 1000;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  flex-wrap: wrap;
}

.city-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #374151;
  white-space: nowrap;
}

.city-selector label {
  font-weight: 500;
}

.search-box {
  display: flex;
  gap: 8px;
  flex: 1;
  min-width: 240px;
}

.modern-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.modern-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.modern-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
}

.modern-btn.primary {
  background: #667eea;
  color: white;
}

.modern-btn.primary:hover {
  background: #5a67d8;
}

.modern-btn.outline {
  background: white;
  color: #6b7280;
  border: 1px solid #d1d5db;
}

.modern-btn.outline:hover {
  background: #f9fafb;
  color: #374151;
}

.radius-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #374151;
}

.modern-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: white;
  font-size: 14px;
  outline: none;
}

.map-tools {
  display: flex;
  gap: 8px;
}

.tool-btn {
  padding: 8px;
  min-width: auto;
}

/* 地图容器 */
.baidu-map {
  width: 100%;
  height: 100%;
  min-height: 400px;
  border-radius: 16px;
  position: relative;
}

/* 坐标显示 */
.coords-display {
  position: absolute;
  bottom: 15px;
  left: 15px;
  background: rgba(255, 255, 255, 0.95);
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  color: #6b7280;
  z-index: 1000;
  display: flex;
  gap: 16px;
}

/* 附近商圈面板 */
.nearby-areas-panel {
  position: absolute;
  top: 80px;
  right: 15px;
  width: 300px;
  max-height: 400px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 16px;
  z-index: 1000;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.nearby-areas-panel h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #111827;
}

.areas-list {
  max-height: 320px;
  overflow-y: auto;
}

.area-item {
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.area-item:hover {
  background: #f9fafb;
  border-color: #667eea;
}

.area-item.active {
  background: #eef2ff;
  border-color: #667eea;
}

.area-name {
  font-weight: 500;
  color: #111827;
  margin-bottom: 4px;
}

.area-info {
  display: flex;
  gap: 8px;
  font-size: 12px;
}

.area-distance {
  color: #6b7280;
}

.area-type {
  color: #6b7280;
}

.area-hot {
  font-weight: 500;
}

.area-hot.hot {
  color: #dc2626;
}

.area-hot.warm {
  color: #ea580c;
}

.area-hot.cool {
  color: #2563eb;
}

/* 选中商圈详情 */
.selected-area-panel {
  position: absolute;
  bottom: 15px;
  right: 15px;
  width: 280px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 20px;
  z-index: 1000;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.selected-area-panel h4 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #111827;
}

.area-details {
  margin-bottom: 16px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.detail-item .label {
  color: #6b7280;
}

.detail-item .value {
  color: #111827;
  font-weight: 500;
}

.detail-item .value.hot {
  color: #dc2626;
}

.detail-item .value.warm {
  color: #ea580c;
}

.detail-item .value.cool {
  color: #2563eb;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .map-controls {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .search-box {
    min-width: auto;
  }
  
  .nearby-areas-panel {
    width: 250px;
  }
  
  .selected-area-panel {
    width: 250px;
  }
}

@media (max-width: 768px) {
  .map-controls {
    left: 10px;
    right: 10px;
    padding: 12px;
  }
  
  .nearby-areas-panel {
    top: auto;
    bottom: 80px;
    right: 10px;
    left: 10px;
    width: auto;
    max-height: 200px;
  }
  
  .selected-area-panel {
    bottom: 10px;
    right: 10px;
    left: 10px;
    width: auto;
  }
  
  .coords-display {
    bottom: 10px;
    left: 10px;
    font-size: 11px;
  }
}
</style>
