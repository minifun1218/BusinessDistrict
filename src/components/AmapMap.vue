<template>
  <div class="amap-container">
    <!-- 加载状态 -->
    <div v-if="isLoading" class="map-loading">
      <div class="loading-spinner"></div>
      <div class="loading-text">高德地图加载中...</div>
    </div>

    <!-- 地图控制面板 -->
    <div class="map-controls" v-show="!isLoading">
      <!-- 城市选择器 -->
      <div class="city-selector">
        <label>当前城市：</label>
        <CitySelector v-model="selectedCity" @change="handleCityChange" @location-found="handleLocationFound" :disabled="cityChanging" />
        <div v-if="cityChanging" class="city-changing-indicator">
          <div class="city-loading-spinner"></div>
          <span>切换中...</span>
        </div>
      </div>

      <!-- 搜索框 -->
      <div class="search-box">
        <input
          v-model="searchKeyword"
          @keyup.enter="searchLocation"
          placeholder="搜索地点、商圈、POI..."
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

      <!-- 搜索配置 -->
      <div class="search-config">
        <div class="config-item">
          <label>搜索半径：</label>
          <select v-model="searchRadius" @change="onRadiusChange" class="modern-select">
            <option value="500">500米</option>
            <option value="1000">1公里</option>
            <option value="3000">3公里</option>
            <option value="5000">5公里</option>
            <option value="10000">10公里</option>
          </select>
        </div>
        
        <div class="config-item">
          <label>每页结果：</label>
          <select v-model="pageSize" @change="onPageSizeChange" class="modern-select">
            <option value="5">5条</option>
            <option value="10">10条</option>
            <option value="20">20条</option>
            <option value="50">50条</option>
          </select>
        </div>
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
        
        <!-- 缓存状态指示器 -->
        <div class="cache-status-indicator" v-if="searchHistory.length > 0" :title="`本地缓存: ${searchHistory.length} 个位置`">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M16 4H18C19.1046 4 20 4.89543 20 6V18C20 19.1046 19.1046 20 18 20H6C4.89543 20 4 19.1046 4 18V6C4 4.89543 4.89543 4 6 4H8" stroke="currentColor" stroke-width="2"/>
            <rect x="8" y="2" width="8" height="4" rx="1" stroke="currentColor" stroke-width="2"/>
            <path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2"/>
          </svg>
          <span class="cache-count">{{ searchHistory.length }}</span>
        </div>
      </div>
    </div>

    <!-- 高德地图容器 -->
    <div ref="amapContainer" class="amap" :style="{ height: mapHeight }"></div>

    <!-- 坐标显示 -->
    <div v-if="!isLoading && currentCoords" class="coords-display">
      <span>经度: {{ currentCoords.lng.toFixed(6) }}</span>
      <span>纬度: {{ currentCoords.lat.toFixed(6) }}</span>
    </div>

    <!-- 搜索结果面板 -->
    <div v-if="searchResults.length > 0" class="search-results-panel" ref="searchPanel">
      <div class="panel-header">
        <h4>搜索结果 ({{ totalCount }}个)</h4>
        <div class="pagination" v-if="totalPages > 1">
          <button 
            @click="prevPage" 
            :disabled="currentPage === 1"
            class="page-btn modern-btn outline"
          >
            上一页
          </button>
          <span class="page-info">{{ currentPage }}/{{ totalPages }}</span>
          <button 
            @click="nextPage" 
            :disabled="currentPage === totalPages"
            class="page-btn modern-btn outline"
          >
            下一页
          </button>
        </div>
      </div>
      
      <div class="results-list">
        <div 
          v-for="(result, index) in searchResults" 
          :key="result.id || index"
          @click="selectSearchResult(result)"
          class="result-item"
          :class="{ active: selectedResult?.id === result.id }"
        >
          <div class="result-name">{{ result.name }}</div>
          <div class="result-address">{{ result.address || result.district }}</div>
          <div class="result-info">
            <span v-if="result.type" class="result-type">{{ result.type }}</span>
            <span v-if="result.distance" class="result-distance">{{ Math.round(result.distance) }}米</span>
            <span v-if="result.tel" class="result-tel">{{ result.tel }}</span>
          </div>
          <div v-if="result.business_area" class="result-business">
            商圈: {{ result.business_area }}
          </div>
        </div>
      </div>
    </div>

    <!-- 附近商圈列表 -->
    <div v-if="nearbyBusinessAreas.length > 0" class="nearby-areas-panel">
      <div class="panel-header">
        <h4>附近商圈 ({{ nearbyBusinessAreas.length }}个)</h4>
        <div class="cache-indicator" v-if="searchResultCached">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="#10b981" stroke-width="2"/>
            <path d="m9 12 2 2 4-4" stroke="#10b981" stroke-width="2"/>
          </svg>
          <span>缓存数据</span>
        </div>
      </div>
      <div class="areas-list">
        <div 
          v-for="area in nearbyBusinessAreas" 
          :key="area.id"
          @click="selectBusinessAreaFromList(area)"
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

    <!-- 选中POI/商圈详情 -->
    <div v-if="selectedResult || selectedArea" class="details-panel modern-card">
      <div v-if="selectedResult">
        <h4>{{ selectedResult.name }}</h4>
        <div class="detail-content">
          <div class="detail-item" v-if="selectedResult.address">
            <span class="label">地址：</span>
            <span class="value">{{ selectedResult.address }}</span>
          </div>
          <div class="detail-item" v-if="selectedResult.type">
            <span class="label">类型：</span>
            <span class="value">{{ selectedResult.type }}</span>
          </div>
          <div class="detail-item" v-if="selectedResult.tel">
            <span class="label">电话：</span>
            <span class="value">{{ selectedResult.tel }}</span>
          </div>
          <div class="detail-item" v-if="selectedResult.business_area">
            <span class="label">商圈：</span>
            <span class="value">{{ selectedResult.business_area }}</span>
          </div>
          <div class="detail-item" v-if="selectedResult.distance">
            <span class="label">距离：</span>
            <span class="value">{{ Math.round(selectedResult.distance) }}米</span>
          </div>
        </div>
      </div>
      
      <div v-else-if="selectedArea">
        <h4>{{ selectedArea.name }}</h4>
        <div class="detail-content">
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
      </div>
      
      <button @click="viewDetails" class="modern-btn primary">查看详情</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ENV_CONFIG } from '../config/env.js'
import { loadAmapAPI, isAmapAvailable } from '../utils/mapLoader.js'
// 不再使用外部API服务，改用SDK内置搜索
import { businessApi } from '../api/business.js'
import CitySelector from './CitySelector.vue'

// Props
const props = defineProps({
  modelValue: { type: Object, default: () => ({ lng: 116.4074, lat: 39.9042 }) },
  height: { type: String, default: '500px' },
  businessAreas: { type: Array, default: () => [] },
  currentCity: { type: Object, default: () => ({ id: 'beijing', name: '北京' }) }
})

// Emits
const emit = defineEmits(['update:modelValue', 'area-selected', 'location-changed', 'city-changed', 'poi-selected', 'area-data-updated', 'crawl'])

// 响应式数据
const amapContainer = ref(null)
const searchPanel = ref(null)
const map = ref(null)
const markers = ref([])
const placeSearch = ref(null)
const geolocation = ref(null)

const searchKeyword = ref('')
const searchRadius = ref(1000)
const pageSize = ref(10)
const currentPage = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)

const selectedCity = ref(props.currentCity)
const mapHeight = ref(props.height)
const isLoading = ref(true)
const hasInitialized = ref(false)

const currentCoords = ref(props.modelValue)
const searchResults = ref([])
const nearbyBusinessAreas = ref([])
const selectedResult = ref(null)
const selectedArea = ref(null)
const searchResultCached = ref(false)
const cityChanging = ref(false)

// 本地缓存搜索历史
const searchHistory = ref([])
const cacheRange = ref(500) // 缓存有效范围（米）

let resizeHandler = null

// 城市代码映射
const cityCodeMap = {
  'beijing': '010',
  'shanghai': '021',
  'guangzhou': '020',
  'shenzhen': '0755',
  'hangzhou': '0571',
  'nanjing': '025',
  'wuhan': '027',
  'chengdu': '028'
}

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

// 计算两点间距离（米）
const calculateDistance = (lng1, lat1, lng2, lat2) => {
  const R = 6371000 // 地球半径（米）
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLng = (lng2 - lng1) * Math.PI / 180
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLng / 2) * Math.sin(dLng / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}

// 检查本地缓存
const checkLocalCache = (longitude, latitude, radius) => {
  console.log('检查本地缓存，位置:', longitude, latitude, '半径:', radius)
  
  for (const historyItem of searchHistory.value) {
    const distance = calculateDistance(
      longitude, latitude,
      historyItem.longitude, historyItem.latitude
    )
    
    console.log('与历史位置距离:', distance, '米，缓存范围:', cacheRange.value, '米')
    
    // 如果在缓存范围内，且搜索半径相近
    if (distance <= cacheRange.value && Math.abs(historyItem.radius - radius) <= 100) {
      console.log('使用本地缓存数据，历史位置:', historyItem.longitude, historyItem.latitude)
      return historyItem
    }
  }
  
  console.log('未找到合适的本地缓存')
  return null
}

// 保存搜索结果到本地缓存
const saveToLocalCache = (longitude, latitude, radius, areas, cached = false) => {
  const cacheItem = {
    longitude,
    latitude,
    radius,
    areas,
    cached,
    timestamp: Date.now()
  }
  
  // 添加到历史记录，最多保存10个位置
  searchHistory.value.unshift(cacheItem)
  if (searchHistory.value.length > 10) {
    searchHistory.value = searchHistory.value.slice(0, 10)
  }
  
  console.log('💾 保存到本地缓存，当前缓存数量:', searchHistory.value.length)
}

// 清除本地缓存
const clearLocalCache = () => {
  searchHistory.value = []
  console.log('🗑️ 已清除本地缓存')
}

// 快速初始化
const quickInit = async () => {
  if (hasInitialized.value) return
  
  try {
    // 检查API是否已加载
    if (window.AMap && isAmapAvailable()) {
      initAmapMap()
      return
    }
    
    // 加载高德地图API
    const loadSuccess = await loadAmapAPI()
    if (loadSuccess && isAmapAvailable()) {
      requestAnimationFrame(() => initAmapMap())
    } else {
      showMapPlaceholder('API加载失败')
    }
  } catch (e) {
    console.error('高德地图API加载错误:', e)
    showMapPlaceholder('API加载出错')
  }
}

// 地图初始化
const initAmapMap = () => {
  if (!amapContainer.value) return
  if (!ENV_CONFIG.AMAP_CONFIG.key || !ENV_CONFIG.AMAP_CONFIG.securityJsCode) {
    showMapPlaceholder('API密钥或安全密钥未配置')
    return
  }
  if (!window.AMap) {
    showMapPlaceholder('API未就绪')
    return
  }

  try {
    const container = amapContainer.value
    container.innerHTML = ''
    
    // 创建地图实例
    map.value = new window.AMap.Map(container, {
      center: [props.modelValue.lng, props.modelValue.lat],
      zoom: 11,
      resizeEnable: true,
      rotateEnable: true,
      pitchEnable: true,
      zoomEnable: true,
      dragEnable: true
    })

    // 初始化地点搜索服务（插件已通过AMapLoader预加载）
    try {
      // 地点搜索
      placeSearch.value = new window.AMap.PlaceSearch({
        pageSize: pageSize.value,
        pageIndex: currentPage.value,
        city: getCityCode(selectedCity.value.id),
        citylimit: true, // 限制在指定城市内搜索
        map: map.value,
        autoFitView: false, // 手动控制视野
        extensions: 'all' // 获取详细信息
      })
      
      console.log('PlaceSearch服务初始化完成，当前城市:', selectedCity.value.name, '城市代码:', getCityCode(selectedCity.value.id))

      // 定位服务
      geolocation.value = new window.AMap.Geolocation({
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
        convert: true,
        showButton: false,
        buttonPosition: 'LB',
        showMarker: true,
        showCircle: true,
        panToLocation: true,
        zoomToAccuracy: true
      })

      console.log('高德地图服务初始化成功')
    } catch (error) {
      console.error('高德地图服务初始化失败:', error)
      showMapPlaceholder('服务初始化失败')
      return
    }

    // 地图事件监听
    map.value.on('click', handleMapClick)
    map.value.on('moveend', handleMapMoveEnd)
    map.value.on('zoomend', handleZoomEnd)

    // 加载初始商圈数据
    if (props.businessAreas.length > 0) {
      loadBusinessAreaMarkers()
    }

    // 窗口大小调整监听
    const onResize = throttle(() => map.value?.getSize(), 300)
    resizeHandler = onResize
    window.addEventListener('resize', onResize, { passive: true })

    hasInitialized.value = true
    isLoading.value = false

    console.log('高德地图初始化成功')

  } catch (error) {
    console.error('地图初始化失败:', error)
    showMapPlaceholder('地图初始化失败')
  }
}

// 获取城市代码
const getCityCode = (cityId) => {
  return cityCodeMap[cityId] || '010'
}

// 显示占位符
const showMapPlaceholder = (reason = '地图加载失败') => {
  isLoading.value = false
  if (!amapContainer.value) return
  amapContainer.value.innerHTML = `
    <div style="
      width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
      background: #1f2937; border: 1px dashed #4b5563; color: #d1d5db; font-size: 14px;
      text-align: center; flex-direction: column; padding: 20px; box-sizing: border-box;
    ">
      <div style="margin-bottom: 10px; font-size: 24px;">🗺️</div>
      <div style="font-weight: bold; margin-bottom: 8px; color: #f3f4f6;">${reason}</div>
      <div style="font-size: 12px; color: #9ca3af;">请检查网络连接或联系管理员</div>
    </div>
  `
}

// 地图点击事件
const handleMapClick = async (e) => {
  const lnglat = e.lnglat
  const coords = { lng: lnglat.getLng(), lat: lnglat.getLat() }
  
  currentCoords.value = coords
  emit('update:modelValue', coords)
  emit('location-changed', coords)
  
  // 添加点击标记
  addClickMarker(lnglat)
  
  // 搜索附近商圈（带缓存功能）
  await searchNearbyBusinessAreasWithCache(lnglat)
}

// 地图移动结束事件
const handleMapMoveEnd = throttle(() => {
  if (!map.value) return
  const center = map.value.getCenter()
  const coords = { lng: center.getLng(), lat: center.getLat() }
  currentCoords.value = coords
  emit('update:modelValue', coords)
}, 200)

// 地图缩放结束事件
const handleZoomEnd = throttle(() => {
  // 根据缩放级别调整标记显示
  loadBusinessAreaMarkers()
}, 300)

// 添加点击标记
const addClickMarker = (lnglat) => {
  if (!map.value) return
  
  // 清除之前的点击标记
  markers.value.forEach(marker => {
    if (marker.isClickMarker) {
      map.value.remove(marker)
    }
  })
  markers.value = markers.value.filter(marker => !marker.isClickMarker)
  
  // 创建新标记
  const marker = new window.AMap.Marker({
    position: lnglat,
    title: '点击位置',
    icon: new window.AMap.Icon({
      size: new window.AMap.Size(25, 34),
      image: '//webapi.amap.com/theme/v1.3/markers/n/mark_b.png',
      imageOffset: new window.AMap.Pixel(-9, -3),
      imageSize: new window.AMap.Size(135, 40)
    })
  })
  
  marker.isClickMarker = true
  map.value.add(marker)
  markers.value.push(marker)
  
  // 添加信息窗口
  const infoWindow = new window.AMap.InfoWindow({
    content: `
      <div style="padding: 10px; min-width: 200px;">
        <h4 style="margin: 0 0 10px 0;color: black;">选中位置</h4>
        <p style="margin: 5px 0;color: black;">经度: ${lnglat.getLng().toFixed(6)}</p>
        <p style="margin: 5px 0;color: black;">纬度: ${lnglat.getLat().toFixed(6)}</p>
        <button onclick="searchNearbyPOI()" style="margin-top: 10px; padding: 5px 10px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer;">搜索附近商圈</button>
      </div>
    `,
    offset: new window.AMap.Pixel(0, -34)
  })
  
  marker.on('click', () => {
    infoWindow.open(map.value, lnglat)
  })
}

// 搜索位置 - 使用高德地图SDK内置搜索
const searchLocation = async () => {
  if (!searchKeyword.value.trim()) return

  try {
    console.log('开始搜索:', searchKeyword.value)
    
    // 直接使用地图内置搜索
    if (placeSearch.value) {
      placeSearch.value.setPageIndex(currentPage.value)
      placeSearch.value.setPageSize(pageSize.value)
      placeSearch.value.setCity(getCityCode(selectedCity.value.id))
      
      placeSearch.value.search(searchKeyword.value, (status, result) => {
        if (status === 'complete') {
          handleSearchResult(result)
        } else {
          console.error('搜索失败:', result)
          searchResults.value = []
          totalCount.value = 0
          totalPages.value = 0
        }
      })
    } else {
      console.error('PlaceSearch服务未初始化')
      searchResults.value = []
    }
    
  } catch (error) {
    console.error('搜索失败:', error)
    searchResults.value = []
    totalCount.value = 0
    totalPages.value = 0
  }
}

// 处理API搜索结果函数已移除，改用SDK内置搜索

// 处理内置搜索结果
const handleSearchResult = (result) => {
  if (result.poiList && result.poiList.pois) {
    const pois = result.poiList.pois
    searchResults.value = pois.map(poi => ({
      id: poi.id,
      name: poi.name,
      address: poi.address || poi.district,
      type: poi.type,
      tel: poi.tel,
      location: poi.location,
      distance: poi.distance,
      business_area: poi.business_area
    }))
    
    totalCount.value = result.poiList.count
    totalPages.value = Math.ceil(totalCount.value / pageSize.value)
    
    // 清除之前的搜索标记
    clearSearchMarkers()
    
    // 添加搜索结果标记
    addSearchMarkers(pois)
    
    // 自动调整视野
    if (pois.length > 0) {
      const bounds = new window.AMap.Bounds()
      pois.forEach(poi => {
        bounds.extend(poi.location)
      })
      map.value.setBounds(bounds)
    }
    
    console.log(`内置搜索到 ${pois.length} 个结果`)
  } else {
    searchResults.value = []
    totalCount.value = 0
    totalPages.value = 0
  }
}

// API搜索标记函数已移除，统一使用内置搜索标记

// 添加内置搜索结果标记
const addSearchMarkers = (pois) => {
  if (!map.value) return
  
  pois.forEach((poi, index) => {
    const marker = new window.AMap.Marker({
      position: poi.location,
      title: poi.name,
      icon: new window.AMap.Icon({
        size: new window.AMap.Size(25, 34),
        image: '//webapi.amap.com/theme/v1.3/markers/n/mark_r.png',
        imageOffset: new window.AMap.Pixel(-9, -3),
        imageSize: new window.AMap.Size(135, 40)
      }),
      label: {
        content: (index + 1).toString(),
        offset: new window.AMap.Pixel(-9, -20),
        direction: 'center'
      }
    })
    
    marker.isSearchMarker = true
    marker.poiData = poi
    map.value.add(marker)
    markers.value.push(marker)
    
    // 点击标记选中POI
    marker.on('click', () => {
      selectSearchResult({
        id: poi.id,
        name: poi.name,
        address: poi.address || poi.district,
        type: poi.type,
        tel: poi.tel,
        location: poi.location,
        distance: poi.distance,
        business_area: poi.business_area
      })
    })
  })
}

// 清除搜索标记
const clearSearchMarkers = () => {
  markers.value.forEach(marker => {
    if (marker.isSearchMarker) {
      map.value.remove(marker)
    }
  })
  markers.value = markers.value.filter(marker => !marker.isSearchMarker)
}

// 选择搜索结果
const selectSearchResult = (result) => {
  selectedResult.value = result
  selectedArea.value = null
  
  emit('poi-selected', result)
  
  if (map.value && result.location) {
    map.value.setCenter(result.location)
    map.value.setZoom(16)
  }
}

// 分页操作
const prevPage = () => {
  if (currentPage.value > 1 && placeSearch.value) {
    currentPage.value--
    placeSearch.value.setPageIndex(currentPage.value)
    placeSearch.value.setCity(getCityCode(selectedCity.value.id))
    placeSearch.value.search(searchKeyword.value, (status, result) => {
      if (status === 'complete') {
        handleSearchResult(result)
      } else {
        console.error('分页搜索失败:', result)
      }
    })
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value && placeSearch.value) {
    currentPage.value++
    placeSearch.value.setPageIndex(currentPage.value)
    placeSearch.value.setCity(getCityCode(selectedCity.value.id))
    placeSearch.value.search(searchKeyword.value, (status, result) => {
      if (status === 'complete') {
        handleSearchResult(result)
      } else {
        console.error('分页搜索失败:', result)
      }
    })
  }
}

// 加载商圈标记（用于props传入的商圈数据）
const loadBusinessAreaMarkers = () => {
  if (!map.value || !props.businessAreas.length) return

  // 清除旧的商圈标记
  clearBusinessMarkers()

  // 根据缩放级别限制显示数量
  const currentZoom = map.value.getZoom()
  const maxMarkers = currentZoom < 12 ? 20 : 50
  
  let filteredAreas = props.businessAreas
  if (currentZoom < 12) {
    filteredAreas = props.businessAreas
      .filter(a => a.hotValue > 60)
      .slice(0, maxMarkers)
  } else {
    filteredAreas = props.businessAreas.slice(0, maxMarkers)
  }

  // 创建标记
  addBusinessAreaMarkers(filteredAreas)
}

// 添加商圈标记（通用方法）
const addBusinessAreaMarkers = (areas) => {
  if (!map.value || !areas.length) return

  // 清除之前的商圈标记
  clearBusinessMarkers()

  areas.forEach(area => {
    let iconColor = 'b' // 蓝色 (cool)
    if (area.hotValue > 80) iconColor = 'r' // 红色 (hot)
    else if (area.hotValue > 50) iconColor = 'o' // 橙色 (warm)
    
    const marker = new window.AMap.Marker({
      position: [area.longitude, area.latitude],
      title: area.name,
      icon: new window.AMap.Icon({
        size: new window.AMap.Size(25, 34),
        image: `//webapi.amap.com/theme/v1.3/markers/n/mark_${iconColor}.png`,
        imageOffset: new window.AMap.Pixel(-9, -3),
        imageSize: new window.AMap.Size(135, 40)
      })
    })
    
    marker.isBusinessMarker = true
    marker.businessData = area
    map.value.add(marker)
    markers.value.push(marker)
    
    // 添加信息窗口
    const infoWindow = new window.AMap.InfoWindow({
      content: `
        <div style="padding: 10px; min-width: 200px;">
          <h4 style="margin: 0 0 10px 0; color: black;">${area.name}</h4>
          <p style="margin: 5px 0; color: black;">类别: ${area.category}</p>
          <p style="margin: 5px 0; color: black;">热度: ${area.hotValue}</p>
          ${area.distance ? `<p style="margin: 5px 0; color: black;">距离: ${area.distance}米</p>` : ''}
          <p style="margin: 5px 0; color: black;">地址: ${area.address || '暂无地址信息'}</p>
        </div>
      `,
      offset: new window.AMap.Pixel(0, -34)
    })
    
    // 点击标记显示信息窗口并选中商圈
    marker.on('click', () => {
      infoWindow.open(map.value, marker.getPosition())
      selectBusinessArea(area)
    })
  })
}

// 清除商圈标记
const clearBusinessMarkers = () => {
  markers.value.forEach(marker => {
    if (marker.isBusinessMarker) {
      map.value.remove(marker)
    }
  })
  markers.value = markers.value.filter(marker => !marker.isBusinessMarker)
}

// 获取当前位置
const getCurrentLocation = () => {
  if (!geolocation.value) return
  
  geolocation.value.getCurrentPosition((status, result) => {
    if (status === 'complete') {
      const coords = { 
        lng: result.position.getLng(), 
        lat: result.position.getLat() 
      }
      currentCoords.value = coords
      emit('update:modelValue', coords)
      
      map.value.setCenter(result.position)
      map.value.setZoom(15)
      
      // 搜索附近商圈
      searchNearbyBusinessAreas(result.position)
    } else {
      console.error('定位失败:', result)
      alert('定位失败，请检查浏览器定位权限')
    }
  })
}

// 搜索附近商圈（带缓存功能）
const searchNearbyBusinessAreasWithCache = async (lnglat) => {
  try {
    const longitude = lnglat.getLng()
    const latitude = lnglat.getLat()
    const radius = parseInt(searchRadius.value)
    
    console.log('开始搜索附近商圈（带缓存）...', longitude, latitude, '半径:', radius)
    
    // 首先检查本地缓存
    const localCache = checkLocalCache(longitude, latitude, radius)
    if (localCache) {
      console.log('🎯 使用本地缓存数据，商圈数量:', localCache.areas.length)
      nearbyBusinessAreas.value = localCache.areas
      addBusinessAreaMarkers(localCache.areas)
      
      searchResultCached.value = true
      emit('location-changed', {
        lng: longitude,
        lat: latitude,
        nearbyAreas: localCache.areas,
        cached: true
      })
      return
    }
    
    // 检查数据库缓存
    try {
      const cacheResponse = await businessApi.checkNearbyCache(longitude, latitude, radius)
      if (cacheResponse.data && cacheResponse.data.length > 0) {
        console.log('📊 从数据库缓存获取商圈:', cacheResponse.data.length, '个')
        nearbyBusinessAreas.value = cacheResponse.data
        addBusinessAreaMarkers(cacheResponse.data)
        
        // 保存到本地缓存
        saveToLocalCache(longitude, latitude, radius, cacheResponse.data, true)
        
        searchResultCached.value = true
        emit('location-changed', {
          lng: longitude,
          lat: latitude,
          nearbyAreas: cacheResponse.data,
          cached: true
        })
        return
      }
    } catch (cacheError) {
      console.warn('检查数据库缓存失败，继续SDK搜索:', cacheError)
    }
    
    // 如果缓存中没有数据，使用SDK搜索
    const businessAreas = await searchNearbyBusinessAreasSdk(lnglat)
    console.log('🔍 SDK搜索到商圈:', businessAreas.length, '个')
    
    if (businessAreas.length > 0) {
      // 保存搜索结果到数据库
      try {
        const saveResponse = await businessApi.searchAndSaveBusinessAreas({
          longitude,
          latitude,
          radius,
          cityId: selectedCity.value.id,
          searchAreas: businessAreas
        })
        
        console.log('商圈数据保存结果:', saveResponse.message)
        
        // 使用保存后的数据（可能包含数据库ID等信息）
        const finalAreas = saveResponse.data && saveResponse.data.areas ? saveResponse.data.areas : businessAreas
        nearbyBusinessAreas.value = finalAreas
        addBusinessAreaMarkers(finalAreas)
        
        // 保存到本地缓存
        saveToLocalCache(longitude, latitude, radius, finalAreas, false)
        
      } catch (saveError) {
        console.error('保存商圈数据失败:', saveError)
        // 即使保存失败，仍然显示搜索结果
        nearbyBusinessAreas.value = businessAreas
        addBusinessAreaMarkers(businessAreas)
        
        // 保存到本地缓存
        saveToLocalCache(longitude, latitude, radius, businessAreas, false)
      }
    } else {
      nearbyBusinessAreas.value = []
      // 即使没有数据也保存到缓存，避免重复搜索
      saveToLocalCache(longitude, latitude, radius, [], false)
    }
    
    searchResultCached.value = false
    emit('location-changed', {
      lng: longitude,
      lat: latitude,
      nearbyAreas: nearbyBusinessAreas.value,
      cached: false
    })
    
  } catch (error) {
    console.error('搜索附近商圈失败:', error)
    // 如果所有搜索都失败，回退到模拟数据
    const mockNearbyAreas = generateMockNearbyAreas(lnglat)
    nearbyBusinessAreas.value = mockNearbyAreas
    
    searchResultCached.value = false
    emit('location-changed', {
      lng: lnglat.getLng(),
      lat: lnglat.getLat(),
      nearbyAreas: mockNearbyAreas,
      cached: false
    })
  }
}

// 搜索附近商圈 - 使用高德地图SDK内置搜索（保持原有功能）
const searchNearbyBusinessAreas = async (lnglat) => {
  // 直接调用带缓存的版本
  await searchNearbyBusinessAreasWithCache(lnglat)
}

// 搜索附近POI - 使用高德地图SDK内置搜索
const searchNearbyPois = async (lnglat) => {
  try {
    const location = `${lnglat.getLng()},${lnglat.getLat()}`
    
    console.log('开始搜索附近POI...', location)
    
    if (!placeSearch.value) {
      console.warn('PlaceSearch服务未初始化')
      return
    }
    
    // 使用SDK内置搜索附近POI
    const pois = await searchNearbyPoisSdk(lnglat)
    
    console.log('搜索到POI:', pois.length, '个')
    
    // 将POI转换为搜索结果格式
    const poiResults = pois.map(poi => ({
      id: poi.id,
      name: poi.name,
      address: poi.address || poi.district,
      type: poi.type,
      tel: poi.tel,
      location: poi.location,
      distance: poi.distance,
      business_area: poi.business_area
    }))
    
    // 更新搜索结果
    searchResults.value = poiResults
    totalCount.value = pois.length
    totalPages.value = Math.ceil(totalCount.value / pageSize.value)
    
    // 清除之前的搜索标记
    clearSearchMarkers()
    
    // 添加POI标记
    addSearchMarkers(pois)
    
    console.log(`搜索附近POI完成，共找到 ${pois.length} 个`)
    
  } catch (error) {
    console.error('搜索附近POI失败:', error)
  }
}

// 使用SDK搜索附近商圈
const searchNearbyBusinessAreasSdk = (centerPoint) => {
  return new Promise((resolve) => {
    if (!placeSearch.value) {
      resolve([])
      return
    }
    
    // 商圈相关关键词
    const businessKeywords = ['商圈', '购物中心', '商业广场', '步行街']
    const allResults = []
    let completedSearches = 0
    
    // 创建临时搜索实例用于商圈搜索
    const businessSearch = new window.AMap.PlaceSearch({
      pageSize: 10,
      pageIndex: 1,
      city: getCityCode(selectedCity.value.id),
      citylimit: true,
      map: null, // 不自动显示在地图上
      autoFitView: false
    })
    
    const searchKeyword = (keyword) => {
      businessSearch.searchNearBy(keyword, centerPoint, parseInt(searchRadius.value), (status, result) => {
        completedSearches++
        
        if (status === 'complete' && result.poiList && result.poiList.pois) {
          const pois = result.poiList.pois.map(poi => ({
            id: poi.id || `area_${Math.random().toString(36).substr(2, 9)}`,
            name: poi.name,
            longitude: poi.location.getLng(),
            latitude: poi.location.getLat(),
            address: poi.address || poi.district,
            category: determineAreaCategory(poi),
            hotValue: calculateHotValue(poi),
            distance: poi.distance ? Math.round(poi.distance) : 0,
            type: poi.type || '',
            tel: poi.tel || '',
            storeCount: Math.floor(Math.random() * 200) + 50,
            avgConsumption: Math.floor(Math.random() * 300) + 100
          }))
          
          allResults.push(...pois)
        }
        
        // 所有搜索完成后返回结果
        if (completedSearches === businessKeywords.length) {
          // 去重和排序
          const uniqueResults = deduplicateAreas(allResults)
          const sortedResults = uniqueResults.sort((a, b) => a.distance - b.distance)
          resolve(sortedResults.slice(0, 20)) // 最多返回20个结果
        }
      })
    }
    
    // 搜索所有关键词
    businessKeywords.forEach(searchKeyword)
    
    // 设置超时
    setTimeout(() => {
      if (completedSearches < businessKeywords.length) {
        console.warn('商圈搜索超时，返回已有结果')
        const uniqueResults = deduplicateAreas(allResults)
        const sortedResults = uniqueResults.sort((a, b) => a.distance - b.distance)
        resolve(sortedResults.slice(0, 20))
      }
    }, 8000)
  })
}

// 使用SDK搜索附近POI
const searchNearbyPoisSdk = (centerPoint) => {
  return new Promise((resolve) => {
    if (!placeSearch.value) {
      resolve([])
      return
    }
    
    // 创建临时搜索实例用于POI搜索
    const poiSearch = new window.AMap.PlaceSearch({
      pageSize: 20,
      pageIndex: 1,
      city: getCityCode(selectedCity.value.id),
      citylimit: true,
      map: null, // 不自动显示在地图上
      autoFitView: false
    })
    
    // 搜索附近所有POI
    poiSearch.searchNearBy('', centerPoint, parseInt(searchRadius.value), (status, result) => {
      if (status === 'complete' && result.poiList && result.poiList.pois) {
        const pois = result.poiList.pois.filter(poi => poi.name && poi.location)
        resolve(pois)
      } else {
        console.warn('POI搜索失败:', result)
        resolve([])
      }
    })
    
    // 设置超时
    setTimeout(() => {
      console.warn('POI搜索超时')
      resolve([])
    }, 5000)
  })
}

// 确定商圈类别
const determineAreaCategory = (poi) => {
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

// 计算热度值
const calculateHotValue = (poi) => {
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

// 去重商圈数据
const deduplicateAreas = (areas) => {
  const seen = new Set()
  const unique = []

  for (const area of areas) {
    const key = `${area.name}_${area.longitude}_${area.latitude}`
    if (!seen.has(key)) {
      seen.add(key)
      unique.push(area)
    }
  }

  return unique
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
    const distance = Math.floor(Math.random() * parseInt(searchRadius.value)) + 100
    
    return {
      ...area,
      longitude: centerPoint.getLng() + (Math.random() - 0.5) * 0.02,
      latitude: centerPoint.getLat() + (Math.random() - 0.5) * 0.02,
      distance,
      storeCount: Math.floor(Math.random() * 200) + 50,
      avgConsumption: Math.floor(Math.random() * 300) + 100
    }
  }).filter(area => area.distance <= parseInt(searchRadius.value))
    .sort((a, b) => a.distance - b.distance)
}

// 选择商圈（从列表点击，不触发后端请求）
const selectBusinessAreaFromList = (area) => {
  selectedArea.value = area
  selectedResult.value = null
  // 注意：不发送 area-selected 事件，避免触发后端请求
  
  if (map.value) {
    map.value.setCenter([area.longitude, area.latitude])
  }
  
  console.log('从列表选中商圈:', area.name, '- 不触发后端请求')
}

// 选择商圈（从地图标记点击，触发后端请求）
const selectBusinessArea = (area) => {
  selectedArea.value = area
  selectedResult.value = null
  emit('area-selected', area)
  
  if (map.value) {
    map.value.setCenter([area.longitude, area.latitude])
  }
  
  console.log('从地图标记选中商圈:', area.name, '- 触发后端请求')
}

// 清除标记
const clearMarkers = () => {
  if (!map.value) return
  
  markers.value.forEach(marker => map.value.remove(marker))
  markers.value = []
  selectedResult.value = null
  selectedArea.value = null
  nearbyBusinessAreas.value = []
  searchResults.value = []
  searchResultCached.value = false
}

// 刷新地图
const refreshMap = throttle(() => {
  if (map.value) {
    map.value.getSize()
    const center = map.value.getCenter()
    map.value.setCenter(center)
  }
}, 300)

// 城市变化处理
const handleCityChange = async (city) => {
  console.log('城市变更为:', city)
  cityChanging.value = true
  
  try {
    selectedCity.value = city
    emit('city-changed', city)
    
  // 清除之前的搜索结果，因为城市已变更
  searchResults.value = []
  nearbyBusinessAreas.value = []
  clearMarkers()
  clearLocalCache() // 清除本地缓存
    
    // 平滑切换到新城市并自动加载商圈数据
    await updateMapCenterForCity(city)
  } catch (error) {
    console.error('城市切换失败:', error)
  } finally {
    cityChanging.value = false
  }
}

// 处理定位找到事件
const handleLocationFound = async (locationData) => {
  console.log('接收到定位数据:', locationData)
  const { city, coordinates } = locationData
  
  if (!map.value || !coordinates) {
    console.warn('地图未初始化或缺少坐标信息')
    return
  }
  
  try {
    cityChanging.value = true
    
    // 清除之前的搜索结果
    searchResults.value = []
    nearbyBusinessAreas.value = []
    clearMarkers()
    
    // 直接定位到精确坐标
    const lnglat = new AMap.LngLat(coordinates.longitude, coordinates.latitude)
    console.log('定位到精确坐标:', coordinates)
    
    // 平滑移动到定位点
    map.value.panTo(lnglat, 1000) // 1秒动画
    
    // 设置合适的缩放级别
    setTimeout(() => {
      map.value.setZoom(15) // 设置较高的缩放级别以显示详细信息
    }, 500)
    
    // 在定位点添加标记
    const locationMarker = new AMap.Marker({
      position: lnglat,
      title: city ? `当前位置: ${city.name}` : '当前位置',
      icon: new AMap.Icon({
        image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_r.png',
        size: new AMap.Size(25, 34),
        imageSize: new AMap.Size(25, 34)
      })
    })
    
    map.value.add(locationMarker)
    markers.value.push(locationMarker)
    
    // 自动搜索当前位置附近的商圈
    setTimeout(async () => {
      console.log('开始搜索定位点附近的商圈...')
      await searchNearbyBusinessAreasWithCache(lnglat)
    }, 1000)
    
    // 发出位置变化事件
    emit('location-changed', { 
      lng: coordinates.longitude, 
      lat: coordinates.latitude, 
      city: city,
      source: 'user-location' 
    })
    
    console.log('定位完成，地图已移动到用户当前位置')
  } catch (error) {
    console.error('处理定位数据失败:', error)
  } finally {
    cityChanging.value = false
  }
}

// 根据城市更新地图中心点
const updateMapCenterForCity = async (city) => {
  if (!map.value) return
  
  console.log('正在切换到城市:', city.name)
  
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
  
  // 使用平滑动画移动到新城市
  map.value.panTo(coords, 1000) // 1秒动画
  
  // 延迟设置缩放级别，确保平移动画完成
  setTimeout(() => {
    if (map.value) {
      map.value.setZoom(11)
    }
  }, 500)
  
  currentCoords.value = { lng: coords[0], lat: coords[1] }
  emit('update:modelValue', currentCoords.value)
  
  // 更新搜索城市
  if (placeSearch.value) {
    placeSearch.value.setCity(getCityCode(city.id))
  }
  
  // 清除之前的搜索结果
  clearMarkers()
  
  // 自动搜索新城市的商圈数据
  setTimeout(async () => {
    try {
      console.log('自动搜索', city.name, '的商圈数据...')
      const lnglat = new window.AMap.LngLat(coords[0], coords[1])
      await searchNearbyBusinessAreasWithCache(lnglat)
      console.log('已加载', city.name, '的商圈数据')
    } catch (error) {
      console.warn('自动加载商圈数据失败:', error)
    }
  }, 1200) // 等待地图动画完成后再搜索
}

// 配置变化处理
const onRadiusChange = () => {
  console.log('搜索半径变更为:', searchRadius.value)
  if (currentCoords.value) {
    const lnglat = new window.AMap.LngLat(currentCoords.value.lng, currentCoords.value.lat)
    searchNearbyBusinessAreas(lnglat)
  }
}

const onPageSizeChange = () => {
  console.log('每页结果数变更为:', pageSize.value)
  if (placeSearch.value) {
    placeSearch.value.setPageSize(pageSize.value)
    // 如果有搜索关键词，重新搜索以应用新的页面大小
    if (searchKeyword.value.trim()) {
      currentPage.value = 1 // 重置到第一页
      searchLocation()
    }
  }
}
const viewDetails = async () => {
  // 只触发查看详情事件，不再执行爬取逻辑
  console.log(selectedArea.value, '123123123')
  if (selectedResult.value) {
    emit('poi-selected', selectedResult.value)
  } else if (selectedArea.value) {
    emit('area-selected', selectedArea.value)
  }
}

// 获取热度等级样式类
const getHotClass = (hotValue) => {
  if (hotValue > 80) return 'hot'
  if (hotValue > 50) return 'warm'
  return 'cool'
}

// 显示详情通知
const showDetailNotification = (message, type = 'info') => {
  // 创建通知元素
  const notification = document.createElement('div')
  notification.className = `detail-notification ${type}`
  notification.textContent = message
  
  // 添加到页面
  document.body.appendChild(notification)
  
  // 显示动画
  setTimeout(() => {
    notification.classList.add('show')
  }, 100)
  
  // 自动隐藏
  setTimeout(() => {
    notification.classList.remove('show')
    setTimeout(() => {
      if (document.body.contains(notification)) {
        document.body.removeChild(notification)
      }
    }, 300)
  }, 3000)
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
    map.value.setCenter([newCenter.lng, newCenter.lat])
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
  window.searchNearbyPOI = async () => {
    if (currentCoords.value) {
      const lnglat = new window.AMap.LngLat(currentCoords.value.lng, currentCoords.value.lat)
      
      // 搜索附近商圈（带缓存）
      await searchNearbyBusinessAreasWithCache(lnglat)
      
      // 搜索附近POI
      await searchNearbyPois(lnglat)
    }
  }
  
  window.searchNearbyBusinessAreas = () => {
    if (currentCoords.value) {
      const lnglat = new window.AMap.LngLat(currentCoords.value.lng, currentCoords.value.lat)
      searchNearbyBusinessAreasWithCache(lnglat)
    }
  }
})

onUnmounted(() => {
  try {
    if (map.value) {
      map.value.off('click', handleMapClick)
      map.value.off('moveend', handleMapMoveEnd)
      map.value.off('zoomend', handleZoomEnd)
    }
  } catch {}
  
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler)
    resizeHandler = null
  }
  
  // 清理全局函数
  delete window.searchNearbyPOI
  delete window.searchNearbyBusinessAreas
})
</script>

<style scoped>
.amap-container {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 16px;
  overflow: hidden;
  background: #1a1a1a;
}

/* 加载状态 */
.map-loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #1f2937;
  z-index: 1000;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #374151;
  border-top: 4px solid #60a5fa;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

.loading-text {
  color: #d1d5db;
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
  align-items: flex-start;
  background: rgba(31, 41, 55, 0.95);
  backdrop-filter: blur(10px);
  padding: 12px 16px;
  border-radius: 12px;
  z-index: 1000;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  flex-wrap: wrap;
  border: 1px solid rgba(75, 85, 99, 0.3);
}

.city-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #e5e7eb;
  white-space: nowrap;
}

.city-selector label {
  font-weight: 500;
  color: #f3f4f6;
}

.city-changing-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: 12px;
  padding: 4px 8px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 6px;
  border: 1px solid rgba(59, 130, 246, 0.3);
  font-size: 12px;
  color: #60a5fa;
}

.city-loading-spinner {
  width: 12px;
  height: 12px;
  border: 2px solid rgba(96, 165, 250, 0.3);
  border-top: 2px solid #60a5fa;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.search-box {
  display: flex;
  gap: 8px;
  flex: 1;
  min-width: 300px;
}

.modern-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #4b5563;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
  background: #374151;
  color: #f9fafb;
}

.modern-input:focus {
  border-color: #60a5fa;
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.1);
}

.modern-input::placeholder {
  color: #9ca3af;
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
  background: #3b82f6;
  color: white;
}

.modern-btn.primary:hover {
  background: #2563eb;
}

.modern-btn.outline {
  background: #374151;
  color: #d1d5db;
  border: 1px solid #4b5563;
}

.modern-btn.outline:hover {
  background: #4b5563;
  color: #f3f4f6;
}

.modern-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.search-config {
  display: flex;
  gap: 16px;
  align-items: center;
}

.config-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #e5e7eb;
  white-space: nowrap;
}

.modern-select {
  padding: 6px 10px;
  border: 1px solid #4b5563;
  border-radius: 6px;
  background: #374151;
  color: #f9fafb;
  font-size: 13px;
  outline: none;
  min-width: 80px;
}

.map-tools {
  display: flex;
  gap: 8px;
}

.tool-btn {
  padding: 8px;
  min-width: auto;
}

.cache-status-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 8px;
  color: #10b981;
  font-size: 12px;
  font-weight: 500;
  cursor: help;
}

.cache-count {
  background: rgba(16, 185, 129, 0.2);
  padding: 2px 6px;
  border-radius: 4px;
  min-width: 16px;
  text-align: center;
}

/* 地图容器 */
.amap {
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
  background: rgba(31, 41, 55, 0.95);
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  color: #d1d5db;
  z-index: 1000;
  display: flex;
  gap: 16px;
  border: 1px solid rgba(75, 85, 99, 0.3);
}

/* 搜索结果面板 */
.search-results-panel {
  position: absolute;
  top: 400px;
  right: 15px;
  width: 320px;
  max-height: 400px;
  background: rgba(31, 41, 55, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 16px;
  z-index: 1000;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  border: 1px solid rgba(75, 85, 99, 0.3);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #4b5563;
}

.panel-header h4 {
  margin: 0;
  font-size: 16px;
  color: #f3f4f6;
}

.pagination {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.page-btn {
  padding: 4px 8px;
  font-size: 12px;
}

.page-info {
  color: #d1d5db;
  min-width: 40px;
  text-align: center;
}

.results-list {
  max-height: 400px;
  overflow-y: auto;
}

.result-item {
  padding: 12px;
  border: 1px solid #4b5563;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background: #374151;
}

.result-item:hover {
  background: #4b5563;
  border-color: #60a5fa;
}

.result-item.active {
  background: #1e3a8a;
  border-color: #60a5fa;
}

.result-name {
  font-weight: 500;
  color: #f3f4f6;
  margin-bottom: 4px;
  font-size: 14px;
}

.result-address {
  color: #d1d5db;
  font-size: 12px;
  margin-bottom: 6px;
  line-height: 1.4;
}

.result-info {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 11px;
}

.result-type {
  background: #4b5563;
  color: #e5e7eb;
  padding: 2px 6px;
  border-radius: 4px;
}

.result-distance {
  color: #10b981;
  font-weight: 500;
}

.result-tel {
  color: #60a5fa;
}

.result-business {
  margin-top: 4px;
  font-size: 11px;
  color: #a78bfa;
}

/* 附近商圈面板 */
.nearby-areas-panel {
  position: absolute;
  top: 80px;
  right: 15px;
  width: 300px;
  max-height: 300px;
  background: rgba(31, 41, 55, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 16px;
  z-index: 1001;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(75, 85, 99, 0.3);
}

.nearby-areas-panel .panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #4b5563;
}

.nearby-areas-panel h4 {
  margin: 0;
  font-size: 16px;
  color: #f3f4f6;
}

.cache-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.cache-indicator span {
  font-weight: 500;
}

.areas-list {
  max-height: 220px;
  overflow-y: auto;
}

.area-item {
  padding: 10px;
  border: 1px solid #4b5563;
  border-radius: 6px;
  margin-bottom: 6px;
  cursor: pointer;
  transition: all 0.2s;
  background: #374151;
}

.area-item:hover {
  background: #4b5563;
  border-color: #60a5fa;
}

.area-item.active {
  background: #1e3a8a;
  border-color: #60a5fa;
}

.area-name {
  font-weight: 500;
  color: #f3f4f6;
  margin-bottom: 4px;
  font-size: 13px;
}

.area-info {
  display: flex;
  gap: 8px;
  font-size: 11px;
}

.area-distance {
  color: #d1d5db;
}

.area-type {
  color: #d1d5db;
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

/* 详情面板 */
.details-panel {
  position: absolute;
  bottom: 15px;
  right: 15px;
  width: 280px;
  background: rgba(31, 41, 55, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 20px;
  z-index: 1000;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(75, 85, 99, 0.3);
}

.details-panel h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #f3f4f6;
}

.detail-content {
  margin-bottom: 16px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
  line-height: 1.4;
}

.detail-item .label {
  color: #d1d5db;
  flex-shrink: 0;
  margin-right: 8px;
}

.detail-item .value {
  color: #f3f4f6;
  font-weight: 500;
  text-align: right;
  word-break: break-all;
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
@media (max-width: 1200px) {
  .search-results-panel {
    width: 280px;
  }
  
  .search-box {
    min-width: 250px;
  }
}

@media (max-width: 1024px) {
  .map-controls {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .search-box {
    min-width: auto;
  }
  
  .search-config {
    flex-wrap: wrap;
    gap: 12px;
  }
  
  .search-results-panel {
    width: 250px;
  }
  
  .nearby-areas-panel {
    width: 250px;
    top: 80px;
  }
  
  .details-panel {
    width: 250px;
  }
}

@media (max-width: 768px) {
  .map-controls {
    left: 10px;
    right: 10px;
    padding: 12px;
  }
  
  .search-results-panel {
    top: 250px;
    bottom: auto;
    right: 10px;
    left: 10px;
    width: auto;
    max-height: 200px;
  }
  
  .nearby-areas-panel {
    top: 80px;
    right: 10px;
    left: 10px;
    width: auto;
    max-height: 150px;
  }
  
  .details-panel {
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

/* 详情通知样式 */
.detail-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  z-index: 10000;
  transform: translateX(100%);
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
}

.detail-notification.show {
  transform: translateX(0);
}

.detail-notification.success {
  background: rgba(16, 185, 129, 0.9);
  border: 1px solid #10b981;
}

.detail-notification.error {
  background: rgba(239, 68, 68, 0.9);
  border: 1px solid #ef4444;
}

.detail-notification.info {
  background: rgba(59, 130, 246, 0.9);
  border: 1px solid #3b82f6;
}
</style>
