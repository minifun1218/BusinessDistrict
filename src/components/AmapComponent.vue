<template>
  <div class="amap-container">
    <!-- 地图控制面板 -->
    <div class="map-controls">
      <!-- 城市选择器 -->
      <div class="city-selector">
        <label>当前城市：</label>
        <CitySelector v-model="selectedCity" @change="handleCityChange" />
      </div>
      
      <div class="search-box">
        <input 
          v-model="searchKeyword" 
          @keyup.enter="searchLocation"
          placeholder="搜索地点..." 
          class="modern-input"
        />
        <button @click="searchLocation" class="search-btn modern-btn primary">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
            <path d="m21 21-4.35-4.35" stroke="currentColor" stroke-width="2"/>
          </svg>
        </button>
      </div>
      
      <div class="distance-selector">
        <label>搜索半径：</label>
        <select v-model="searchRadius" @change="updateSearchRadius" class="modern-select">
          <option value="500">500米</option>
          <option value="1000">1公里</option>
          <option value="2000">2公里</option>
          <option value="5000">5公里</option>
          <option value="10000">10公里</option>
        </select>
      </div>
      
      <div class="map-tools">
        <button @click="getCurrentLocation" class="tool-btn modern-btn outline" title="定位到当前位置">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C13.1046 2 14 2.89543 14 4C14 5.10457 13.1046 6 12 6C10.8954 6 10 5.10457 10 4C10 2.89543 10.8954 2 12 2Z" fill="currentColor"/>
            <path d="M12 18C13.1046 18 14 18.8954 14 20C14 21.1046 13.1046 22 12 22C10.8954 22 10 21.1046 10 20C10 18.8954 10.8954 18 12 18Z" fill="currentColor"/>
            <path d="M6 12C6 10.8954 5.10457 10 4 10C2.89543 10 2 10.8954 2 12C2 13.1046 2.89543 14 4 14C5.10457 14 6 13.1046 6 12Z" fill="currentColor"/>
            <path d="M22 12C22 10.8954 21.1046 10 20 10C18.8954 10 18 10.8954 18 12C18 13.1046 18.8954 14 20 14C21.1046 14 22 13.1046 22 12Z" fill="currentColor"/>
          </svg>
        </button>
        <button @click="clearMarkers" class="tool-btn modern-btn outline" title="清除标记">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 6H5H21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6H19Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
    
    <!-- 高德地图容器 -->
    <div ref="amapContainer" class="amap" :style="{ height: mapHeight }"></div>
    
    <!-- 地图图例 -->
    <div class="map-legend">
      <div class="legend-item">
        <span class="legend-marker hot"></span>
        <span>热门商圈 (热度 > 80)</span>
      </div>
      <div class="legend-item">
        <span class="legend-marker warm"></span>
        <span>一般商圈 (热度 50-80)</span>
      </div>
      <div class="legend-item">
        <span class="legend-marker cool"></span>
        <span>冷门商圈 (热度 < 50)</span>
      </div>
      <div class="legend-item">
        <span class="legend-marker selected"></span>
        <span>已选择区域</span>
      </div>
    </div>
    
    <!-- 选中区域信息面板 -->
    <div v-if="selectedArea" class="area-info-panel modern-card fade-in-scale">
      <h4>{{ selectedArea.name }}</h4>
      <div class="area-stats">
        <div class="stat-item">
          <span class="label">热度值：</span>
          <span class="value">{{ selectedArea.hotValue }}</span>
        </div>
        <div class="stat-item">
          <span class="label">商家数量：</span>
          <span class="value">{{ selectedArea.storeCount }}</span>
        </div>
        <div class="stat-item">
          <span class="label">平均消费：</span>
          <span class="value">¥{{ selectedArea.avgConsumption }}</span>
        </div>
        <div class="stat-item">
          <span class="label">类型：</span>
          <span class="value">{{ selectedArea.category }}</span>
        </div>
      </div>
      <button @click="viewAreaDetails" class="modern-btn primary">查看详情</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ENV_CONFIG } from '../config/env.js'
import { loadAmapAPI, isAmapAvailable } from '../utils/mapLoader.js'
import CitySelector from './CitySelector.vue'

// Props
const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({ lng: 116.4074, lat: 39.9042 })
  },
  height: {
    type: String,
    default: '500px'
  },
  businessAreas: {
    type: Array,
    default: () => []
  },
  currentCity: {
    type: Object,
    default: () => ({ id: 'beijing', name: '北京' })
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'area-selected', 'location-changed', 'city-changed'])

// 响应式数据
const amapContainer = ref(null)
const map = ref(null)
const markers = ref([])
const searchKeyword = ref('')
const searchRadius = ref(1000)
const selectedArea = ref(null)
const mapHeight = ref(props.height)
const selectedCity = ref(props.currentCity)

// 地图初始化
const initAmap = () => {
  console.log('开始初始化高德地图...')
  console.log('API密钥:', ENV_CONFIG.AMAP_CONFIG.key ? '已配置' : '未配置')
  
  // 检查DOM元素
  if (!amapContainer.value) {
    console.error('地图容器DOM元素未找到，延迟重试...')
    setTimeout(() => initAmap(), 200)
    return
  }

  // 检查API密钥
  if (!ENV_CONFIG.AMAP_CONFIG.key || ENV_CONFIG.AMAP_CONFIG.key.trim() === '') {
    console.warn('高德地图API密钥未配置，显示占位符')
    showMapPlaceholder()
    return
  }

  // 检查高德地图API
  if (!window.AMap) {
    console.error('高德地图API未加载，显示占位符')
    showMapPlaceholder()
    return
  }

  try {
    console.log('创建地图实例...')
    
    // 清空容器内容
    if (amapContainer.value) {
      amapContainer.value.innerHTML = ''
    }

    // 创建地图实例
    map.value = new window.AMap.Map(amapContainer.value, {
      zoom: ENV_CONFIG.AMAP_CONFIG.defaultZoom,
      center: ENV_CONFIG.AMAP_CONFIG.defaultCenter,
      mapStyle: 'amap://styles/normal',
      features: ['bg', 'road', 'building', 'point']
    })
    
    // 添加地图控件
    const toolbar = new window.AMap.ToolBar()
    const scale = new window.AMap.Scale()
    const mapType = new window.AMap.MapType()
    
    map.value.addControl(toolbar)
    map.value.addControl(scale)
    map.value.addControl(mapType)
    
    // 添加地图点击事件
    map.value.on('click', handleMapClick)
    
    // 添加地图移动事件
    map.value.on('moveend', handleMapMoveEnd)
    
    // 加载商圈标记
    loadBusinessAreaMarkers()
    
    console.log('高德地图初始化成功')
  } catch (error) {
    console.error('高德地图初始化失败:', error)
    showMapPlaceholder('地图初始化失败')
  }
}

// 显示地图占位符
const showMapPlaceholder = (reason = '高德地图API密钥未配置') => {
  if (amapContainer.value) {
    let message = ''
    let instruction = ''
    
    if (reason === 'API密钥授权失败') {
      message = '高德地图API密钥授权失败'
      instruction = '请检查API密钥是否正确，并确保已在高德开放平台中启用Web服务API'
    } else if (reason === '地图初始化失败') {
      message = '地图初始化失败'
      instruction = '请检查网络连接和API密钥配置'
    } else {
      message = reason
      instruction = '请在 src/config/env.js 中配置正确的 AMAP_CONFIG.key'
    }
    
    amapContainer.value.innerHTML = `
      <div style="
        width: 100%; 
        height: 100%; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        background: #f5f5f5;
        border: 1px dashed #d9d9d9;
        color: #666;
        font-size: 14px;
        text-align: center;
        flex-direction: column;
        padding: 20px;
        box-sizing: border-box;
      ">
        <div style="margin-bottom: 10px; font-size: 24px;">🗺️</div>
        <div style="font-weight: bold; margin-bottom: 8px;">${message}</div>
        <div style="font-size: 12px; color: #999; line-height: 1.4; max-width: 300px;">
          ${instruction}
        </div>
        <div style="font-size: 12px; color: #999; margin-top: 10px;">
          系统其他功能不受影响
        </div>
      </div>
    `
  }
}

// 地图点击事件处理
const handleMapClick = (e) => {
  const lnglat = e.lnglat
  console.log('地图点击坐标:', lnglat.getLng(), lnglat.getLat())
  
  // 更新选中位置
  emit('update:modelValue', { lng: lnglat.getLng(), lat: lnglat.getLat() })
  emit('location-changed', { lng: lnglat.getLng(), lat: lnglat.getLat() })
  
  // 在点击位置添加标记
  addClickMarker(lnglat)
  
  // 搜索附近的商圈
  searchNearbyBusinessAreas(lnglat)
}

// 地图移动结束事件
const handleMapMoveEnd = () => {
  const center = map.value.getCenter()
  emit('update:modelValue', { lng: center.getLng(), lat: center.getLat() })
}

// 添加点击标记
const addClickMarker = (lnglat) => {
  if (!map.value) return
  
  // 清除之前的点击标记
  markers.value.forEach(marker => {
    if (marker.isClickMarker) {
      map.value.remove(marker)
    }
  })
  
  // 创建新的点击标记
  const marker = new window.AMap.Marker({
    position: lnglat,
    title: '选中位置'
  })
  marker.isClickMarker = true
  map.value.add(marker)
  
  // 添加到标记数组
  markers.value.push(marker)
  
  // 创建信息窗口
  const infoWindow = new window.AMap.InfoWindow({
    content: `
      <div style="padding: 10px;">
        <h4>选中位置</h4>
        <p>经度: ${lnglat.getLng().toFixed(6)}</p>
        <p>纬度: ${lnglat.getLat().toFixed(6)}</p>
        <button onclick="searchNearby()" style="margin-top: 10px; padding: 5px 10px; background: #667eea; color: white; border: none; border-radius: 4px;">搜索附近商圈</button>
      </div>
    `
  })
  
  marker.on('click', () => {
    infoWindow.open(map.value, lnglat)
  })
}

// 加载商圈标记
const loadBusinessAreaMarkers = () => {
  if (!map.value || !props.businessAreas.length) return
  
  props.businessAreas.forEach(area => {
    const position = [area.longitude, area.latitude]
    
    // 根据热度值选择颜色
    let color = '#2196f3' // 默认蓝色（冷门）
    if (area.hotValue > 80) {
      color = '#ff4444' // 红色（热门）
    } else if (area.hotValue > 50) {
      color = '#ff9800' // 橙色（一般）
    }
    
    // 创建标记
    const marker = new window.AMap.Marker({
      position: position,
      title: area.name,
      icon: new window.AMap.Icon({
        size: new window.AMap.Size(25, 35),
        image: `data:image/svg+xml;base64,${btoa(`
          <svg width="25" height="35" xmlns="http://www.w3.org/2000/svg">
            <path d="M12.5 0C5.6 0 0 5.6 0 12.5c0 12.5 12.5 22.5 12.5 22.5s12.5-10 12.5-22.5C25 5.6 19.4 0 12.5 0z" fill="${color}"/>
            <circle cx="12.5" cy="12.5" r="6" fill="white"/>
          </svg>
        `)}`
      })
    })
    
    // 添加点击事件
    marker.on('click', () => {
      selectBusinessArea(area)
      
      // 显示信息窗口
      const infoWindow = new window.AMap.InfoWindow({
        content: `
          <div style="padding: 15px; min-width: 200px;">
            <h4 style="margin: 0 0 10px 0; color: #333;">${area.name}</h4>
            <p style="margin: 5px 0;"><strong>热度值:</strong> ${area.hotValue}</p>
            <p style="margin: 5px 0;"><strong>商家数量:</strong> ${area.storeCount}</p>
            <p style="margin: 5px 0;"><strong>平均消费:</strong> ¥${area.avgConsumption}</p>
            <p style="margin: 5px 0;"><strong>类型:</strong> ${area.category}</p>
            <button onclick="viewDetails('${area.id}')" style="margin-top: 10px; padding: 8px 16px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer;">查看详情</button>
          </div>
        `
      })
      
      infoWindow.open(map.value, position)
    })
    
    map.value.add(marker)
    markers.value.push(marker)
  })
}

// 选择商圈
const selectBusinessArea = (area) => {
  selectedArea.value = area
  emit('area-selected', area)
  
  // 移动地图到选中区域
  map.value.setCenter([area.longitude, area.latitude])
}

// 搜索位置
const searchLocation = () => {
  if (!searchKeyword.value.trim()) return
  
  window.AMap.plugin('AMap.PlaceSearch', () => {
    const placeSearch = new window.AMap.PlaceSearch({
      pageSize: 10,
      pageIndex: 1,
      city: selectedCity.value.name
    })
    
    placeSearch.search(searchKeyword.value, (status, result) => {
      if (status === 'complete' && result.poiList && result.poiList.pois.length > 0) {
        const poi = result.poiList.pois[0]
        const position = [poi.location.lng, poi.location.lat]
        
        map.value.setCenter(position)
        map.value.setZoom(15)
        
        // 添加搜索结果标记
        const marker = new window.AMap.Marker({
          position: position,
          title: poi.name
        })
        map.value.add(marker)
        markers.value.push(marker)
        
        // 更新选中位置
        emit('update:modelValue', { lng: poi.location.lng, lat: poi.location.lat })
        emit('location-changed', { lng: poi.location.lng, lat: poi.location.lat })
      }
    })
  })
}

// 获取当前位置
const getCurrentLocation = () => {
  window.AMap.plugin('AMap.Geolocation', () => {
    const geolocation = new window.AMap.Geolocation({
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0,
      convert: true,
      showButton: true,
      buttonPosition: 'LB',
      showMarker: true,
      showCircle: true,
      panToLocation: true,
      zoomToAccuracy: true
    })
    
    geolocation.getCurrentPosition((status, result) => {
      if (status === 'complete') {
        const position = result.position
        emit('update:modelValue', { lng: position.lng, lat: position.lat })
      } else {
        console.error('获取位置失败:', result)
        alert('获取位置失败，请检查浏览器定位权限')
      }
    })
  })
}

// 清除标记
const clearMarkers = () => {
  markers.value.forEach(marker => {
    map.value.remove(marker)
  })
  markers.value = []
  selectedArea.value = null
}

// 更新搜索半径
const updateSearchRadius = () => {
  // 如果有选中的位置，重新搜索附近商圈
  if (selectedArea.value) {
    const lnglat = new window.AMap.LngLat(selectedArea.value.longitude, selectedArea.value.latitude)
    searchNearbyBusinessAreas(lnglat)
  }
}

// 搜索附近商圈
const searchNearbyBusinessAreas = async (lnglat) => {
  try {
    console.log('搜索附近商圈:', lnglat.getLng(), lnglat.getLat(), searchRadius.value)
    
    // 调用业务API搜索附近商圈
    const { businessApi } = await import('../api/business.js')
    const nearbyAreas = await businessApi.searchNearbyBusinessAreas({
      longitude: lnglat.getLng(),
      latitude: lnglat.getLat(),
      radius: searchRadius.value
    })
    
    console.log('搜索到附近商圈:', nearbyAreas)
    
    // 通知父组件更新商圈数据
    emit('location-changed', { 
      lng: lnglat.getLng(), 
      lat: lnglat.getLat(),
      nearbyAreas: nearbyAreas || []
    })
    
  } catch (error) {
    console.error('搜索附近商圈失败:', error)
  }
}

// 查看区域详情
const viewAreaDetails = () => {
  if (selectedArea.value) {
    emit('area-selected', selectedArea.value)
  }
}

// 城市变化处理
const handleCityChange = (city) => {
  selectedCity.value = city
  emit('city-changed', city)
  
  // 更新地图中心点到新城市
  updateMapCenterForCity(city)
}

// 根据城市更新地图中心点
const updateMapCenterForCity = (city) => {
  if (!map.value) return
  
  const cityCoords = {
    'beijing': [116.4074, 39.9042],
    'shanghai': [121.4737, 31.2304],
    'guangzhou': [113.2644, 23.1291],
    'shenzhen': [114.0579, 22.5431],
    'hangzhou': [120.1614, 30.2936],
    'nanjing': [118.7969, 32.0603],
    'wuhan': [114.2734, 30.5801],
    'chengdu': [104.0668, 30.5728]
  }
  
  const coords = cityCoords[city.id] || cityCoords['beijing']
  
  map.value.setCenter(coords)
  map.value.setZoom(ENV_CONFIG.AMAP_CONFIG.defaultZoom)
  emit('update:modelValue', { lng: coords[0], lat: coords[1] })
}

// 监听商圈数据变化
watch(() => props.businessAreas, () => {
  if (map.value) {
    // 清除现有商圈标记
    markers.value.forEach(marker => {
      if (!marker.isClickMarker) {
        map.value.remove(marker)
      }
    })
    markers.value = markers.value.filter(marker => marker.isClickMarker)
    
    // 重新加载商圈标记
    loadBusinessAreaMarkers()
  }
}, { deep: true })

// 监听中心点变化
watch(() => props.modelValue, (newCenter) => {
  if (map.value && newCenter) {
    map.value.setCenter([newCenter.lng, newCenter.lat])
  }
}, { deep: true })

// 生命周期
onMounted(async () => {
  console.log('AmapComponent组件已挂载')
  await nextTick()
  
  // 使用动态加载器加载高德地图API
  try {
    console.log('开始加载高德地图API...')
    const loadSuccess = await loadAmapAPI()
    
    if (loadSuccess && isAmapAvailable()) {
      console.log('高德地图API加载成功，开始初始化地图')
      initAmap()
    } else {
      console.warn('高德地图API加载失败或密钥未配置')
      showMapPlaceholder('API加载失败或密钥未配置')
    }
  } catch (error) {
    console.error('加载高德地图API时出错:', error)
    showMapPlaceholder('API加载出错')
  }
})

onUnmounted(() => {
  if (map.value) {
    map.value.destroy()
  }
})

// 暴露给模板的全局函数
window.searchNearby = () => {
  const center = map.value.getCenter()
  searchNearbyBusinessAreas(center)
}

window.viewDetails = (areaId) => {
  const area = props.businessAreas.find(a => a.id === areaId)
  if (area) {
    selectBusinessArea(area)
  }
}
</script>

<style scoped>
.amap-container {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 16px;
  overflow: hidden;
}

.map-controls {
  position: absolute;
  top: 15px;
  left: 15px;
  right: 15px;
  display: flex;
  gap: 15px;
  align-items: center;
  background: rgba(26, 43, 74, 0.9);
  backdrop-filter: blur(20px);
  padding: 12px 20px;
  border-radius: 12px;
  z-index: 1000;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  flex-wrap: wrap;
}

.city-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #8c9eff;
  font-size: 14px;
  white-space: nowrap;
}

.city-selector label {
  font-weight: 500;
}

.search-box {
  display: flex;
  gap: 8px;
  flex: 1;
}

.search-box input {
  flex: 1;
  min-width: 200px;
}

.search-btn {
  padding: 8px 12px;
  min-width: auto;
}

.distance-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #8c9eff;
  font-size: 14px;
}

.distance-selector label {
  white-space: nowrap;
}

.modern-select {
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: #fff;
  font-size: 14px;
}

.modern-select option {
  background: #1a2b4a;
  color: #fff;
}

.map-tools {
  display: flex;
  gap: 8px;
}

.tool-btn {
  padding: 8px;
  min-width: auto;
}

.amap {
  width: 100%;
  border-radius: 16px;
}

.map-legend {
  position: absolute;
  bottom: 15px;
  left: 15px;
  background: rgba(26, 43, 74, 0.9);
  backdrop-filter: blur(20px);
  padding: 15px;
  border-radius: 12px;
  z-index: 1000;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
  color: #8c9eff;
  font-size: 14px;
}

.legend-item:last-child {
  margin-bottom: 0;
}

.legend-marker {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-marker.hot {
  background: #ff4444;
  box-shadow: 0 0 10px rgba(255, 68, 68, 0.6);
}

.legend-marker.warm {
  background: #ff9800;
  box-shadow: 0 0 10px rgba(255, 152, 0, 0.6);
}

.legend-marker.cool {
  background: #2196f3;
  box-shadow: 0 0 10px rgba(33, 150, 243, 0.6);
}

.legend-marker.selected {
  background: #4caf50;
  box-shadow: 0 0 10px rgba(76, 175, 80, 0.6);
}

.area-info-panel {
  position: absolute;
  bottom: 15px;
  right: 15px;
  width: 280px;
  padding: 20px;
  z-index: 1000;
}

.area-info-panel h4 {
  margin: 0 0 15px 0;
  color: #8c9eff;
  font-size: 18px;
  font-weight: bold;
}

.area-stats {
  margin-bottom: 15px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.stat-item .label {
  color: #b3c6ff;
}

.stat-item .value {
  color: #fff;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .map-controls {
    flex-wrap: wrap;
    gap: 10px;
    padding: 10px 15px;
  }
  
  .city-selector {
    order: 1;
    flex: 0 0 auto;
  }
  
  .search-box {
    order: 2;
    flex: 1 1 200px;
    min-width: 200px;
  }
  
  .distance-selector {
    order: 3;
    flex: 0 0 auto;
  }
  
  .map-tools {
    order: 4;
    flex: 0 0 auto;
  }
}

@media (max-width: 768px) {
  .map-controls {
    flex-direction: column;
    gap: 12px;
    padding: 15px;
  }
  
  .city-selector,
  .search-box,
  .distance-selector,
  .map-tools {
    width: 100%;
    justify-content: center;
    order: unset;
  }
  
  .search-box {
    flex-direction: row;
  }
  
  .distance-selector,
  .map-tools {
    justify-content: space-between;
  }
  
  .area-info-panel {
    width: calc(100% - 30px);
    left: 15px;
    right: 15px;
  }
}
</style>
